from dash import Dash, html, dcc, Input, Output

from src.components.sidebar import create_sidebar
from src.components.navbar import create_navbar
from src.pages.overview import create_overview_page

from src.pages.project_a import create_project_a_page
from src.pages.project_b import create_project_b_page
from src.pages.well_correlation import create_well_correlation_page
from src.pages.data_explorer import create_data_explorer_page

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
                className="page-content"
            )
        ]
    )
])


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):

    if pathname == "/" or pathname == "/overview":
        return create_overview_page()

    elif pathname == "/project-a":
        return create_project_a_page()

    elif pathname == "/project-b":
        return create_project_b_page()
    
    elif pathname == "/correlation":
        return create_well_correlation_page()
    elif pathname == "/data-explorer":
        return create_data_explorer_page()

    return html.Div(
        className="panel",
        children=[
            html.H2("Page Under Development"),
            html.P(f"Route: {pathname}")
        ]
    )


if __name__ == "__main__":
    app.run(debug=True)
