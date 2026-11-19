from dash import html, dcc


def create_well_filter(wells):
    return html.Div(
        className="filter-group",
        children=[
            html.Label("Select Wells"),
            dcc.Dropdown(
                options=[{"label": well, "value": well} for well in wells],
                value=wells,
                multi=True,
                placeholder="Select wells",
                className="filter-dropdown"
            )
        ]
    )


def create_depth_filter(min_depth, max_depth):
    return html.Div(
        className="filter-group",
        children=[
            html.Label("Depth Range (ft)"),
            dcc.RangeSlider(
                min=min_depth,
                max=max_depth,
                value=[min_depth, max_depth],
                step=10,
                tooltip={"placement": "bottom", "always_visible": False}
            )
        ]
    )