import plotly.graph_objects as go
from dash import html

from src.project_a.data_loader import load_processed_wells

wells_data = load_processed_wells()


def get_coverage_status(value, curve_available=True):
    if not curve_available or value == 0:
        return "Unavailable"
    elif value >= 90:
        return "High"
    elif value >= 70:
        return "Moderate"
    return "Low"


def update_data_explorer(selected_wells, selected_curves):

    selected_wells = selected_wells or []
    selected_curves = selected_curves or []

    coverage = []

    for well in selected_wells:
        df = wells_data[well]
        row = []

        for curve in selected_curves:
            if curve in df.columns:
                percent = round(df[curve].notna().mean() * 100, 1)
            else:
                percent = 0.0

            row.append(percent)

        coverage.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=coverage,
            x=selected_curves,
            y=selected_wells,
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

    table = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Well"),
                        *[
                            html.Th(
                                html.Div(
                                    [
                                        html.Div(curve),
                                        html.Div(
                                            "Coverage",
                                            style={
                                                "fontSize": "12px",
                                                "color": "#6b7280",
                                            },
                                        ),
                                    ]
                                )
                            )
                            for curve in selected_curves
                        ],
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(well),
                            *[
                                html.Td(
                                    html.Div(
                                        [
                                            html.Div(f"{value}%"),
                                            html.Div(
                                                get_coverage_status(
                                                    value,
                                                    curve in wells_data[well].columns,
                                                ),
                                                style={
                                                    "fontSize": "12px",
                                                    "fontWeight": "600",
                                                    "color": (
                                                        "#16a34a"
                                                        if value >= 90
                                                        else "#d97706"
                                                        if value >= 70
                                                        else "#dc2626"
                                                        if value > 0
                                                        else "#6b7280"
                                                    ),
                                                },
                                            ),
                                        ]
                                    )
                                )
                                for curve, value in zip(
                                    selected_curves, coverage[i]
                                )
                            ],
                        ]
                    )
                    for i, well in enumerate(selected_wells)
                ]
            ),
        ],
        className="data-table",
    )

    return fig, table