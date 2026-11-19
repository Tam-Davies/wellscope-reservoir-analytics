
from dash import html, dcc
import plotly.graph_objects as go

from src.components.cards import create_kpi_card


def create_project_a_page():

    wells = ["W-2", "W-3", "W-5", "W-6", "W-11"]
    net_pay = [675.5, 907.0, 1285.0, 785.0, 571.5]
    ntg = [0.15, 0.21, 0.25, 0.16, 0.16]
    phie = [0.259, 0.272, 0.281, 0.296, 0.288]

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=wells,
            y=net_pay,
            name="Net Pay",
            marker_color="#2563eb",
        )
    )

    fig.update_layout(
        title="Net Pay by Well",
        xaxis_title="Well",
        yaxis_title="Net Pay (ft)",
        template="plotly_white",
        height=380,
    )

    table_rows = []

    for i, well in enumerate(wells):
        table_rows.append(
            html.Tr([
                html.Td(well),
                html.Td(f"{net_pay[i]:,.1f} ft"),
                html.Td(f"{ntg[i]:.2f}"),
                html.Td(f"{phie[i]:.3f}"),
            ])
        )

    return html.Div([
        html.Div([
            html.H1("Reservoir Characterization"),
            html.P(
                "Petrophysical evaluation, electrofacies classification "
                "and reservoir quality assessment."
            ),
        ], className="page-header"),

        html.Div([
            create_kpi_card("Wells in Study", "7", "Field dataset", "◉"),
            create_kpi_card("Evaluable Wells", "5", "Net pay evaluated", "⌁"),
            create_kpi_card("Electrofacies", "4", "K-Means clusters", "◈"),
            create_kpi_card("Best Net Pay", "1,285 ft", "W-5", "▤"),
        ], className="kpi-grid"),

        html.Div([
            dcc.Graph(figure=fig)
        ], className="panel"),

        html.Div([
            html.H3("Well Evaluation Summary", className="section-title"),
            html.Table([
                html.Thead(html.Tr([
                    html.Th("Well"),
                    html.Th("Net Pay"),
                    html.Th("NTG"),
                    html.Th("PHIE"),
                ])),
                html.Tbody(table_rows)
            ], className="data-table")
        ], className="panel"),

        html.Div([
            html.H3("Evaluation Notes", className="section-title"),
            html.P(
                "W-5 recorded the highest evaluated net pay. W-6 had the "
                "highest reported effective porosity among these wells. "
                "W-7 and W-22 remain unevaluable for net pay because of "
                "required curve availability limitations and are excluded "
                "from this table."
            ),
        ], className="panel"),
    ])
