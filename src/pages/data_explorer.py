
from dash import html, dcc
import plotly.graph_objects as go


def create_data_explorer_page():

    wells = ["W-2", "W-3", "W-5", "W-6", "W-7", "W-11", "W-22"]
    curves = ["GR", "RHOB", "NPHI", "ILD", "DT"]

    coverage = [
        [100, 59, 58, 59, 59],
        [100, 52, 52, 61, 61],
        [100, 83, 84, 83, 83],
        [100, 92, 91, 97, 97],
        [99,  0, 100, 0, 13],
        [100, 95, 95, 93, 0],
        [99, 98,  0,  0,  0],
    ]

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

    return html.Div([
        # Header
        html.Div([
            html.H1("Data Explorer"),
            html.P(
                "Explore well datasets, log availability, "
                "and data quality."
            ),
        ], className="page-header"),

        # Summary
        html.Div([
            html.Div([
                html.P("Wells"),
                html.H2("7"),
                html.Small("Available in study"),
            ], className="metric-card"),

            html.Div([
                html.P("Log Curves"),
                html.H2("5"),
                html.Small("Curve types reviewed"),
            ], className="metric-card"),

            html.Div([
                html.P("GR Coverage"),
                html.H2("~100%"),
                html.Small("Available across all wells"),
            ], className="metric-card"),

            html.Div([
                html.P("Data Quality"),
                html.H2("Variable"),
                html.Small("Curve availability differs by well"),
            ], className="metric-card"),
        ], className="metrics-grid"),

        # Coverage heatmap
        html.Div([
            dcc.Graph(
                figure=fig,
                config={"displayModeBar": True}
            ),
        ], className="panel"),

        # Coverage table
        html.Div([
            html.H3("Curve Coverage Table", className="section-title"),

            html.Table([
                html.Thead(
                    html.Tr([
                        html.Th("Well"),
                        *[html.Th(curve) for curve in curves]
                    ])
                ),
                html.Tbody(table_rows),
            ], className="data-table"),

        ], className="panel"),

        # Data quality notes
        html.Div([
            html.H3("Data Quality Notes", className="section-title"),
            html.P(
                "Gamma Ray coverage is nearly complete across the dataset. "
                "Other curves have varying availability."
            ),
            html.P(
                "W-7 has no RHOB or ILD coverage, while W-22 has no NPHI, "
                "ILD, or DT coverage. These limitations affect downstream "
                "petrophysical evaluation and imputation."
            ),
        ], className="panel"),
    ])
