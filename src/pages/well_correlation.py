
from dash import html, dcc
import plotly.graph_objects as go


def create_well_correlation_page():

    empty_fig = go.Figure()

    empty_fig.update_layout(
        title="Multi-Well Gamma Ray Correlation",
        xaxis_title="Gamma Ray (API)",
        yaxis_title="Measured Depth (ft)",
        yaxis=dict(autorange="reversed"),
        template="plotly_white",
        height=700,
    )

    return html.Div([
        # Header
        html.Div([
            html.H1("Well Correlation"),
            html.P(
                "Compare stratigraphic patterns and gamma ray responses "
                "across multiple wells."
            ),
        ], className="page-header"),

        # Well selection
        html.Div([
            html.H3("Correlation Configuration", className="section-title"),

            html.Label("Select Wells"),

            dcc.Dropdown(
                id="correlation-wells",
                options=[
                    {"label": well, "value": well}
                    for well in ["W-2", "W-3", "W-5", "W-6", "W-7", "W-11", "W-22"]
                ],
                value=["W-2", "W-3", "W-5"],
                multi=True,
                placeholder="Select wells to compare",
            ),

            html.Div([
                html.Label("Log Curve"),
                dcc.Dropdown(
                    id="correlation-curve",
                    options=[
                        {"label": "Gamma Ray (GR)", "value": "GR"},
                    ],
                    value="GR",
                    clearable=False,
                ),
            ], style={"marginTop": "18px"}),
        ], className="panel"),

        # Correlation visualization
        html.Div([
            dcc.Graph(
                id="correlation-plot",
                figure=empty_fig,
                config={"displayModeBar": True},
            ),
        ], className="panel"),

        # Interpretation panel
        html.Div([
            html.H3("Correlation Notes", className="section-title"),
            html.P(
                "The correlation workflow will use measured depth and "
                "available log curves to support qualitative stratigraphic "
                "comparison. Structural correlation and horizon interpretation "
                "will require interpreted formation tops."
            ),
        ], className="panel"),
    ])
