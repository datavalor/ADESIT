import plotly.graph_objects as go

from constants import *
import utils.viz.figure_utils as figure_utils

def add_basic_rangeslider(
        fig, 
        session_infos,
        yaxis_column_name,
    ):
    df_minmax = session_infos['df_minmax']
    time_infos = session_infos['time_infos']
    fig.add_trace(
        go.Scatter(
            x=df_minmax[time_infos['time_attribute']].to_numpy(), 
            y=df_minmax[yaxis_column_name].to_numpy(),
            marker = {
                'color': NON_ANALYSED_COLOR
            }
        )
    )
    fig.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )
    fig.add_vrect(
        x0=time_infos['time_periods_list'][time_infos['current_time_period']], 
        x1=time_infos['time_periods_list'][time_infos['current_time_period']+1],
        fillcolor='green', 
        opacity=0.2, 
        line_width=0
    )
    return fig

def update_rangeslider_layout(fig, session_infos, yaxis_column_name):
    return fig.update_layout(
        margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, 
        hovermode='closest', 
        height = 650,
        showlegend=False,
        barmode='stack',
        xaxis_title=session_infos['time_infos']['time_attribute'],
        yaxis_title=yaxis_column_name
    )

def add_selection_to_rangeslider(fig, session_infos, selection_infos, yaxis_column_name):
    # Deleting previous selections
    fig.data = tuple([datum for datum in fig.data if datum['name']!='selection'])

    # Drawing points
    if selection_infos.get('point', None) is not None:
        selected_point=selection_infos['point']
        in_violation_with = selection_infos['in_violation_with']
        if not in_violation_with.empty:
            involved_style = (SELECTED_COLOR_BAD, SELECTED_COLOR_BAD_OUTLINE)            
        else:
            selection_style = figure_utils.choose_selected_point_style(session_infos, selection_infos)
            selection_symbol = 'circle'
        return fig
    else:
        return fig