
from dash import html, dcc
import plotly.graph_objects as go

from src.components.cards import create_kpi_card


def create_overview_page():

    # Net pay values from Project A
    wells = ["W-2", "W-3", "W-5", "W-6", "W-11"]
    net_pay = [675.5, 907.0, 1285.0, 785.0, 571.5]

    net_pay_fig = go.Figure(
        go.Bar(
            x=wells,
            y=net_pay,
            text=[f"{value:,.1f} ft" for value in net_pay],
            textposition="outside",
            marker=dict(color="#2563eb"),
        )
    )

    net_pay_fig.update_layout(
        title="Net Pay Comparison Across Evaluated Wells",
        xaxis_title="Well",
        yaxis_title="Net Pay (ft)",
        template="plotly_white",
        height=400,
        margin=dict(l=40, r=20, t=60, b=40),
        showlegend=False,
    )

    return html.Div(
        children=[
            # Page header
            html.Div(
                className="page-header",
                children=[
                    html.H1("Field Overview"),
                    html.P(
                        "Reservoir characterization summary and field-wide analytics"
                    ),
                ],
            ),

            # KPI Cards
            html.Div(
                className="kpi-grid",
                children=[
                    create_kpi_card(
                        "Wells Analyzed",
                        "7",
                        "Wells included in the study",
                        "◉",
                    ),
                    create_kpi_card(
                        "Evaluable Wells",
                        "5 / 7",
                        "Net pay successfully evaluated",
                        "⌁",
                    ),
                    create_kpi_card(
                        "Total Net Pay",
                        "4,224 ft",
                        "Across five evaluable wells",
                        "▤",
                    ),
                    create_kpi_card(
                        "Electrofacies",
                        "4",
                        "K-Means facies clusters",
                        "◈",
                    ),
                ],
            ),

            # Net pay chart
            html.Div(
                className="panel",
                children=[
                    dcc.Graph(
                        figure=net_pay_fig,
                        config={"displayModeBar": True},
                    ),
                ],
            ),

            # Field highlight
            html.Div(
                className="panel",
                children=[
                    html.H3("Field Highlight", className="section-title"),
                    html.P(
                        "W-5 recorded the highest evaluated net pay "
                        "(1,285 ft), followed by W-3 (907 ft). "
                        "W-7 and W-22 were not evaluable due to "
                        "missing required log curves; their net pay "
                        "should not be interpreted as zero."
                    ),
                ],
            ),
        ]
    )
