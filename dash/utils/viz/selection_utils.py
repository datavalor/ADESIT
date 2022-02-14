import plotly.graph_objects as go
import pandas as pd

import utils.viz.scatter_utils as scatter_utils
import utils.viz.figure_utils as figure_utils

from constants import *

def add_selection_as_vertical_lines(
    figure, 
    session_infos, 
    selection_infos, 
    xaxis_column_name, 
    yaxis_column_name, 
    minmax=None,
    add_trace_args={},
    orientation = 'v',
    remove_previous_selections=True
):
    # Deleting previous selections
    if remove_previous_selections:
        figure.data = tuple([datum for datum in figure.data if datum['name']!='selection'])

    hist_axis = xaxis_column_name if orientation == 'v' else yaxis_column_name

    # Drawing points
    point = selection_infos['point']
    if point is None: return figure

    in_violation_with = selection_infos['in_violation_with']
    if minmax is None: min, max = session_infos['user_columns'][yaxis_column_name].get_minmax(auto_margin=True)
    else: min, max = minmax
    point_line_color = figure_utils.choose_selected_point_style(session_infos, selection_infos)[0]

    xrange, yrange = [point[hist_axis],point[hist_axis]], [min, max]
    if orientation=='h': xrange, yrange = yrange, xrange
    figure.add_trace(
        go.Scatter(
            x=xrange, 
            y=yrange, 
            mode='lines', 
            line=dict(color=point_line_color, width=3),
            name='selection',
            yaxis='y'

        ),
        **add_trace_args
    )
    for _, row in in_violation_with.iterrows():
        xrange, yrange = [row[hist_axis],row[hist_axis]], [min, max]
        if orientation=='h': xrange, yrange = yrange, xrange
        figure.add_trace(
            go.Scatter(
                x=xrange, 
                y=yrange, 
                mode='lines', 
                line=dict(color=CE_COLOR, width=2),
                name='selection',
                yaxis='y'
            ),
            **add_trace_args
        )
       

def add_selection_as_scatterpoints(
    fig, 
    session_infos, 
    selection_infos, 
    xaxis_column_name, 
    yaxis_column_name
):
    # Deleting previous selections
    fig.data = tuple([datum for datum in fig.data if datum['name']!='selection'])

    # Drawing points
    if selection_infos.get('point', None) is None: return fig
    
    selected_point=selection_infos['point']
    in_violation_with = selection_infos['in_violation_with']
    if not in_violation_with.empty:
        involved_points={
            'data': {
                'df': in_violation_with
            }
        }
        scatter_utils.add_basic_scatter(
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
    scatter_utils.add_basic_scatter(
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