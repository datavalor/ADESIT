from plotly.subplots import make_subplots

import utils.data_utils as data_utils
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
    fig.update_xaxes(range=data_utils.attribute_min_max(xaxis_column_name, session_infos, rel_margin=0.1), row=2, col=1)
    fig.update_yaxes(range=data_utils.attribute_min_max(yaxis_column_name, session_infos, rel_margin=0.1), row=2, col=1)
    # print(data_utils.attribute_min_max(xaxis_column_name, session_infos, rel_margin=0.05))
    fig.update_traces(opacity=0.9)
    fig.update_layout(
        margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, 
        hovermode='closest', 
        height = 550,
        showlegend=False,
        barmode='group'
    )
    return fig