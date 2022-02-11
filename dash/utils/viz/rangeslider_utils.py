import plotly.graph_objects as go

from constants import *
import utils.viz.figure_utils as figure_utils
import utils.viz.scatter_utils as scatter_utils

def add_basic_rangeslider(
        fig, 
        session_infos,
        yaxis_column_name,
        show_markers=True
    ):
    df_minmax = session_infos['df_minmax']
    time_infos = session_infos['time_infos']

    fig.add_trace(
        go.Scatter(
            x=df_minmax[time_infos['time_attribute']].to_numpy(), 
            y=df_minmax[yaxis_column_name].to_numpy(),
            mode="lines",
            marker = {
                'color': NON_ANALYSED_COLOR
            }
        )
    )
    
    if show_markers:
        marker_args = {
            'opacity': 1,
            'color': NON_ANALYSED_COLOR,
            'line_width': 0,
            'size': 5
        }
        scatter_utils.add_basic_scatter(fig, session_infos, time_infos['time_attribute'], yaxis_column_name, marker_args=marker_args)

def update_rangeslider_layout(fig, session_infos, yaxis_column_name, show_cuts, custom_xrange=None, custom_yrange=None):
    ti = session_infos['time_infos']
    index = ti['current_time_period']
    date_min = ti['time_periods_list'][index]
    date_max = ti['time_periods_list'][index+1]
    yattr_min, yattr_max = session_infos['user_columns'][yaxis_column_name].get_minmax(auto_margin=True)

    if show_cuts:
        for ts in ti['time_periods_list']:
            fig.add_trace(
                go.Scatter(
                    x=[ts,ts], 
                    y=[yattr_min, yattr_max], 
                    mode='lines', 
                    line=dict(color='rgba(0,0,0,0.2)', width=3),
                    name='selection'
                )
            )

    fig.update_layout(
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[date_min, date_min,date_max,date_max], 
            y=[yattr_min,yattr_max,yattr_max,yattr_min],
            fill='toself', 
            fillcolor='rgba(0,128,0,0.1)',
            line={
                'width': 0
            },
            mode='lines',
            name='selection'
        )
    )
    fig_data = list(fig.data)
    fig_data.insert(0, fig_data[-1] )
    fig_data.pop(-1)
    fig.data = tuple(fig_data)
    
    # updating minmax layout
    margin = (date_max-date_min)*0.05
    xrange = [date_min-margin, date_max+margin] if custom_xrange is None else custom_xrange
    yrange = [yattr_min, yattr_max] if custom_yrange is None else custom_yrange
    fig.update_xaxes(range=xrange)
    fig.update_yaxes(range=yrange)

    fig.update_layout(
        margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, 
        hovermode='closest', 
        height = 650,
        showlegend=False,
        barmode='stack',
        xaxis_title=ti['time_attribute'],
        yaxis_title=yaxis_column_name
    )