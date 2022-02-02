import plotly.graph_objects as go

from utils.figure_utils import gen_subplot_fig, adjust_layout
import utils.histogram_utils as hist_gen
from constants import *

def gen_hovertemplate(df, session_infos):
    col_pos = {col: i for i, col in enumerate(df.columns)}
    # Fetching and grouping column names
    features = session_infos["X"]
    target = session_infos["Y"]
    other = []
    for col in session_infos['user_columns']: 
        if col not in features and col not in target:
            other.append(col)
    # Constructing hovertemplate
    hovertemplate = f'[id]: %{{customdata[{col_pos[ADESIT_INDEX]}]}} <br>'
    for col in features: hovertemplate+=f"[F] {col}: %{{customdata[{col_pos[col]}]}} <br>"
    for col in target: hovertemplate+=f"[T] {col}: %{{customdata[{col_pos[col]}]}} <br>"
    for col in other: hovertemplate+=f"{col}: %{{customdata[{col_pos[col]}]}} <br>"
    hovertemplate+="<extra></extra>"
    return hovertemplate

def gen_marker(symbol='circle', opacity=1, marker_size=8, marker_line_width=1, color="white"):
    return {
        'symbol': symbol,
        'opacity': opacity, 
        'size': marker_size, 
        'color': color,
        'line':{
            'color':'Black',
            'width': marker_line_width
        }
    }

def add_basic_scatter(
        fig, 
        df, xaxis_column_name, 
        yaxis_column_name, 
        session_infos=None, 
        marker_size=7, 
        marker_symbol='circle',
        marker_line_width=0, 
        marker_opacity=1, 
        marker_color="black"
    ):
    marker = gen_marker(
        symbol=marker_symbol,
        marker_size=marker_size,
        opacity=marker_opacity,
        marker_line_width=marker_line_width,
        color=marker_color
    )
    params = {
        'x': df[xaxis_column_name], 
        'y': df[yaxis_column_name], 
        'mode': 'markers', 
        'marker': marker
    }
    if session_infos is not None:
        params['customdata']=df.to_numpy()
        params['hovertemplate']=gen_hovertemplate(df, session_infos)
    
    fig.add_trace(
        go.Scattergl(**params),
        row=2, col=1
    )
    return fig

def basic_scatter(df, xaxis_column_name, yaxis_column_name, resolution, session_infos):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig = add_basic_scatter(fig, df, xaxis_column_name, yaxis_column_name, session_infos=session_infos, marker_opacity=0.6, marker_color=NON_ANALYSED_COLOR) 
    fig = hist_gen.add_basic_histograms(fig, df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, df, xaxis_column_name, yaxis_column_name, session_infos)
    return fig

def advanced_scatter(graph_df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, resolution, view='ALL', selection=False, session_infos=None):
    _class = str(right_attrs[0])
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)

    non_problematics_df = graph_df.loc[graph_df[label_column] == 0]
    problematics_df = graph_df.loc[graph_df[label_column] > 0]
    if selection:
        prob_opacity, nprob_opacity = 0.5, 0.5
    else:
        if view == 'NP': prob_opacity, nprob_opacity = 0.1, 0.7
        elif view == 'P': prob_opacity, nprob_opacity = 0.7, 0.1
        else: prob_opacity, nprob_opacity = 0.7, 0.7
    
    fig = add_basic_scatter(fig, non_problematics_df, xaxis_column_name, yaxis_column_name, session_infos=session_infos, marker_opacity=nprob_opacity, marker_color=FREE_COLOR)
    fig = add_basic_scatter(fig, problematics_df, xaxis_column_name, yaxis_column_name, session_infos=session_infos, marker_opacity=prob_opacity, marker_color=CE_COLOR, marker_symbol="cross")
    fig = hist_gen.add_advanced_histograms(fig, non_problematics_df, problematics_df, xaxis_column_name, yaxis_column_name, resolution, session_infos)
    fig = adjust_layout(fig, graph_df, xaxis_column_name, yaxis_column_name, session_infos)

    return fig

def add_selection_to_scatter(fig, graph_df, right_attrs, xaxis_column_name, yaxis_column_name, prob_mark_symbol = "cross", selected=None):
    if selected is not None:
        selected_point=graph_df.loc[[selected[0]]]
        if len(selected)>1:
            selection_color = SELECTED_COLOR_BAD
            selection_symbol = prob_mark_symbol
            involved_points=graph_df.loc[selected[1:]]
            fig=add_basic_scatter(
                fig, involved_points, xaxis_column_name, yaxis_column_name, 
                marker_opacity=0.9, 
                marker_color=CE_COLOR, 
                marker_size=12, 
                marker_line_width=2,
                marker_symbol = selection_symbol
            )
        else:
            selection_color = SELECTED_COLOR_GOOD
            selection_symbol = "circle"
        fig=add_basic_scatter(
            fig, selected_point, xaxis_column_name, yaxis_column_name, 
            marker_opacity=0.9, 
            marker_color=selection_color, 
            marker_size=14,
            marker_line_width=2,
            marker_symbol = selection_symbol
        )
        return fig
    else:
        return fig