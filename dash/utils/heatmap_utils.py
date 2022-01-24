import plotly.graph_objects as go
from utils.figure_utils import gen_subplot_fig, adjust_layout, add_basic_histograms, add_advanced_histograms

def heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution):
    colorscale=[
        [0.0, 'rgba(0,0,0,0)'],
        [1.0, 'rgba(0,0,0,1)'],
    ]

    fig.add_trace(
        go.Histogram2d(
            x=df[xaxis_column_name],
            y=df[yaxis_column_name],
            colorscale=colorscale,
            # zmax=10,
            nbinsx=resolution,
            nbinsy=resolution,
            zauto=True,
            showscale=False,
        ),
        row=2, 
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df[xaxis_column_name],
            y=df[yaxis_column_name],
            mode='markers',
            showlegend=False,
            marker=dict(
                symbol='circle',
                opacity=0.7,
                color='white',
                size=8,
                line=dict(width=1),
            )
        ),
        row=2, 
        col=1
    )

    return fig

def basic_heatmap(df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig = heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution)
    fig = add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig

def advanced_heatmap(df, label_column, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig = heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution)
    
    problematics_df = df.loc[df[label_column] > 0]

    fig = add_advanced_histograms(fig, df, problematics_df, xaxis_column_name, yaxis_column_name, resolution)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig