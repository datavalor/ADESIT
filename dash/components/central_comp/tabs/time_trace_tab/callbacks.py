import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

from utils.cache_utils import *
from constants import *

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        [Output('timetrace-yaxis-dropdown', 'options'),
        Output('timetrace-yaxis-dropdown', 'value')],
        [Input('time-period-dropdown', 'value')],
        [State('session-id', 'children')]
    )
    def time_trace_yaxis_dropdown_options(time_attribute, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_yaxis_dropdown_options callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh=session_data['data_holder']
        if dh is not None:
            options = []
            time_attribute = dh['time_infos']['time_attribute']
            if time_attribute is not None:
                for attr_name, attr in dh['user_columns'].items():
                    if not attr.is_datetime():
                        options.append({'label': attr_name, 'value': attr_name})
                if options:
                    return options, options[0]['value']
                else:
                    raise PreventUpdate
            else:
                raise PreventUpdate

        else:
            raise PreventUpdate


    @dash.callback(
        Output('time_trace_graph', 'figure'),
        [Input('timetrace-yaxis-dropdown', 'value'),
        Input('data_filters_have_changed', 'children'),],
        [State('session-id', 'children')]
    )
    def time_trace_graph(yaxis_name, data_updated, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_graph callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        #https://plotly.com/python/range-slider/
        dh=session_data['data_holder']
        if dh is not None and dh['df_minmax'] is not None:
            time_attribute = dh['time_infos']['time_attribute']
            if time_attribute is not None:
                df_minmax = dh['df_minmax']
                fig = go.Figure()
                fig.add_trace(
                    go.Scatter(
                        x=df_minmax[time_attribute].to_numpy(), 
                        y=df_minmax[yaxis_name].to_numpy(),
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
                        type="date"
                    )
                )
                fig.update_layout(
                    margin={'l': 60, 'b': 50, 't': 10, 'r': 30}, 
                    hovermode='closest', 
                    height = 650,
                    showlegend=False,
                    barmode='stack',
                    xaxis_title=time_attribute,
                    yaxis_title=yaxis_name
                )
                return fig
            else:
                return go.Figure()
        else:
            raise PreventUpdate