
from dash import html, dcc, Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

from src.project_a.data_loader import load_processed_wells


wells_data = load_processed_wells()

LOG_OPTIONS = ["GR", "ILD", "RHOB", "NPHI", "DT"]

VSH_MODELS = {
    "Larionov Tertiary": "VSH_LARIONOV_TERTIARY",
    "Larionov Older Rocks": "VSH_LARIONOV_OLDER",
    "Clavier": "VSH_CLAVIER",
    "Stieber": "VSH_STIEBER",
}

VSH_COLORS = {
    "Larionov Tertiary": "#2563eb",
    "Larionov Older Rocks": "#dc2626",
    "Clavier": "#16a34a",
    "Stieber": "#9333ea",
}


# =========================================================
# VSH CALCULATIONS
# =========================================================

def calculate_vsh(df):
    """Calculate IGR and multiple Vsh models from Gamma Ray."""

    df = df.copy()

    if "GR" not in df.columns:
        return df

    gr = df["GR"]

    gr_min = gr.quantile(0.05)
    gr_max = gr.quantile(0.95)

    if (
        not np.isfinite(gr_min)
        or not np.isfinite(gr_max)
        or gr_max == gr_min
    ):
        return df

    igr = ((gr - gr_min) / (gr_max - gr_min)).clip(0, 1)

    df["IGR"] = igr

    # Larionov Tertiary rocks
    df["VSH_LARIONOV_TERTIARY"] = (
        0.083 * (2 ** (3.7 * igr) - 1)
    ).clip(0, 1)

    # Larionov Older rocks
    df["VSH_LARIONOV_OLDER"] = (
        0.33 * (2 ** (2 * igr) - 1)
    ).clip(0, 1)

    # Clavier
    clavier_term = 3.38 - (igr + 0.7) ** 2

    df["VSH_CLAVIER"] = (
        1.7 - np.sqrt(clavier_term.clip(lower=0))
    ).clip(0, 1)

    # Stieber
    denominator = (3 - 2 * igr).replace(0, np.nan)

    df["VSH_STIEBER"] = (
        igr / denominator
    ).clip(0, 1)

    return df


def pd_is_invalid(value):
    """Check whether a scalar is invalid."""
    return bool(np.isnan(value))


# =========================================================
# PAGE LAYOUT
# =========================================================

