from pathlib import Path
import lasio
import pandas as pd

DATA_DIR = Path("data/project_a/raw")


def load_las_file(file_path):
    """Load a LAS file and standardize its depth column."""
    las = lasio.read(file_path)

    # LAS depth index becomes our standard DEPTH column
    df = las.df().reset_index()

    # Standardize the depth column name
    df.rename(columns={df.columns[0]: "DEPTH"}, inplace=True)

    # Remove redundant depth curves
    duplicate_depth_columns = [
        col for col in df.columns
        if col.startswith("DEPT:")
    ]

    df.drop(columns=duplicate_depth_columns, inplace=True, errors="ignore")

    return df


def load_all_wells():
    """Load all LAS files from the Project A raw-data directory."""
    wells = {}

    for file_path in DATA_DIR.glob("*.las"):
        well_name = file_path.stem

        try:
            wells[well_name] = load_las_file(file_path)
            print(f"Loaded {well_name}: {wells[well_name].shape}")

        except Exception as error:
            print(f"Failed to load {well_name}: {error}")

    return wells