import numpy as np

import plotly.graph_objects as go
from utils.figure_utils import gen_subplot_fig, adjust_layout, add_basic_histograms, add_advanced_histograms, convert_from_numpy_edges

def heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution):
    colorscale=[
        [0.0, 'rgba(0,0,0,0)'],
        [1.0, 'rgba(0,0,0,1)'],
    ]

    H, xedges, yedges = np.histogram2d(df[xaxis_column_name], df[yaxis_column_name], bins=(resolution, resolution))
    fig.add_trace(
        go.Heatmap(
            z=np.transpose(H),
            x=convert_from_numpy_edges(xedges),
            y=convert_from_numpy_edges(yedges),
            showscale=False,
            colorscale=colorscale
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
    
    non_problematics_df = df.loc[df[label_column] == 0]
    problematics_df = df.loc[df[label_column] > 0]

    fig = add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    fig.update_layout(barmode='group')
    fig.update_layout(barmode='group')
    return fig