def create_project_a_page():

    wells = sorted(wells_data.keys())
    default_well = wells[0] if wells else None

    available_logs = [
        log
        for log in LOG_OPTIONS
        if any(log in df.columns for df in wells_data.values())
    ]

    default_logs = ["GR"] if "GR" in available_logs else available_logs[:1]

    return html.Div(
        [
            html.H1("Project A — Reservoir Characterization"),

            html.P(
                "Interactive petrophysical log visualization, "
                "Vsh computation and reservoir interval screening."
            ),

            # -------------------------
            # Controls
            # -------------------------
            html.Div(
                className="panel",
                children=[
                    html.Label("Select Well"),

                    dcc.Dropdown(
                        id="project-a-well-select",
                        options=[
                            {"label": well, "value": well}
                            for well in wells
                        ],
                        value=default_well,
                        clearable=False,
                    ),

                    html.Br(),

                    html.Label("Select Log Tracks"),

                    dcc.Dropdown(
                        id="project-a-track-select",
                        options=[
                            {"label": log, "value": log}
                            for log in available_logs
                        ],
                        value=default_logs,
                        multi=True,
                        placeholder="Select logs to display",
                    ),

                    html.Br(),

                    html.Label("Vsh Models for Log Tracks"),

                    dcc.Dropdown(
                        id="project-a-vsh-model-select",
                        options=[
                            {"label": model, "value": model}
                            for model in VSH_MODELS
                        ],
                        value=["Larionov Tertiary"],
                        multi=True,
                        placeholder="Select Vsh models",
                    ),

                    html.Br(),

                    html.Label("Depth Interval (ft) — Optional"),
                    html.Div([
                        dcc.Input(id="project-a-top-depth", type="number", placeholder="Top depth", debounce=True, style={"width": "48%"}),
                        dcc.Input(id="project-a-bottom-depth", type="number", placeholder="Bottom depth", debounce=True, style={"width": "48%", "marginLeft": "2%"}),
                    ], style={"display": "flex", "gap": "8px"}),
                    html.Button("Reset to Full Well", id="project-a-reset-depth", n_clicks=0, style={"marginTop": "10px"}),
                    html.Br(),
                    html.Button("Export Vsh / ML Dataset (CSV)", id="project-a-export-csv", n_clicks=0, style={"marginTop": "12px"}),
                    dcc.Download(id="project-a-export-download"),
                    html.Br(),
                    html.Label("Reservoir Screening Vsh Cutoff"),

                    dcc.Slider(
                        id="project-a-vsh-cutoff",
                        min=0,
                        max=1,
                        step=0.05,
                        value=0.40,
                        marks={
                            0: "0",
                            0.2: "0.2",
                            0.4: "0.4",
                            0.6: "0.6",
                            0.8: "0.8",
                            1: "1.0",
                        },
                    ),
                ],
            ),

            # -------------------------
            # Log track viewer
            # -------------------------
            html.Div(
                className="panel",
                children=[
                    dcc.Graph(
                        id="project-a-log-tracks",
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "responsive": True,
                        },
                    )
                ],
            ),

            # -------------------------
            # Vsh report section
            # -------------------------
            html.H2("Vsh Model Comparison Report"),

            html.P(
                "Compare shale-volume models against the normalized "
                "Gamma Ray Index (IGR)."
            ),

            html.Div(
                className="panel",
                children=[
                    html.Label("Models to Compare"),

                    dcc.Dropdown(
                        id="project-a-report-model-select",
                        options=[
                            {"label": model, "value": model}
                            for model in VSH_MODELS
                        ],
                        value=list(VSH_MODELS.keys()),
                        multi=True,
                        placeholder="Select models to compare",
                    ),

                    dcc.Graph(
                        id="project-a-vsh-report",
                        config={
                            "displayModeBar": True,
                            "scrollZoom": True,
                            "responsive": True,
                        },
                    ),
                ],
            ),

            # -------------------------
            # Electrofacies Analysis
            # -------------------------
            html.H2("Electrofacies Analysis"),
            html.P("Cluster selected petrophysical logs into data-driven electrofacies groups."),
            html.Div(
                className="panel",
                children=[
                    html.Label("Input Logs for Clustering"),
                    dcc.Dropdown(
                        id="project-a-electrofacies-logs",
                        options=[{"label": log, "value": log} for log in available_logs],
                        value=[log for log in ["GR", "RHOB", "NPHI"] if log in available_logs],
                        multi=True,
                        placeholder="Select at least two logs",
                    ),
                    html.Br(),
                    html.Label("Number of Electrofacies"),
                    dcc.Slider(id="project-a-electrofacies-clusters", min=2, max=8, step=1, value=4,
                               marks={i: str(i) for i in range(2, 9)}),
                    dcc.Graph(id="project-a-electrofacies-figure", config={"displayModeBar": True, "responsive": True}),
                ],
            ),
        ]
    )



# =========================================================
# MULTI-TRACK LOG FIGURE
# =========================================================

