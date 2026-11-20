import pandas as pd
from dash import html, dcc
import plotly.graph_objects as go

from src.project_a.data_loader import load_processed_wells


def create_data_explorer_page():

    wells_data = load_processed_wells()

    wells = sorted(wells_data.keys())
    curves = ["GR", "RHOB", "NPHI", "ILD", "DT"]

    coverage = []

    for well, df in wells_data.items():
        row = {"Well": well}

        for curve in curves:
            if curve in df.columns:
                row[curve] = round(df[curve].notna().mean() * 100, 1)
            else:
                row[curve] = 0.0

        coverage.append(row)

    coverage_df = pd.DataFrame(coverage)

    total_samples = sum(len(df) for df in wells_data.values())

    avg_gr_coverage = round(
        coverage_df["GR"].mean(), 1
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=coverage_df[curves].values,
            x=curves,
            y=coverage_df["Well"],
            colorscale=[
                [0.0, "#fee2e2"],
                [0.5, "#fef3c7"],
                [1.0, "#2563eb"],
            ],
            zmin=0,
            zmax=100,
            text=[
                [f"{value}%" for value in row]
                for row in coverage_df[curves].values
            ],
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

    initial_table = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Well"),
                        *[html.Th(curve) for curve in curves],
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["Well"]),
                            *[
                                html.Td(f"{row[curve]}%")
                                for curve in curves
                            ],
                        ]
                    )
                    for _, row in coverage_df.iterrows()
                ]
            ),
        ],
        className="data-table",
    )

    return html.Div(
        [
            html.H1("Data Explorer"),
            html.P(
                "Explore well log data quality, curve coverage, "
                "and data availability across wells."
            ),

            # KPI Cards
            html.Div(
                className="kpi-grid",
                children=[
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.H4("Total Wells"),
                            html.H2(len(wells)),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.H4("Log Curves"),
                            html.H2(len(curves)),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.H4("Average GR Coverage"),
                            html.H2(f"{avg_gr_coverage}%"),
                        ],
                    ),
                    html.Div(
                        className="kpi-card",
                        children=[
                            html.H4("Total Samples"),
                            html.H2(f"{total_samples:,}"),
                        ],
                    ),
                ],
            ),

            # Filters
            html.Div(
                className="panel",
                children=[
                    html.H3("Filters"),

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

                    html.Br(),

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
                ],
            ),

            # Heatmap
            html.Div(
                className="panel",
                children=[
                    dcc.Graph(
                        id="data-explorer-heatmap",
                        figure=fig,
                    ),
                ],
            ),

            # Coverage Table
            html.Div(
                className="panel",
                children=[
                    html.H3("Curve Coverage Table"),
                    html.Div(
                        id="data-explorer-table",
                        children=initial_table,
                    ),
                ],
            ),

            # Data quality notes
            html.Div(
                className="panel",
                children=[
                    html.H3("Data Quality Notes"),
                    html.Ul(
                        [
                            html.Li(
                                "Curve availability varies significantly "
                                "between wells."
                            ),
                            html.Li(
                                "Missing curves are treated as unavailable "
                                "data, not zero-valued measurements."
                            ),
                            html.Li(
                                "W-7 and W-22 have significant curve "
                                "availability limitations."
                            ),
                            html.Li(
                                "Coverage percentages are calculated from "
                                "the processed well data."
                            ),
                        ]
                    ),
                ],
            ),
        ]
    )