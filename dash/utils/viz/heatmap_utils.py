import numpy as np

import plotly.graph_objects as go
from utils.viz.figure_utils import gen_subplot_fig, adjust_layout, convert_from_numpy_edges
import utils.viz.histogram_utils as hist_gen
import utils.viz.scatter_utils as scatter_utils
import matplotlib

from constants import *

def get_data_and_res_for_histogram(
    session_infos, 
    column_name, 
    target_resolution,
    data_key = 'df'
):
    data = session_infos['data'][data_key][column_name]
    attr = session_infos['user_columns'][column_name]
    # if the data is categorical, we need to label encode the data
    resolution = target_resolution
    if attr.is_categorical(): 
        le = attr.label_encoder
        data = le.transform(data)
        ncats = len(attr.sorted_classes)
        resolution = np.arange(0,ncats+1)-0.5
    return data, resolution

def create_bins_from_edges_from_histogram(edges, column_name, session_infos):
    bins = convert_from_numpy_edges(edges)
    attr = session_infos['user_columns'][column_name]
    if attr.is_categorical():
        bins = attr.label_encoder.inverse_transform(np.array(bins, dtype=np.int))
    return bins

def compute_2d_histogram(
    session_infos, 
    xaxis_column_name, 
    yaxis_column_name, 
    xresolution, yresolution,
    range=None,
    data_key = 'df'
):
    # We need to get the label encoded columns if the axis is categorical
    xdata, xres = get_data_and_res_for_histogram(session_infos, xaxis_column_name, xresolution, data_key=data_key)
    ydata, yres = get_data_and_res_for_histogram(session_infos, yaxis_column_name, yresolution, data_key=data_key)
    if range is None: 
        range=[
            session_infos['user_columns'][xaxis_column_name].get_minmax(relative_margin=0.05),
            session_infos['user_columns'][yaxis_column_name].get_minmax(relative_margin=0.05)
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

def basic_heatmap(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    H, xbins, ybins = compute_2d_histogram(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution)
    fig = add_basic_heatmap(fig, H, xbins, ybins)
    fig = scatter_utils.add_basic_scatter(
        fig, session_infos, xaxis_column_name, yaxis_column_name, 
        marker_args = {
            'opacity': 0.7,
            'color': 'white',
            'size': 6,
            'line_width': 1,
            'line_color': 'black',
            'symbol': 'circle'
        },
        add_trace_args={'row': 2, 'col': 1}
    )
    fig = hist_gen.add_basic_histograms(fig, session_infos, xaxis_column_name, xresolution, add_trace_args={'row': 1, 'col': 1})
    fig = hist_gen.add_basic_histograms(fig, session_infos, yaxis_column_name, yresolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    fig = adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)
    return fig

def advanced_heatmap(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)

    H_np, xbins_np, ybins_np = compute_2d_histogram(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution, data_key='df_free')
    H_pr, xbins_pr, ybins_pr = compute_2d_histogram(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution, data_key='df_prob')

    fig = add_basic_heatmap(fig, H_np, xbins_np, ybins_np, hue=FREE_COLOR)
    fig = add_basic_heatmap(fig, H_pr, xbins_pr, ybins_pr, hue=CE_COLOR)

    fig = scatter_utils.add_basic_scatter(
        fig, session_infos, xaxis_column_name, yaxis_column_name, 
        marker_args = {
            'opacity': 0.7,
            'color': 'white',
            'size': 6,
            'line_width': 1,
            'line_color': 'black',
            'symbol': 'circle'
        },
        data_key='df_free',
        add_trace_args={'row': 2, 'col': 1}
    )
    fig = scatter_utils.add_basic_scatter(
        fig, session_infos, xaxis_column_name, yaxis_column_name,
        marker_args = {
            'opacity': 0.7,
            'color': 'white',
            'size': 6,
            'line_width': 1,
            'line_color': 'black',
            'symbol': 'cross'
        },
        add_trace_args={'row': 2, 'col': 1},
        data_key='df_prob'
    )
    
    fig = hist_gen.add_advanced_histograms(fig, session_infos, xaxis_column_name, xresolution, add_trace_args={'row': 1, 'col': 1})
    fig = hist_gen.add_advanced_histograms(fig, session_infos, yaxis_column_name, yresolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    fig = adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)
    return fig