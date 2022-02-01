import numpy as np

import plotly.graph_objects as go
from utils.figure_utils import gen_subplot_fig, adjust_layout, convert_from_numpy_edges
import utils.histogram_utils as hist_gen
import utils.data_utils as data_utils
import utils.scatter_utils as scatter_utils
import matplotlib

from constants import *

def get_data_and_res_for_histogram(df, axis, target_resolution, session_infos):
    data=df[axis]
    resolution = target_resolution
    # if the data is categorical, we need to label encode the data
    if data_utils.is_categorical(axis, session_infos): 
        le = session_infos["categorical_columns_infos"][axis]["label_encoder"] 
        data = le.transform(data)
        ncats = len(session_infos["categorical_columns_infos"][axis]["unique_values"])
        resolution = np.arange(0,ncats+1)-0.5
    return data, resolution

def create_bins_from_edges_from_histogram(edges, axis, session_infos):
    bins = convert_from_numpy_edges(edges)
    if data_utils.is_categorical(axis, session_infos): 
        le = session_infos["categorical_columns_infos"][axis]["label_encoder"] 
        bins = le.inverse_transform(np.array(bins, dtype=np.int))
    return bins

def compute_2d_histogram(df, xaxis_column_name, yaxis_column_name, resolution, session_infos, range=None):
    # We need to get the label encoded columns if the axis is categorical
    xdata, xres = get_data_and_res_for_histogram(df, xaxis_column_name, resolution, session_infos)
    ydata, yres = get_data_and_res_for_histogram(df, yaxis_column_name, resolution, session_infos)
    if range is None: 
        range=[
            data_utils.attribute_min_max(xaxis_column_name, session_infos, rel_margin=0.05),
            data_utils.attribute_min_max(yaxis_column_name, session_infos, rel_margin=0.05),
        ]
    H, xedges, yedges = np.histogram2d(xdata, ydata, bins=(xres, yres), range=range)
    xbins = create_bins_from_edges_from_histogram(xedges, xaxis_column_name, session_infos)
    ybins = create_bins_from_edges_from_histogram(yedges, yaxis_column_name, session_infos)

    return H, xbins, ybins

def add_basic_heatmap(fig, H, xbins, ybins, hue="#000000"):
    RBG_3digits_str = ",".join([str(round(n,2)) for n in matplotlib.colors.to_rgb(hue)])
    colorscale=[
        [0.0, f'rgba({RBG_3digits_str},0)'],
        [1.0, f'rgba({RBG_3digits_str},1)'],
    ]

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

    return fig

def basic_heatmap(df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    H, xbins, ybins = compute_2d_histogram(df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = add_basic_heatmap(fig, H, xbins, ybins)
    fig = scatter_utils.add_basic_scatter(
        fig, df, xaxis_column_name, yaxis_column_name, session_infos, 
        marker_color="white", 
        marker_opacity=0.7,
        marker_line_width=1
    )
    fig = hist_gen.add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig

def advanced_heatmap(df, label_column, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    
    non_problematics_df = df.loc[df[label_column] == 0]
    problematics_df = df.loc[df[label_column] > 0]
    H_np, xbins_np, ybins_np = compute_2d_histogram(non_problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    H_pr, xbins_pr, ybins_pr = compute_2d_histogram(problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)

    fig = add_basic_heatmap(fig, H_np, xbins_np, ybins_np, hue=FREE_COLOR)
    fig = add_basic_heatmap(fig, H_pr, xbins_pr, ybins_pr, hue=CE_COLOR)

    fig = scatter_utils.add_basic_scatter(
        fig, non_problematics_df, xaxis_column_name, yaxis_column_name, session_infos, 
        marker_color="white", 
        marker_opacity=0.7,
        marker_line_width=1,
        marker_symbol="circle"
    )
    fig = scatter_utils.add_basic_scatter(
        fig, problematics_df, xaxis_column_name, yaxis_column_name, session_infos, 
        marker_color="white", 
        marker_opacity=0.7,
        marker_line_width=1,
        marker_symbol="cross"
    )
    
    fig = hist_gen.add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig