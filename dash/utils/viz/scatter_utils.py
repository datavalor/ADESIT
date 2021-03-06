import plotly.graph_objects as go

from utils.viz.figure_utils import gen_subplot_fig, adjust_layout
import utils.viz.histogram_utils as hist_gen
import utils.viz.figure_utils as figure_utils
from constants import *

def gen_hovertemplate(df, session_infos):
    col_pos = {col: i for i, col in enumerate(df.columns)}
    # Fetching and grouping column names
    features = session_infos['X']
    target = session_infos['Y']
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

def gen_marker(symbol='circle', opacity=1, size=8, line_width=1, line_color='black', color="white"):
    return {
        'symbol': symbol,
        'opacity': opacity, 
        'size': size, 
        'color': color,
        'line':{
            'color': line_color,
            'width': line_width
        }
    }

def add_basic_scatter(
        fig, 
        session_infos, 
        xaxis_column_name, 
        yaxis_column_name,
        marker_args  = {},
        data_key='df',
        hover=True,
        scatter_args = {},
        add_trace_args = {},
        df=None
    ):
    if df is None: df = session_infos['data'][data_key]
    marker = gen_marker(**marker_args)
    params = {
        'x': df[xaxis_column_name], 
        'y': df[yaxis_column_name], 
        'mode': 'markers', 
        'marker': marker,
        **scatter_args
    }
    if session_infos is not None:
        df['real_id'] = df.index
        params['customdata']=df.to_numpy()
        if hover: params['hovertemplate']=gen_hovertemplate(df, session_infos)
    
    fig.add_trace(
        go.Scattergl(**params),
        **add_trace_args
    )

def basic_scatter(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    marker_args = {
        'opacity': 0.6,
        'color': NON_ANALYSED_COLOR,
        'line_width': 0
    }
    add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=marker_args, add_trace_args={'row': 2, 'col': 1}) 
    hist_gen.add_basic_histograms(fig, session_infos, xaxis_column_name, xresolution, add_trace_args={'row': 1, 'col': 1})
    hist_gen.add_basic_histograms(fig, session_infos, yaxis_column_name, yresolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)
    return fig

def advanced_scatter(session_infos, xaxis_column_name, yaxis_column_name, xresolution, yresolution, view='ALL', selection=False):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    if selection:
        prob_opacity, nprob_opacity = 0.5, 0.5
    else:
        if view == 'NP': prob_opacity, nprob_opacity = 0.1, 0.7
        elif view == 'P': prob_opacity, nprob_opacity = 0.7, 0.1
        else: prob_opacity, nprob_opacity = 0.7, 0.7
    free_marker_args = {
        'opacity': nprob_opacity,
        'color': FREE_COLOR,
        'line_width': 0
    }
    add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=free_marker_args, data_key='df_free', add_trace_args={'row': 2, 'col': 1})
    prob_marker_args = {
        'opacity': prob_opacity,
        'color': CE_COLOR,
        'line_width': 0,
        'symbol': 'cross'
    }
    add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=prob_marker_args , data_key='df_prob', add_trace_args={'row': 2, 'col': 1})
    hist_gen.add_advanced_histograms(fig, session_infos, xaxis_column_name, xresolution, add_trace_args={'row': 1, 'col': 1})
    hist_gen.add_advanced_histograms(fig, session_infos, yaxis_column_name, yresolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)
    return fig