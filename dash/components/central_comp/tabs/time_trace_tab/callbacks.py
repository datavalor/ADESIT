import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

from utils.cache_utils import *
from constants import *
import utils.viz.rangeslider_utils  as rangeslider_utils
import utils.viz.scatter_utils as scatter_utils

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
        Input('selection_changed', 'children'),
        Input('time-trace-viz-switches', 'value'),
        Input('time-trace-center-button', 'n_clicks')],
        [State('time_trace_graph', 'figure'),
        State('session-id', 'children')]
    )
    def time_trace_graph(yaxis_name, data_updated, selection_changed, viz_switches, center_on_period, time_trace_fig, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_graph callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        #https://plotly.com/python/range-slider/
        dh=session_data['data_holder']
        if dh is not None and dh['df_minmax'] is not None:
            time_attribute = dh['time_infos']['time_attribute']
            if time_attribute is not None:
                if changed_id not in ['selection_changed.children', 'time-trace-viz-switches.value', 'time-trace-center-button.n_clicks']:
                    fig = rangeslider_utils.add_basic_rangeslider(go.Figure(), dh, yaxis_name)
                    update_minmax = True
                else:
                    del time_trace_fig['layout']['xaxis']['rangeslider']
                    del time_trace_fig['layout']['template']
                    fig = go.Figure(time_trace_fig)
                    update_minmax = True
                update_minmax = (1 in viz_switches)
                if changed_id == 'time-trace-viz-switches.value': update_minmax=False
                if changed_id == 'time-trace-center-button.n_clicks': update_minmax=True
                rangeslider_utils.add_selection_to_rangeslider(
                    fig, 
                    dh, 
                    get_data(session_id)["selection_infos"],
                    time_attribute,
                    yaxis_name
                )
                print(changed_id, update_minmax)
                fig = rangeslider_utils.update_rangeslider_layout(fig, dh, yaxis_name, show_cuts=(0 in viz_switches), update_minmax=update_minmax)
                return fig
            else:
                return go.Figure()
        else:
            raise PreventUpdate