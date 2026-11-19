from dash import html, dcc
import plotly.graph_objects as go

from src.project_a.data_loader import load_processed_wells


def create_data_explorer_page():

    wells_data = load_processed_wells()

    wells = sorted(wells_data.keys())
    curves = ["GR", "RHOB", "NPHI", "ILD", "DT"]

    # Calculate curve coverage
    coverage = []

    for well in wells:
        df = wells_data[well]
        row = []

        for curve in curves:
            if curve in df.columns:
                percent = round(df[curve].notna().mean() * 100, 1)
            else:
                percent = 0.0

            row.append(percent)

        coverage.append(row)

    gr_coverage = round(
        sum(row[curves.index("GR")] for row in coverage) / len(wells),
        1
    )

    total_samples = sum(len(df) for df in wells_data.values())

    # Initial heatmap
    fig = go.Figure(
        data=go.Heatmap(
            z=coverage,
            x=curves,
            y=wells,
            colorscale=[
                [0.0, "#fee2e2"],
                [0.5, "#fef3c7"],
                [1.0, "#2563eb"],
            ],
            zmin=0,
            zmax=100,
            text=[[f"{v}%" for v in row] for row in coverage],
            texttemplate="%{text}",
            colorbar=dict(title="Coverage (%)"),
        )
    )

    fig.update_layout(
        title="Well Log Curve Coverage",
        xaxis_title="Log Curve",
        yaxis_title="Well",
        template="plotly_white",
        height=450,
    )

    # Initial table
    table_rows = []

    for i, well in enumerate(wells):
        table_rows.append(
            html.Tr([
                html.Td(well),
                *[
                    html.Td(f"{value}%")
                    for value in coverage[i]
                ]
            ])
        )

    # Quality notes
    quality_notes = []

    for well in wells:
        df = wells_data[well]
        missing_curves = []

        for curve in curves:
            if curve not in df.columns:
                missing_curves.append(f"{curve} (not available)")

            elif df[curve].isna().mean() > 0.5:
                missing_curves.append(
                    f"{curve} ({df[curve].isna().mean() * 100:.1f}% missing)"
                )

        if missing_curves:
            quality_notes.append(
                html.P(f"{well}: " + ", ".join(missing_curves))
            )

    return html.Div([

        # Header
        html.Div([
            html.H1("Data Explorer"),
            html.P(
                "Explore well datasets, log availability, "
                "and data quality."
            ),
        ], className="page-header"),

        # Summary cards
        html.Div([

            html.Div([
                html.P("Wells"),
                html.H2(str(len(wells))),
                html.Small("Available in study"),
            ], className="metric-card"),

            html.Div([
                html.P("Log Curves"),
                html.H2(str(len(curves))),
                html.Small("Curve types reviewed"),
            ], className="metric-card"),

            html.Div([
                html.P("GR Coverage"),
                html.H2(f"{gr_coverage}%"),
                html.Small("Average across wells"),
            ], className="metric-card"),

            html.Div([
                html.P("Total Samples"),
                html.H2(f"{total_samples:,}"),
                html.Small("Processed log records"),
            ], className="metric-card"),

        ], className="metrics-grid"),

        # Filters
        html.Div([

            html.Div([
                html.Label("Select Wells"),
                dcc.Dropdown(
                    id="well-filter",
                    options=[
                        {"label": well, "value": well}
                        for well in wells
                    ],
                    value=wells,
                    multi=True,
                    placeholder="Select wells",
                ),
            ], className="filter-item"),

            html.Div([
                html.Label("Select Curves"),
                dcc.Dropdown(
                    id="curve-filter",
                    options=[
                        {"label": curve, "value": curve}
                        for curve in curves
                    ],
                    value=curves,
                    multi=True,
                    placeholder="Select curves",
                ),
            ], className="filter-item"),

        ], className="filters-container"),

        # Heatmap — callback target
        html.Div([
            dcc.Graph(
                id="data-explorer-heatmap",
                figure=fig,
                config={"displayModeBar": True},
            ),
        ], className="panel"),

        # Table — callback target
        html.Div([

            html.H3(
                "Curve Coverage Table",
                className="section-title"
            ),

            html.Div(
                html.Table([
                    html.Thead(
                        html.Tr([
                            html.Th("Well"),
                            *[html.Th(curve) for curve in curves]
                        ])
                    ),
                    html.Tbody(table_rows),
                ], className="data-table"),
                id="data-explorer-table",
            ),

        ], className="panel"),

        # Quality notes
        html.Div([

            html.H3(
                "Data Quality Notes",
                className="section-title"
            ),

            html.P(
                f"Coverage is calculated directly from the processed "
                f"LAS data across {total_samples:,} samples. "
                "Missing measurements are not treated as zero."
            ),

            *quality_notes,

        ], className="panel"),

    ])