def create_log_track_figure(
    well,
    selected_logs=None,
    selected_models=None,
    cutoff=0.40,
    top_depth=None,
    bottom_depth=None,
):

    if well not in wells_data:
        return go.Figure()

    df = wells_data[well].copy()
    df = calculate_vsh(df)

    depth = df["DEPTH"]

    if top_depth is not None and bottom_depth is not None:
        top_depth, bottom_depth = sorted([top_depth, bottom_depth])
        df = df.loc[(depth >= top_depth) & (depth <= bottom_depth)].copy()
        depth = df["DEPTH"]
    elif top_depth is not None:
        df = df.loc[depth >= top_depth].copy()
        depth = df["DEPTH"]
    elif bottom_depth is not None:
        df = df.loc[depth <= bottom_depth].copy()
        depth = df["DEPTH"]

    selected_logs = selected_logs or []
    selected_models = selected_models or []

    tracks = []

    # Selected raw logs
    for log in selected_logs:
        if log in df.columns:
            tracks.append(("log", log))

    # Selected calculated Vsh curves
    for model in selected_models:
        if model in VSH_MODELS:
            curve_name = VSH_MODELS[model]

            if curve_name in df.columns:
                tracks.append(("vsh", model))

    if not tracks:
        fig = go.Figure()

        fig.update_layout(
            template="plotly_white",
            title="Select at least one log track or Vsh model",
        )

        return fig

    fig = make_subplots(
        rows=1,
        cols=len(tracks),
        shared_yaxes=True,
        horizontal_spacing=min(0.08, 0.5 / len(tracks)),
        subplot_titles=[name for _, name in tracks],
    )

    for i, (track_type, name) in enumerate(tracks, start=1):

        # -------------------------
        # RAW LOG TRACKS
        # -------------------------
        if track_type == "log":

            curve = df[name]

            x_range = None

            if name == "GR":
                x_range = [0, 150]

            elif name == "RHOB":
                x_range = [1.95, 2.95]

            elif name == "NPHI":
                x_range = [-0.15, 0.60]

            fig.add_trace(
                go.Scatter(
                    x=curve,
                    y=depth,
                    mode="lines",
                    name=name,
                    line=dict(
                        color="#16a34a" if name == "GR" else "#2563eb",
                        width=1,
                    ),
                    connectgaps=False,
                ),
                row=1,
                col=i,
            )

            fig.update_xaxes(
                title_text=name,
                range=x_range,
                showgrid=True,
                gridcolor="lightgray",
                row=1,
                col=i,
            )

        # -------------------------
        # VSH TRACKS
        # -------------------------
        elif track_type == "vsh":

            curve_name = VSH_MODELS[name]
            vsh = df[curve_name]

            # Sand portion: Vsh <= cutoff
            sand_vsh = vsh.where(vsh <= cutoff)

            fig.add_trace(
                go.Scatter(
                    x=sand_vsh,
                    y=depth,
                    mode="lines",
                    name=f"{name} — Low Vsh",
                    line=dict(color="#16a34a", width=1),
                    fill="tozerox",
                    fillcolor="rgba(22,163,74,0.65)",
                    connectgaps=False,
                ),
                row=1,
                col=i,
            )

            # Shale portion: Vsh > cutoff
            shale_vsh = vsh.where(vsh > cutoff)

            fig.add_trace(
                go.Scatter(
                    x=shale_vsh,
                    y=depth,
                    mode="lines",
                    name=f"{name} — High Vsh",
                    line=dict(color="#dc2626", width=1),
                    fill="tozerox",
                    fillcolor="rgba(220,38,38,0.60)",
                    connectgaps=False,
                ),
                row=1,
                col=i,
            )

            # Vsh cutoff line
            fig.add_vline(
                x=cutoff,
                line_dash="dash",
                line_color="#374151",
                line_width=1.5,
                row=1,
                col=i,
            )

            fig.update_xaxes(
                title_text="Vsh",
                range=[0, 1],
                showgrid=True,
                gridcolor="lightgray",
                row=1,
                col=i,
            )

    # -------------------------
    # Shared depth axis
    # -------------------------
    fig.update_yaxes(
        title_text="Depth (ft)",
        autorange="reversed",
        showgrid=True,
        gridcolor="lightgray",
        row=1,
        col=1,
    )

    for i in range(2, len(tracks) + 1):

        fig.update_yaxes(
            showgrid=True,
            gridcolor="lightgray",
            matches="y",
            row=1,
            col=i,
        )

    fig.update_layout(
        height=1100,
        title=f"Well Log Tracks — {well}",
        template="plotly_white",
        showlegend=False,
        margin=dict(l=70, r=30, t=90, b=60),
    )

    return fig


# =========================================================
# CLEAN THEORETICAL VSH MODEL COMPARISON
# =========================================================

