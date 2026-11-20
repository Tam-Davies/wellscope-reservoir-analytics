from pathlib import Path
import lasio
import pandas as pd
import numpy as np

DATA_DIR = Path("data/project_a/raw")


def load_las_file(file_path):
    """Load a LAS file and standardize its depth column."""
    las = lasio.read(file_path)
    df = las.df().reset_index()

    df.rename(columns={df.columns[0]: "DEPTH"}, inplace=True)

    duplicate_depth_columns = [
        col for col in df.columns if col.startswith("DEPT:")
    ]

    df.drop(
        columns=duplicate_depth_columns,
        inplace=True,
        errors="ignore"
    )

    return df


def load_all_wells():
    """Load all LAS files from the Project A raw data directory."""
    wells = {}

    for file_path in DATA_DIR.glob("*.las"):
        well_name = file_path.stem

        try:
            wells[well_name] = load_las_file(file_path)
            print(f"Loaded {well_name}: {wells[well_name].shape}")

        except Exception as error:
            print(f"Failed to load {well_name}: {error}")

    return wells


def process_well_data(df):
    """Clean and standardize well log data."""
    processed = df.copy()

    processed.replace([np.inf, -np.inf], np.nan, inplace=True)
    processed.dropna(subset=["DEPTH"], inplace=True)
    processed.sort_values("DEPTH", inplace=True)
    processed.drop_duplicates(
        subset=["DEPTH"],
        keep="first",
        inplace=True
    )
    processed.reset_index(drop=True, inplace=True)

    return processed


def process_all_wells(save=True):
    """Process all raw wells and optionally save processed CSV files."""
    wells = load_all_wells()
    processed_wells = {}

    output_dir = Path("data/project_a/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    for well_name, df in wells.items():
        processed = process_well_data(df)
        processed_wells[well_name] = processed

        if save:
            output_path = output_dir / f"{well_name}_processed.csv"
            processed.to_csv(output_path, index=False)
            print(f"Saved {well_name}: {output_path}")

    return processed_wells


def load_processed_wells():
    """Load processed well data from CSV files."""
    processed_dir = Path("data/project_a/processed")
    wells = {}

    for file_path in processed_dir.glob("*_processed.csv"):
        well_name = file_path.stem.replace("_processed", "")
        wells[well_name] = pd.read_csv(file_path)

    return wells


def get_well_summary():
    """Generate a summary of processed well data."""
    wells = load_processed_wells()
    summaries = []

    for well_name, df in wells.items():
        curves = [col for col in df.columns if col != "DEPTH"]

        summaries.append({
            "Well": well_name,
            "Samples": len(df),
            "Depth_Start_ft": df["DEPTH"].min(),
            "Depth_End_ft": df["DEPTH"].max(),
            "Available_Curves": ", ".join(curves),
            "Curve_Count": len(curves),
            "Missing_Percent": round(
                df[curves].isna().mean().mean() * 100, 2
            ) if curves else 0
        })

    return pd.DataFrame(summaries)