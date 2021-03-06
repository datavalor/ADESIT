from plotly.subplots import make_subplots

from constants import *

def convert_from_numpy_edges(edges):
    centers = []
    for i in range(len(edges)-1):
        centers.append((edges[i]+edges[i+1])/2)
    return centers

def gen_subplot_fig(xaxis_column_name, yaxis_column_name, make_subplot_args={}):
    return make_subplots(
        rows=2, cols=2,
        row_heights=[0.1,0.4],
        column_widths=[0.4,0.1],
        shared_xaxes = True,
        shared_yaxes = True,
        horizontal_spacing=0.01, 
        vertical_spacing=0.03,
        x_title= xaxis_column_name,
        y_title= yaxis_column_name,
        specs=[[{"secondary_y": True}, {"secondary_y": False}],
            [{"secondary_y": False}, {"secondary_y": False}]],
        **make_subplot_args
    )

def adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name):
    fig.update_xaxes(range=session_infos['user_columns'][xaxis_column_name].get_minmax(auto_margin=True), row=2, col=1)
    fig.update_yaxes(range=session_infos['user_columns'][yaxis_column_name].get_minmax(auto_margin=True), row=2, col=1)
    fig.update_traces(opacity=0.9)
    fig.update_layout(
        margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, 
        hovermode='closest', 
        height = 650,
        showlegend=False,
        barmode='stack'
    )

def choose_selected_point_style(session_infos, selection_infos):
    if session_infos['data']['df_free'] is not None:
        if not selection_infos['in_violation_with'].empty:
            selection_style = (SELECTED_COLOR_BAD, SELECTED_COLOR_BAD_OUTLINE, 'cross')
        else:
            selection_style = (SELECTED_COLOR_GOOD, SELECTED_COLOR_GOOD_OUTLINE, 'circle')
    else:
        selection_style = (SELECTED_NON_ANALYSED_COLOR, SELECTED_NON_ANALYSED_COLOR_OUTLINE, 'circle')
    return selection_style