
from dash import Dash, html, dcc

from src.components.sidebar import create_sidebar
from src.components.navbar import create_navbar

app = Dash(
    __name__,
    title="WellScope | Reservoir Analytics",
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),

    create_sidebar(),

    html.Div(
        className="main-content",
        children=[
            create_navbar(),

            html.Div(
                id="page-content",
                className="page-content",
                children=[
                    html.H2("Welcome to WellScope"),
                    html.P(
                        "Interactive Well Log Analytics & Reservoir Characterization Platform"
                    ),
                    html.Div(
                        "Dashboard pages will be loaded here.",
                        className="panel"
                    )
                ]
            )
        ]
    )
])


if __name__ == "__main__":
    app.run(debug=True)