def create_vsh_report_figure(well, selected_models=None):

    selected_models = selected_models or []

    # Smooth theoretical IGR domain
    igr = np.linspace(0, 1, 500)

    fig = go.Figure()

    # Linear IGR reference
    fig.add_trace(
        go.Scatter(
            x=igr,
            y=igr,
            mode="lines",
            name="Linear IGR",
            line=dict(
                color="#222222",
                width=2,
                dash="dash",
            ),
        )
    )

    # Larionov Tertiary
    if "Larionov Tertiary" in selected_models:

        vsh = 0.083 * (2 ** (3.7 * igr) - 1)

        fig.add_trace(
            go.Scatter(
                x=igr,
                y=np.clip(vsh, 0, 1),
                mode="lines",
                name="Larionov Tertiary",
                line=dict(
                    color="#2563eb",
                    width=2,
                ),
            )
        )

    # Larionov Older Rocks
    if "Larionov Older Rocks" in selected_models:

        vsh = 0.33 * (2 ** (2 * igr) - 1)

        fig.add_trace(
            go.Scatter(
                x=igr,
                y=np.clip(vsh, 0, 1),
                mode="lines",
                name="Larionov Older Rocks",
                line=dict(
                    color="#dc2626",
                    width=2,
                ),
            )
        )

    # Clavier
    if "Clavier" in selected_models:

        term = 3.38 - (igr + 0.7) ** 2
        vsh = 1.7 - np.sqrt(np.clip(term, 0, None))

        fig.add_trace(
            go.Scatter(
                x=igr,
                y=np.clip(vsh, 0, 1),
                mode="lines",
                name="Clavier",
                line=dict(
                    color="#16a34a",
                    width=2,
                ),
            )
        )

    # Stieber
    if "Stieber" in selected_models:

        denominator = 3 - 2 * igr
        vsh = igr / denominator

        fig.add_trace(
            go.Scatter(
                x=igr,
                y=np.clip(vsh, 0, 1),
                mode="lines",
                name="Stieber",
                line=dict(
                    color="#9333ea",
                    width=2,
                ),
            )
        )

    fig.update_layout(
        title=f"Vsh Model Comparison — {well}",
        template="plotly_white",
        height=650,
        margin=dict(l=70, r=35, t=110, b=80),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            y=1.12,
            x=0,
            font=dict(size=12),
        ),
    )

    fig.update_xaxes(
        title="IGR (Normalized Gamma Ray Index)",
        range=[0, 1],
        dtick=0.1,
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
    )

    fig.update_yaxes(
        title="Vsh (Fraction)",
        range=[0, 1],
        dtick=0.1,
        showgrid=True,
        gridcolor="#E5E7EB",
        zeroline=False,
    )

    return fig


# =========================================================
# EXPORT DATA PREPARATION
# =========================================================

def prepare_vsh_export_data(well, top_depth=None, bottom_depth=None, cutoff=0.40):
    """Prepare a depth-filtered, ML-friendly CSV dataset with calculated Vsh columns."""
    if well not in wells_data:
        return pd.DataFrame()

    df = calculate_vsh(wells_data[well].copy())
    depth = df["DEPTH"]

    if top_depth is not None and bottom_depth is not None:
        top_depth, bottom_depth = sorted([top_depth, bottom_depth])
        df = df.loc[(depth >= top_depth) & (depth <= bottom_depth)].copy()
    elif top_depth is not None:
        df = df.loc[depth >= top_depth].copy()
    elif bottom_depth is not None:
        df = df.loc[depth <= bottom_depth].copy()

    df["WELL"] = well
    df["VSH_SCREENING_CUTOFF"] = cutoff


    for model_name, curve_name in VSH_MODELS.items():
        if curve_name in df.columns:
            df[f"SAND_FLAG_{curve_name}"] = (df[curve_name] <= cutoff).astype("Int64")

    # Keep depth first, well identifier second, then the original and engineered data.
    ordered_cols = ["DEPTH", "WELL"] + [col for col in df.columns if col not in {"DEPTH", "WELL"}]
    return df[ordered_cols].reset_index(drop=True)



