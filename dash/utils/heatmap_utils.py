import numpy as np

import plotly.graph_objects as go
from utils.figure_utils import gen_subplot_fig, adjust_layout, convert_from_numpy_edges
import utils.histogram_utils as hist_gen

from constants import *

def heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    colorscale=[
        [0.0, 'rgba(0,0,0,0)'],
        [1.0, 'rgba(0,0,0,1)'],
    ]
    
    # We need to get the label encoded columns if the axis is categorical
    if session_infos["user_columns_type"][xaxis_column_name]=="categorical": xaxis_column_name += SUFFIX_OF_ENCODED_COLS
    if session_infos["user_columns_type"][yaxis_column_name]=="categorical": yaxis_column_name += SUFFIX_OF_ENCODED_COLS
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
    fig = heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = hist_gen.add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig

def advanced_heatmap(df, label_column, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig = heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    
    non_problematics_df = df.loc[df[label_column] == 0]
    problematics_df = df.loc[df[label_column] > 0]

    fig = hist_gen.add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    fig.update_layout(barmode='group')
    fig.update_layout(barmode='group')
    return fig