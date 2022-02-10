import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

from utils.cache_utils import *
from constants import *
import utils.viz.rangeslider_utils  as rangeslider_utils

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
        Input('data_updated', 'children'),
        Input('selection_changed', 'children')],
        [State('session-id', 'children')]
    )
    def time_trace_graph(yaxis_name, data_updated, selection_changed, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_graph callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        #https://plotly.com/python/range-slider/
        dh=session_data['data_holder']
        if dh is not None and dh['df_minmax'] is not None:
            ti = dh['time_infos']
            time_attribute = dh['time_infos']['time_attribute']
            if time_attribute is not None:
                fig = go.Figure()
                fig = rangeslider_utils.add_basic_rangeslider(fig, dh, yaxis_name)
                fig = rangeslider_utils.update_rangeslider_layout(fig, dh, yaxis_name)
                return fig
            else:
                return go.Figure()
        else:
            raise PreventUpdate