# =========================================================
# ELECTROFACIES CLUSTERING
# =========================================================

def prepare_electrofacies_data(well, selected_logs=None, n_clusters=4, top_depth=None, bottom_depth=None):
    """Standardize selected log features and assign KMeans electrofacies labels."""
    if well not in wells_data:
        return pd.DataFrame()
    selected_logs = selected_logs or []
    valid_logs = [log for log in selected_logs if log in wells_data[well].columns]
    if len(valid_logs) < 2:
        return pd.DataFrame()

    df = wells_data[well].copy()
    depth = df["DEPTH"]
    if top_depth is not None and bottom_depth is not None:
        top_depth, bottom_depth = sorted([top_depth, bottom_depth])
        df = df.loc[(depth >= top_depth) & (depth <= bottom_depth)].copy()
    elif top_depth is not None:
        df = df.loc[depth >= top_depth].copy()
    elif bottom_depth is not None:
        df = df.loc[depth <= bottom_depth].copy()

    usable = df.dropna(subset=valid_logs).copy()
    if len(usable) < n_clusters:
        return pd.DataFrame()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(usable[valid_logs])
    model = KMeans(n_clusters=int(n_clusters), random_state=42, n_init=10)
    usable["ELECTROFACIES"] = model.fit_predict(scaled) + 1
    usable["WELL"] = well
    usable["CLUSTER_INPUT_LOGS"] = ", ".join(valid_logs)
    usable["ELECTROFACIES_COUNT"] = int(n_clusters)
    return usable



def create_electrofacies_figure(well, selected_logs=None, n_clusters=4, top_depth=None, bottom_depth=None):
    results = prepare_electrofacies_data(well, selected_logs, n_clusters, top_depth, bottom_depth)
    if results.empty:
        fig = go.Figure()
        fig.update_layout(template="plotly_white", title="Select at least two valid logs and enough samples")
        return fig

    palette = ["#2563eb", "#dc2626", "#16a34a", "#9333ea", "#f59e0b", "#0891b2", "#db2777", "#64748b"]
    results = results.sort_values("DEPTH").reset_index(drop=True)
    depths = results["DEPTH"].to_numpy(dtype=float)
    labels = results["ELECTROFACIES"].to_numpy(dtype=int)
    typical_step = float(np.median(np.diff(depths))) if len(depths) > 1 else 1.0

    # Build depth intervals from neighboring sample midpoints, preserving large data gaps.
    interval_top = np.empty(len(depths), dtype=float)
    interval_bottom = np.empty(len(depths), dtype=float)
    if len(depths) == 1:
        interval_top[0], interval_bottom[0] = depths[0] - typical_step / 2, depths[0] + typical_step / 2
    else:
        mids = (depths[:-1] + depths[1:]) / 2
        interval_top[0] = depths[0] - typical_step / 2
        interval_bottom[-1] = depths[-1] + typical_step / 2
        interval_bottom[:-1] = mids
        interval_top[1:] = mids

    fig = go.Figure()
    valid_hover_logs = [log for log in (selected_logs or []) if log in results.columns]
    for facies in sorted(np.unique(labels)):
        color = palette[(int(facies) - 1) % len(palette)]
        first_segment = True
        for i, label in enumerate(labels):
            if label != facies:
                continue
            # Don't visually bridge a large missing-depth interval.
            gap = interval_bottom[i] - interval_top[i]
            if gap > typical_step * 2.5:
                continue
            fig.add_trace(go.Scatter(
                x=[0.18, 0.82], y=[interval_top[i], interval_bottom[i]],
                mode="lines", line=dict(color=color, width=24),
                name=f"Electrofacies {facies}", legendgroup=f"facies-{facies}",
                showlegend=first_segment, hoverinfo="skip"
            ))
            first_segment = False
        # Add hoverable sample points on the facies strip.
        custom_columns = ["DEPTH"] + valid_hover_logs
        custom = results[custom_columns].copy()
        custom.insert(0, "Electrofacies", labels)
        mask = labels == facies
        hover_cols = [c for c in custom.columns if c != "DEPTH"]
        hover_text = "Facies: %{customdata[0]}<br>Depth: %{y:.2f} ft"
        for j, log in enumerate(valid_hover_logs, start=1):
            hover_text += f"<br>{log}: %{{customdata[{j}]}}"
        fig.add_trace(go.Scatter(
            x=np.full(mask.sum(), 0.5), y=depths[mask], mode="markers",
            marker=dict(size=8, color=color, opacity=0),
            customdata=custom.loc[mask, hover_cols].to_numpy(),
            hovertemplate=hover_text + "<extra></extra>",
            showlegend=False, legendgroup=f"facies-{facies}"
        ))

    fig.update_layout(
        title=f"Electrofacies Log — {well}", template="plotly_white", height=850,
        xaxis_title="Facies Track", yaxis_title="Depth (ft)",
        yaxis=dict(autorange="reversed"), legend=dict(orientation="h"),
        margin=dict(l=70, r=30, t=80, b=60),
        plot_bgcolor="white"
    )
    fig.update_xaxes(range=[0, 1], tickvals=[0.5], ticktext=["Electrofacies"], showgrid=False, zeroline=False)
    return fig


