from dash import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.project_a.data_loader import load_processed_wells


def create_correlation_figure(selected_wells, selected_curve="GR"):
    wells_data = load_processed_wells()
    selected_wells = selected_wells or []

    valid_wells = [
        well for well in selected_wells
        if well in wells_data
        and selected_curve in wells_data[well].columns
        and "DEPTH" in wells_data[well].columns
    ]

    if not valid_wells:
        fig = go.Figure()
        fig.update_layout(
            title="Multi-Well Gamma Ray Correlation",
            xaxis_title=f"{selected_curve} (API)",
            yaxis_title="Measured Depth (ft)",
            template="plotly_white",
            annotations=[{
                "text": "Select wells with DEPTH and the selected log curve available.",
                "xref": "paper", "yref": "paper", "x": 0.5, "y": 0.5,
                "showarrow": False
            }]
        )
        return fig

    fig = make_subplots(
        rows=1, cols=len(valid_wells),
        shared_yaxes=True,
        subplot_titles=valid_wells,
        horizontal_spacing=0.04
    )

    for idx, well_name in enumerate(valid_wells, start=1):
        df = wells_data[well_name].copy()
        df = df[["DEPTH", selected_curve]].dropna()
        df = df.sort_values("DEPTH")

        if df.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=df[selected_curve],
                y=df["DEPTH"],
                mode="lines",
                name=well_name,
                showlegend=False,
                line={"width": 1.2},
                hovertemplate=(
                    f"Well: {well_name}<br>"
                    f"{selected_curve}: %{{x}}<br>"
                    "Depth: %{y:.2f} ft<extra></extra>"
                )
            ),
            row=1, col=idx
        )
        fig.update_xaxes(title_text=f"{selected_curve} (API)", row=1, col=idx)

    fig.update_yaxes(
        title_text="Measured Depth (ft)",
        autorange="reversed",
        showgrid=True
    )
    fig.update_layout(
        title="Multi-Well Gamma Ray Correlation",
        template="plotly_white",
        height=max(700, 250 * len(valid_wells)),
        margin={"l": 70, "r": 30, "t": 90, "b": 50}
    )
    return fig


def register_correlation_callbacks(app):
    @app.callback(
        Output("correlation-plot", "figure"),
        Input("correlation-wells", "value"),
        Input("correlation-curve", "value"),
    )
    def update_correlation_plot(selected_wells, selected_curve):
        return create_correlation_figure(selected_wells, selected_curve)
