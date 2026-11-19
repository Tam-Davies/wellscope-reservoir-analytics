from dash import html
from dash import dcc


def create_sidebar():
    return html.Div(
        className="sidebar",
        children=[
            html.Div(
                className="sidebar-brand",
                children=[
                    html.Div("W", className="brand-icon"),
                    html.Div([
                        html.H2("WellScope"),
                        html.P("Reservoir Intelligence")
                    ])
                ]
            ),

            html.Hr(),

            html.P("WORKSPACE", className="nav-label"),

            html.Div([
                dcc.Link(
                    [html.Span("▦", className="nav-icon"), " Overview"],
                    href="/",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.Span("◉", className="nav-icon"), " Reservoir Characterization"],
                    href="/project-a",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.Span("⌁", className="nav-icon"), " Log Imputation"],
                    href="/project-b",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.Span("⇄", className="nav-icon"), " Well Correlation"],
                    href="/correlation",
                    className="nav-link"
                ),
                dcc.Link(
                    [html.Span("▤", className="nav-icon"), " Data Explorer"],
                    href="/data-explorer",
                    className="nav-link"
                ),
            ], className="sidebar-navigation"),

            html.Div(
                className="sidebar-footer",
                children=[
                    html.Div("INTERACTIVE ANALYTICS", className="footer-label"),
                    html.Div("WellScope v1.0", className="footer-version")
                ]
            )
        ]
    )