# =========================================================
# CALLBACK REGISTRATION
# =========================================================

def register_project_a_callbacks(app):

    @app.callback(
        Output("project-a-top-depth", "value"),
        Output("project-a-bottom-depth", "value"),
        Input("project-a-reset-depth", "n_clicks"),
        prevent_initial_call=True,
    )
    def reset_depth_interval(n_clicks):
        return None, None



    @app.callback(
        Output("project-a-export-download", "data"),
        Input("project-a-export-csv", "n_clicks"),
        State("project-a-well-select", "value"),
        State("project-a-top-depth", "value"),
        State("project-a-bottom-depth", "value"),
        State("project-a-vsh-cutoff", "value"),
        prevent_initial_call=True,
    )
    def export_project_a_dataset(n_clicks, well, top_depth, bottom_depth, cutoff):
        if not n_clicks or not well:
            return None

        export_df = prepare_vsh_export_data(well, top_depth, bottom_depth, cutoff)
        if export_df.empty:
            return None

        safe_well = str(well).replace("/", "_").replace("\\", "_")
        return dcc.send_data_frame(export_df.to_csv, f"{safe_well}_vsh_ml_dataset.csv", index=False)



    @app.callback(
        Output("project-a-electrofacies-figure", "figure"),
        Input("project-a-well-select", "value"),
        Input("project-a-electrofacies-logs", "value"),
        Input("project-a-electrofacies-clusters", "value"),
        Input("project-a-top-depth", "value"),
        Input("project-a-bottom-depth", "value"),
    )
    def update_electrofacies(well, selected_logs, n_clusters, top_depth, bottom_depth):
        return create_electrofacies_figure(well, selected_logs, n_clusters, top_depth, bottom_depth)


    @app.callback(
        Output("project-a-log-tracks", "figure"),
        Output("project-a-vsh-report", "figure"),

        Input("project-a-well-select", "value"),
        Input("project-a-track-select", "value"),
        Input("project-a-vsh-model-select", "value"),
        Input("project-a-vsh-cutoff", "value"),
        Input("project-a-report-model-select", "value"),
        Input("project-a-top-depth", "value"),
        Input("project-a-bottom-depth", "value"),
    )
    def update_project_a_tracks(
        well,
        selected_logs,
        selected_models,
        cutoff,
        report_models,
        top_depth,
        bottom_depth,
    ):

        if not well:
            return go.Figure(), go.Figure()

        tracks_fig = create_log_track_figure(
            well,
            selected_logs,
            selected_models,
            cutoff,
            top_depth,
            bottom_depth,
        )

        report_fig = create_vsh_report_figure(
            well,
            report_models,
        )

        return tracks_fig, report_fig
