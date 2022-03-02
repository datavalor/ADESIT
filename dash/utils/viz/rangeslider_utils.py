import plotly.graph_objects as go
from pyparsing import line

from constants import *
import utils.viz.figure_utils as figure_utils
import utils.viz.scatter_utils as scatter_utils

import numpy as np
import pandas as pd

import random

def add_basic_rangeslider(
        fig, 
        session_infos,
        yaxis_column_name,
        show_markers=True,
        show_analysed_colors=True
):
    time_infos = session_infos['time_infos']
    time_attribute = time_infos['time_attribute']

    dfs  = []
    g3s, g3s_dates = [], []
    for i in range(len(time_infos['computation_cache'])):
        period_df = time_infos['computation_cache'][i]['df']
        if len(period_df.index)>0:
            dfs.append(period_df)
            indicators_dict = time_infos['computation_cache'][i]['indicators']
            if indicators_dict is not None:
                mean_period_date = period_df.iloc[0][time_attribute]+(period_df.iloc[-1][time_attribute]-period_df.iloc[0][time_attribute])/2
                g3s_dates.append(mean_period_date)
                if indicators_dict['g3_computation']=='exact':
                    g3s.append(indicators_dict['g3'])
                else:
                    g3_lb, g3_up = indicators_dict['g3']
                    g3s.append((g3_lb+g3_up)/2)
    df = pd.concat(dfs)


    if G12_COLUMN_NAME in df.columns and show_analysed_colors:
        t = df[G12_COLUMN_NAME].copy()
        involved_truth_table = (t==1)
        transition_truth_table = ((2*t-t.shift(1)-t.shift(-1)).fillna(0)==0)
        involved_col, free_col, transition_col = df[yaxis_column_name].copy(), df[yaxis_column_name].copy(), df[yaxis_column_name].copy()
        involved_col[~involved_truth_table] = np.nan
        free_col[involved_truth_table] = np.nan
        transition_col[transition_truth_table] = np.nan
        to_plot = [(CE_COLOR, involved_col), (FREE_COLOR, free_col), (MEDIUM_COLOR, transition_col)]
    else:
        to_plot = [(NON_ANALYSED_COLOR, df[yaxis_column_name])]

    for plot in to_plot:
        fig.add_trace(
            go.Scatter(
                mode='lines',
                x=df[time_attribute].to_numpy(), 
                y=plot[1],
                line = {
                    'color': plot[0],
                    'width': 2
                },
                yaxis='y'
            )
        )

    if g3s:
        fig.add_trace(
            go.Scatter(
                x=g3s_dates, 
                y=g3s,
                mode='markers+lines',
                line = {
                    'color': SELECTED_NON_ANALYSED_COLOR,
                    'width': 2
                },
                yaxis='y2'
            )
        )
    
    if show_markers:
        if G12_COLUMN_NAME in df.columns:
            free_marker_args = {
                'opacity': 1,
                'color': FREE_COLOR,
                'line_width': 0,
                'size': 5
            }
            prob_marker_args = {
                'opacity': 1,
                'color': CE_COLOR,
                'line_width': 0,
                'symbol': 'cross',
                'size': 5
            }
            prob = df[df[G12_COLUMN_NAME]==1]
            free = df[df[G12_COLUMN_NAME]==0]
            scatter_utils.add_basic_scatter(fig, session_infos, time_infos['time_attribute'], yaxis_column_name, marker_args=free_marker_args, df=free)
            scatter_utils.add_basic_scatter(fig, session_infos, time_infos['time_attribute'], yaxis_column_name, marker_args=prob_marker_args, df=prob)
        else:
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
    if session_infos['data']['df_free'] is not None:
        fig.update_layout(
            yaxis=dict(
                anchor="x",
                autorange=True,
                domain=[0, 0.8],
                linecolor="#000000",
                showline=True,
                tickmode="auto",
                titlefont={"color": "#000000"},
                zeroline=True
            ),
            yaxis2=dict(
                anchor="x",
                autorange=True,
                domain=[0.8, 1],
                linecolor=SELECTED_NON_ANALYSED_COLOR,
                showline=True,
                tickfont={"color": SELECTED_NON_ANALYSED_COLOR},
                tickmode="auto",
                title="g3",
                titlefont={"color": SELECTED_NON_ANALYSED_COLOR},
                type="linear",
                zeroline=True
            ),
        )