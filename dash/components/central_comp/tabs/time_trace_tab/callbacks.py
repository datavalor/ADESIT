import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

import plotly.graph_objects as go

from utils.cache_utils import *
from constants import *
import utils.viz.rangeslider_utils  as rangeslider_utils
import utils.viz.scatter_utils as scatter_utils
import utils.viz.selection_utils as selection_utils

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        [
            Output('timetrace-yaxis-dropdown', 'options'),
            Output('timetrace-yaxis-dropdown', 'value')
        ],
        Input('time-range', 'children'),
        State('session-id', 'children')
    )
    def time_trace_yaxis_dropdown_options(timerange_children, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_yaxis_dropdown_options callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate

        time_attribute = dh['time_infos']['time_attribute']
        if time_attribute is None: raise PreventUpdate

        options = []
        for attr_name, attr in dh['user_columns'].items():
            if not attr.is_datetime():
                options.append({'label': attr_name, 'value': attr_name})
        if options:
            return options, options[0]['value']
        else:
            raise PreventUpdate


    @dash.callback(
        Output('timetrace-graph', 'figure'),
        [
            Input('data_updated', 'children'),
            Input('selection_changed', 'children'),
            Input('timetrace-yaxis-dropdown', 'value'),
            Input('time-trace-viz-switches', 'value'),
            Input('time-trace-center-button', 'n_clicks')
        ],
        [
            State('timetrace-graph', 'figure'),
            State('session-id', 'children')
        ]
    )
    def time_trace_graph(data_updated, selection_changed, yaxis_name, viz_switches, center_on_period, time_trace_fig, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'time_trace_graph callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        #https://plotly.com/python/range-slider/
        dh=session_data['data_holder']
        if dh is None or dh.get('df_minmax', None) is None: raise PreventUpdate

        time_attribute = dh['time_infos']['time_attribute']
        if time_attribute is None: return go.Figure()
        if yaxis_name is None: raise PreventUpdate


        actions = {
            #[reload_figure, update_minmax]
            'timetrace-yaxis-dropdown.value': [True, False],
            'data_updated.children': [True, (1 in viz_switches)],
            'selection_changed.children': [False, True],
            'time-trace-viz-switches.value': [True, False],
            'time-trace-center-button.n_clicks': [False, True]
        }

        curr_x_range = time_trace_fig['layout']['xaxis']['range']
        curr_y_range = time_trace_fig['layout']['yaxis']['range']

        # reloading figure
        if actions[changed_id][0]:
            rangeslider_utils.add_basic_rangeslider(go.Figure(), dh, yaxis_name, show_markers=(2 in viz_switches))
        else:
            del time_trace_fig['layout']
            fig = go.Figure(time_trace_fig)

        # updating minmax
        if actions[changed_id][1] or not isinstance(curr_x_range[0], str):
            custom_xrange, custom_yrange=None, None
        else:
            custom_xrange, custom_yrange=curr_x_range, None

        # adding selection
        selection_utils.add_selection_as_vertical_lines(
            fig, 
            dh, 
            get_data(session_id)["selection_infos"],
            time_attribute,
            yaxis_name
        )
        rangeslider_utils.update_rangeslider_layout(fig, dh, yaxis_name, show_cuts=(0 in viz_switches), custom_xrange=custom_xrange, custom_yrange=custom_yrange)
        return fig
            