import numpy as np

import plotly.graph_objects as go
from utils.figure_utils import gen_subplot_fig, adjust_layout, convert_from_numpy_edges
import utils.histogram_utils as hist_gen
import utils.data_utils as data_utils

from constants import *

def get_data_and_res_for_histogram(df, axis, target_resolution, session_infos):
    data=df[axis]
    resolution = target_resolution
    # if the data is categorical, we need to label encode the data
    if session_infos["user_columns_type"][axis]==CATEGORICAL_COLUMN: 
        le = session_infos["cat_columns_ncats"][axis]["label_encoder"] 
        data = le.transform(data)
        ncats = len(session_infos["cat_columns_ncats"][axis]["unique_values"])
        resolution = np.arange(0,ncats+1)-0.5
    return data, resolution

def create_bins_from_edges_from_histogram(edges, axis, session_infos):
    bins = convert_from_numpy_edges(edges)
    if session_infos["user_columns_type"][axis]==CATEGORICAL_COLUMN: 
        le = session_infos["cat_columns_ncats"][axis]["label_encoder"] 
        bins = le.inverse_transform(np.array(bins, dtype=np.int))
    return bins

def compute_2d_histogram(df, xaxis_column_name, yaxis_column_name, resolution, session_infos, range=None):
    # We need to get the label encoded columns if the axis is categorical
    xdata, xres = get_data_and_res_for_histogram(df, xaxis_column_name, resolution, session_infos)
    ydata, yres = get_data_and_res_for_histogram(df, yaxis_column_name, resolution, session_infos)
    if range is None: 
        range=[
            session_infos['num_columns_minmax'].get(xaxis_column_name, [0,xres]),
            session_infos['num_columns_minmax'].get(yaxis_column_name, [0,yres])
        ]
    H, xedges, yedges = np.histogram2d(xdata, ydata, bins=(xres, yres), range=range)
    xbins = create_bins_from_edges_from_histogram(xedges, xaxis_column_name, session_infos)
    ybins = create_bins_from_edges_from_histogram(yedges, yaxis_column_name, session_infos)

    return H, xbins, ybins

def heatmap_basic_bloc(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    colorscale=[
        [0.0, 'rgba(0,0,0,0)'],
        [1.0, 'rgba(0,0,0,1)'],
    ]

    H, xbins, ybins = compute_2d_histogram(df, xaxis_column_name, yaxis_column_name, resolution, session_infos)

    fig.add_trace(
        go.Heatmap(
            z=np.transpose(H),
            x=xbins,
            y=ybins,
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
    H_np, xbins_np, ybins_np = compute_2d_histogram(non_problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    H, xbins, ybins = compute_2d_histogram(problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)

    fig = hist_gen.add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    fig.update_layout(barmode='group')
    fig.update_layout(barmode='group')
    return fig