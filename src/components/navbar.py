from dash import html


def create_navbar():
    return html.Div(
        className="topbar",
        children=[
            html.Div(
                className="topbar-left",
                children=[
                    html.Div("Reservoir Analytics Platform", className="topbar-title"),
                    html.Div("Interactive subsurface intelligence", className="topbar-subtitle"),
                ]
            ),

            html.Div(
                className="topbar-right",
                children=[
                    html.Div("●", className="status-indicator"),
                    html.Span("System Ready", className="status-text"),
                ]
            )
        ]
    )