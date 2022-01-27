import plotly.graph_objects as go
import numpy as np

from utils.figure_utils import convert_from_numpy_edges
import utils.data_utils as data_utils
from constants import *

def compute_1d_histogram(df, axis, resolution, session_infos, minmax=None):
    if data_utils.is_categorical(axis, session_infos):
        bins = session_infos["cat_columns_ncats"][axis]["unique_values"]
        unique_values, count = np.unique(df[axis], return_counts=True)
        count_dict = {}
        for i in range(len(unique_values)): count_dict[unique_values[i]]=count[i]
        bins_counts = [count_dict.get(label,0) for label in bins]
    else:
        if minmax is None: min, max = data_utils.attribute_min_max(axis, session_infos)
        else: min, max = minmax
        bins_counts, bins_edges = np.histogram(
            df[axis], 
            bins=resolution,
            range=(min, max)
        )
        bins = convert_from_numpy_edges(bins_edges)
    return [bins, bins_counts]

def add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    histo_data = []
    for axis in [xaxis_column_name, yaxis_column_name]:
        histo_data.append(compute_1d_histogram(df, axis, resolution, session_infos))

    fig.add_trace(
        go.Bar(x=histo_data[0][0], y=histo_data[0][1], marker_color=NON_ANALYSED_COLOR),
        row=1, col=1, 
    )

    fig.add_trace(
        go.Bar(x=histo_data[1][1], y=histo_data[1][0], marker_color=NON_ANALYSED_COLOR, orientation="h"),
        row=2, col=2, 
    )
    return fig

def add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    xminmax=data_utils.attribute_min_max(xaxis_column_name, session_infos)
    histo_data_x_free = compute_1d_histogram(non_problematics_df, xaxis_column_name, resolution, session_infos, minmax=xminmax)
    histo_data_x_prob = compute_1d_histogram(problematics_df, xaxis_column_name, resolution, session_infos, minmax=xminmax)
    fig.add_trace(
        go.Bar(x=histo_data_x_free[0], y=histo_data_x_free[1], name='Free tuples', offsetgroup=0, marker_color=FREE_COLOR),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=histo_data_x_free[0], y=histo_data_x_prob[1], name='Involved tuples', offsetgroup=1, marker_color=CE_COLOR),
        row=1, col=1
    )

    yminmax=data_utils.attribute_min_max(xaxis_column_name, session_infos)
    histo_data_y_free = compute_1d_histogram(non_problematics_df, yaxis_column_name, resolution, session_infos, minmax=yminmax)
    histo_data_y_prob = compute_1d_histogram(problematics_df, yaxis_column_name, resolution, session_infos, minmax=yminmax)
    fig.add_trace(
        go.Bar(x=histo_data_y_free[1], y=histo_data_y_free[0], name='Free tuples', offsetgroup=0, marker_color=FREE_COLOR, orientation="h"),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(x=histo_data_y_prob[1], y=histo_data_y_free[0], name='Involved tuples', offsetgroup=1, marker_color=CE_COLOR, orientation="h"),
        row=2, col=2
    )
    return fig