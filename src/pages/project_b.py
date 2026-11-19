
from dash import html, dcc


def create_project_b_page():

    return html.Div([
        # Header
        html.Div([
            html.H1("Log Imputation"),
            html.P(
                "Missing-log recovery, model comparison, and blind-well validation."
            ),
        ], className="page-header"),

        # Controls
        html.Div([
            html.H3("Imputation Configuration", className="section-title"),

            html.Div([
                html.Div([
                    html.Label("Target Log"),
                    dcc.Dropdown(
                        id="imputation-target",
                        options=[
                            {"label": "RHOB — Bulk Density", "value": "RHOB"},
                            {"label": "ILD — Deep Resistivity", "value": "ILD"},
                        ],
                        value="RHOB",
                        clearable=False,
                    ),
                ]),

                html.Div([
                    html.Label("Validation Strategy"),
                    dcc.Dropdown(
                        id="imputation-validation",
                        options=[
                            {"label": "Blind-Well Validation", "value": "blind_well"},
                            {"label": "Random Holdout", "value": "random"},
                        ],
                        value="blind_well",
                        clearable=False,
                    ),
                ]),
            ], className="filter-grid"),
        ], className="panel"),

        # Model metrics
        html.Div([
            html.H3("Model Performance", className="section-title"),

            html.Div([
                html.Div([
                    html.P("MAE"),
                    html.H2("--"),
                    html.Small("Mean Absolute Error"),
                ], className="metric-card"),

                html.Div([
                    html.P("RMSE"),
                    html.H2("--"),
                    html.Small("Root Mean Squared Error"),
                ], className="metric-card"),

                html.Div([
                    html.P("R²"),
                    html.H2("--"),
                    html.Small("Coefficient of Determination"),
                ], className="metric-card"),

                html.Div([
                    html.P("Best Model"),
                    html.H2("--"),
                    html.Small("Pending model evaluation"),
                ], className="metric-card"),
            ], className="metrics-grid"),
        ], className="panel"),

        # Model comparison
        html.Div([
            html.H3("Model Comparison", className="section-title"),
            html.P(
                "Classical machine-learning models and neural networks "
                "will be compared under the same validation conditions."
            ),
            dcc.Graph(
                id="imputation-model-comparison",
                figure={
                    "data": [],
                    "layout": {
                        "title": "Model comparison will appear here",
                        "template": "plotly_white",
                        "height": 400,
                    },
                },
            ),
        ], className="panel"),

        # Prediction visualization
        html.Div([
            html.H3("Measured vs Imputed Log", className="section-title"),
            html.P(
                "Select a well and target curve after data and models "
                "are connected to inspect measured and predicted values."
            ),
            dcc.Graph(
                id="imputation-log-plot",
                figure={
                    "data": [],
                    "layout": {
                        "title": "Log reconstruction visualization",
                        "template": "plotly_white",
                        "height": 500,
                    },
                },
            ),
        ], className="panel"),

        # Validation
        html.Div([
            html.H3("Validation Summary", className="section-title"),
            html.Div(
                "Validation results have not yet been loaded.",
                className="validation-placeholder",
            ),
        ], className="panel"),
    ])
