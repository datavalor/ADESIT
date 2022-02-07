import plotly.graph_objects as go

from utils.viz.figure_utils import gen_subplot_fig, adjust_layout
import utils.viz.histogram_utils as hist_gen
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
        session_infos, 
        xaxis_column_name, 
        yaxis_column_name,
        marker_size=7, 
        marker_symbol='circle',
        marker_line_width=0, 
        marker_opacity=1, 
        marker_color='black', 
        data_key='df',
        hover=True,
        scatter_params = {}
    ):
    df = session_infos['data'][data_key]
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
        'marker': marker,
        **scatter_params
    }
    if session_infos is not None:
        params['customdata']=df.to_numpy()
        if hover: params['hovertemplate']=gen_hovertemplate(df, session_infos)
    
    fig.add_trace(
        go.Scattergl(**params),
        row=2, col=1
    )
    return fig

def basic_scatter(session_infos, xaxis_column_name, yaxis_column_name, resolution):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_opacity=0.6, marker_color=NON_ANALYSED_COLOR) 
    fig = hist_gen.add_basic_histograms(fig, session_infos, xaxis_column_name, resolution, add_trace_args={'row': 1, 'col': 1})
    fig = hist_gen.add_basic_histograms(fig, session_infos, yaxis_column_name, resolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    fig = adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)
    return fig

def advanced_scatter(session_infos, xaxis_column_name, yaxis_column_name, resolution, view='ALL', selection=False):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)

    if selection:
        prob_opacity, nprob_opacity = 0.5, 0.5
    else:
        if view == 'NP': prob_opacity, nprob_opacity = 0.1, 0.7
        elif view == 'P': prob_opacity, nprob_opacity = 0.7, 0.1
        else: prob_opacity, nprob_opacity = 0.7, 0.7
    
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_opacity=nprob_opacity, marker_color=FREE_COLOR, data_key='df_free')
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_opacity=prob_opacity, marker_color=CE_COLOR, marker_symbol='cross', data_key='df_prob')
    fig = hist_gen.add_advanced_histograms(fig, session_infos, xaxis_column_name, resolution, add_trace_args={'row': 1, 'col': 1})
    fig = hist_gen.add_advanced_histograms(fig, session_infos, yaxis_column_name, resolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    fig = adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)

    return fig

def add_selection_to_scatter(fig, session_infos, selection_infos, xaxis_column_name, yaxis_column_name, prob_mark_symbol = "cross"):
    # Deleting previous selections
    fig.data = tuple([datum for datum in fig.data if datum['name']!='selection'])

    # Drawing points
    if selection_infos.get('point', None) is not None:
        selected_point=selection_infos['point']
        in_violation_with = selection_infos['in_violation_with']
        if not in_violation_with.empty:
            selection_color = SELECTED_COLOR_BAD
            selection_symbol = prob_mark_symbol
            involved_points={
                'data': {
                    'df': in_violation_with
                }
            }
            fig=add_basic_scatter(
                fig, involved_points, xaxis_column_name, yaxis_column_name, 
                marker_opacity=0.9, 
                marker_color=CE_COLOR, 
                marker_size=12, 
                marker_line_width=2,
                marker_symbol = selection_symbol,
                hover=False,
                scatter_params = {
                    'name': 'selection'
                }
            )
        else:
            if session_infos['data']['df_free'] is not None:
                selection_color = SELECTED_COLOR_GOOD
            else:
                selection_color = NON_ANALYSED_COLOR
            selection_symbol = "circle"
        selected_point_data={
            'data': {
                'df': pd.DataFrame([selected_point])
            }
        }
        fig=add_basic_scatter(
            fig, selected_point_data, xaxis_column_name, yaxis_column_name, 
            marker_opacity=0.9, 
            marker_color=selection_color, 
            marker_size=14,
            marker_line_width=2,
            marker_symbol = selection_symbol,
            hover=False,
            scatter_params = {
                'name': 'selection'
            }
        )
        return fig
    else:
        return fig