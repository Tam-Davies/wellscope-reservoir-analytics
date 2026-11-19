from dash import html


def create_kpi_card(title, value, subtitle, icon):
    return html.Div(
        className="kpi-card",
        children=[
            html.Div(
                className="kpi-card-header",
                children=[
                    html.Span(title, className="kpi-title"),
                    html.Span(icon, className="kpi-icon"),
                ]
            ),
            html.H2(value, className="kpi-value"),
            html.P(subtitle, className="kpi-subtitle"),
        ]
    )