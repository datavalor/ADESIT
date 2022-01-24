from plotly.subplots import make_subplots
import plotly.graph_objects as go

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
    if session_infos["user_columns_type"][xaxis_column_name] == 'categorical':
        fig.update_xaxes(type='category', categoryorder=CATEGORICAL_AXIS_ORDER, row=2, col=1)
        n_cats = session_infos["cat_columns_ncats"][xaxis_column_name]
        fig.update_xaxes(range=[0-0.5,n_cats-1+0.5], row=2, col=1, fixedrange=True)
    elif session_infos["user_columns_type"][xaxis_column_name] == 'numerical':
        xmin = session_infos["num_columns_minmax"][xaxis_column_name][0]
        xmax = session_infos["num_columns_minmax"][xaxis_column_name][1]
        fig.update_xaxes(range=[0.95*xmin, 1.05*xmax], row=2, col=1)

    if session_infos["user_columns_type"][yaxis_column_name] == 'categorical':
        fig.update_yaxes(type='category', categoryorder=CATEGORICAL_AXIS_ORDER, row=2, col=1)
        n_cats = session_infos["cat_columns_ncats"][yaxis_column_name]
        fig.update_yaxes(range=[0-0.5,n_cats-1+0.5], row=2, col=1, fixedrange=True)
    elif session_infos["user_columns_type"][yaxis_column_name] == 'numerical':
        ymin = session_infos["num_columns_minmax"][yaxis_column_name][0]
        ymax = session_infos["num_columns_minmax"][yaxis_column_name][1]
        fig.update_yaxes(range=[0.95*ymin, 1.05*ymax], row=2, col=1)

    fig.update_layout(barmode='overlay',showlegend=False)
    fig.update_traces(opacity=0.9)
    fig.update_layout(margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, hovermode='closest', height = 550)

    return fig

def add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name):
    fig.add_trace(
        go.Histogram(x = df[str(xaxis_column_name)], bingroup=1, nbinsx=20, marker_color=NON_ANALYSED_COLOR), #, marker_color='#000000', nbinsx=10, bingroup=1
        row=1, 
        col=1, 
        secondary_y=False
    )
    fig.add_trace(
        go.Histogram(y = df[str(yaxis_column_name)], bingroup=1, nbinsy=20, marker_color=NON_ANALYSED_COLOR), #, marker_color='#000000', nbinsx=10, bingroup=1
        row=2, 
        col=2, 
        secondary_y=False
    )
    return fig