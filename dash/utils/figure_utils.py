from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

from constants import *

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

def add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    histo_data = []
    for axis in [xaxis_column_name, yaxis_column_name]:
        if session_infos['user_columns_type'][axis]=='numerical':
            min, max = session_infos['num_columns_minmax'][axis]
            # delta = 1*(max-min)/resolution
            delta = 0
            bin_counts, bin_edges = np.histogram(
                df[axis], 
                bins=resolution,
                range=(min-delta, max+delta)
            )
            bin_labels = []
            for i in range(len(bin_edges)-1):
                bin_labels.append((bin_edges[i]+bin_edges[i+1])/2)
        else:
            bin_labels, bin_counts = session_infos["cat_columns_ncats"][axis]
        histo_data.append([bin_counts, bin_labels])

    fig.add_trace(
        go.Bar(y=histo_data[0][0], x=histo_data[0][1], marker_color='#000000'),
        row=1, col=1, 
    )

    fig.add_trace(
        go.Bar(x=histo_data[1][0], y=histo_data[1][1], marker_color='#000000', orientation="h"),
        row=2, col=2, 
    )
    return fig

def add_advanced_histograms(fig, graph_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution):
    fig.add_trace(go.Histogram(x = graph_df[str(xaxis_column_name)], marker_color=FREE_COLOR, bingroup=1, nbinsx=resolution), row=1, col=1, secondary_y=False)
    fig.add_trace(go.Histogram(x = problematics_df[str(xaxis_column_name)], marker_color=CE_COLOR, bingroup=1,  nbinsx=resolution), row=1, col=1,secondary_y=False)
    
    fig.add_trace(go.Histogram(y = graph_df[str(yaxis_column_name)], marker_color=FREE_COLOR, bingroup=2, nbinsy=resolution), row=2, col=2)
    fig.add_trace(go.Histogram(y = problematics_df[str(yaxis_column_name)], marker_color=CE_COLOR, bingroup=2,  nbinsy=resolution), row=2, col=2)

    return fig