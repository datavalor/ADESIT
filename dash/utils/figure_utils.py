from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

from constants import *

def convert_from_numpy_edges(edges):
    centers = []
    for i in range(len(edges)-1):
        centers.append((edges[i]+edges[i+1])/2)
    return centers

def gen_subplot_fig(xaxis_column_name, yaxis_column_name):
    return make_subplots(
        rows=2, cols=2,
        row_heights=[0.1,0.4],
        column_widths=[0.4,0.1],
        shared_xaxes = True,
        shared_yaxes = True,
        horizontal_spacing=0.01, 
        vertical_spacing=0.03,
        x_title= str(xaxis_column_name),
        y_title= str(yaxis_column_name),
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]]
    )

def adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos):
    for axis, func in [(xaxis_column_name, fig.update_xaxes), (yaxis_column_name, fig.update_yaxes)]:
        if session_infos["user_columns_type"][axis] == 'categorical':
            func(type='category', categoryorder='array', categoryarray=session_infos["cat_columns_ncats"][axis][0], row=2, col=1)
            n_cats = len(session_infos["cat_columns_ncats"][axis][0])
            func(range=[0-0.5, n_cats-1+0.5], row=2, col=1)
        elif session_infos["user_columns_type"][axis] == 'numerical':
            vmin = session_infos["num_columns_minmax"][axis][0]
            vmax = session_infos["num_columns_minmax"][axis][1]
            func(range=[0.95*vmin, 1.05*vmax], row=2, col=1)

    fig.update_layout(barmode='overlay', showlegend=False)
    fig.update_traces(opacity=0.9)
    fig.update_layout(margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, hovermode='closest', height = 550)

    return fig

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
        bin_labels, _ = session_infos["cat_columns_ncats"][axis]
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