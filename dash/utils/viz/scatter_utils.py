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
        add_trace_args = {}
    ):
    df = session_infos['data'][data_key]
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
    return fig

def basic_scatter(session_infos, xaxis_column_name, yaxis_column_name, resolution):
    fig = gen_subplot_fig(xaxis_column_name, yaxis_column_name)
    marker_args = {
        'opacity': 0.6,
        'color': NON_ANALYSED_COLOR,
        'line_width': 0
    }
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=marker_args, add_trace_args={'row': 2, 'col': 1}) 
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
    free_marker_args = {
        'opacity': nprob_opacity,
        'color': FREE_COLOR,
        'line_width': 0
    }
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=free_marker_args, data_key='df_free', add_trace_args={'row': 2, 'col': 1})
    prob_marker_args = {
        'opacity': prob_opacity,
        'color': CE_COLOR,
        'line_width': 0,
        'symbol': 'cross'
    }
    fig = add_basic_scatter(fig, session_infos, xaxis_column_name, yaxis_column_name, marker_args=prob_marker_args , data_key='df_prob', add_trace_args={'row': 2, 'col': 1})
    fig = hist_gen.add_advanced_histograms(fig, session_infos, xaxis_column_name, resolution, add_trace_args={'row': 1, 'col': 1})
    fig = hist_gen.add_advanced_histograms(fig, session_infos, yaxis_column_name, resolution, orientation='h', add_trace_args={'row': 2, 'col': 2})
    fig = adjust_layout(fig, session_infos, xaxis_column_name, yaxis_column_name)

    return fig

def add_selection_to_scatter(fig, session_infos, selection_infos, xaxis_column_name, yaxis_column_name):
    # Deleting previous selections
    fig.data = tuple([datum for datum in fig.data if datum['name']!='selection'])

    # Drawing points
    if selection_infos.get('point', None) is not None:
        selected_point=selection_infos['point']
        in_violation_with = selection_infos['in_violation_with']
        if not in_violation_with.empty:
            involved_points={
                'data': {
                    'df': in_violation_with
                }
            }
            fig=add_basic_scatter(
                fig, involved_points, xaxis_column_name, yaxis_column_name, 
                marker_args = {
                    'opacity': 0.9,
                    'color': CE_COLOR,
                    'size': 12,
                    'line_width': 2,
                    'line_color': 'black',
                    'symbol': 'cross'
                },
                hover=False,
                scatter_args = {
                    'name': 'selection'
                },
                add_trace_args={'row': 2, 'col': 1}
            )

        selection_style = figure_utils.choose_selected_point_style(session_infos, selection_infos)
        selected_point_data={
            'data': {
                'df': pd.DataFrame([selected_point])
            }
        }
        fig=add_basic_scatter(
            fig, selected_point_data, xaxis_column_name, yaxis_column_name, 
            marker_args = {
                'opacity': 0.9,
                'color': selection_style[0],
                'size': 14,
                'line_width': 2,
                'line_color': selection_style[1],
                'symbol': selection_style[2]
            },
            hover=False,
            scatter_args = {
                'name': 'selection'
            },
            add_trace_args={'row': 2, 'col': 1}
        )
        return fig
    else:
        return fig