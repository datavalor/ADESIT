import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

from utils.cache_utils import *

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        Output('time_trace_graph', 'figure'),
        [Input('time-attribute-dropdown', 'value')],
        [State('session-id', 'children')]
    )
    def time_trace_graph(time_attribute, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_graph callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        #https://plotly.com/python/range-slider/
        dh=session_data['data_holder']
        if dh is not None:
            return {}
        else:
            raise PreventUpdate