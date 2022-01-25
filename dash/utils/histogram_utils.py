import plotly.graph_objects as go
import numpy as np

from utils.figure_utils import convert_from_numpy_edges
from constants import *

def make_histogram(df, axis, resolution, session_infos, minmax=None):
    if session_infos['user_columns_type'][axis]=='numerical':
        if minmax is None: min, max = session_infos['num_columns_minmax'][axis]
        else: min, max = minmax
        # delta = 1*(max-min)/resolution
        delta = 0
        bin_counts, bin_edges = np.histogram(
            df[axis], 
            bins=resolution,
            range=(min-delta, max+delta)
        )
        bin_labels = convert_from_numpy_edges(bin_edges)
    else:
        bin_labels = session_infos["cat_columns_ncats"][axis]["unique_values"]
        unique, count = np.unique(df[axis], return_counts=True)
        count_dict = {}
        for i in range(len(unique)): count_dict[unique[i]]=count[i]
        bin_counts = [count_dict.get(label,0) for label in bin_labels]
    return [bin_counts, bin_labels]


def add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    histo_data = []
    for axis in [xaxis_column_name, yaxis_column_name]:
        histo_data.append(make_histogram(df, axis, resolution, session_infos))

    fig.add_trace(
        go.Bar(y=histo_data[0][0], x=histo_data[0][1], marker_color=NON_ANALYSED_COLOR),
        row=1, col=1, 
    )

    fig.add_trace(
        go.Bar(x=histo_data[1][0], y=histo_data[1][1], marker_color=NON_ANALYSED_COLOR, orientation="h"),
        row=2, col=2, 
    )
    return fig

def add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    histo_data_x_free = make_histogram(non_problematics_df, xaxis_column_name, resolution, session_infos, minmax=session_infos['num_columns_minmax'].get(xaxis_column_name, None))
    histo_data_x_prob = make_histogram(problematics_df, xaxis_column_name, resolution, session_infos, minmax=session_infos['num_columns_minmax'].get(xaxis_column_name, None))
    fig.add_trace(
        go.Bar(y=histo_data_x_free[0], x=histo_data_x_free[1], name='Free tuples', offsetgroup=0, marker_color=FREE_COLOR),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(y=histo_data_x_prob[0], x=histo_data_x_free[1], name='Involved tuples', offsetgroup=1, marker_color=CE_COLOR),
        row=1, col=1
    )

    histo_data_y_free = make_histogram(non_problematics_df, yaxis_column_name, resolution, session_infos, minmax=session_infos['num_columns_minmax'].get(yaxis_column_name, None))
    histo_data_y_prob = make_histogram(problematics_df, yaxis_column_name, resolution, session_infos, minmax=session_infos['num_columns_minmax'].get(yaxis_column_name, None))
    fig.add_trace(
        go.Bar(x=histo_data_y_free[0], y=histo_data_y_free[1], name='Free tuples', offsetgroup=0, marker_color=FREE_COLOR, orientation="h"),
        row=2, col=2
    )
    fig.add_trace(
        go.Bar(x=histo_data_y_prob[0], y=histo_data_y_free[1], name='Involved tuples', offsetgroup=1, marker_color=CE_COLOR, orientation="h"),
        row=2, col=2
    )
    return fig