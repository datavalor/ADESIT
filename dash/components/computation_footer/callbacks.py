import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate


import multiprocessing as mp

from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.fastg3_utils as fastg3_utils

def register_callbacks(plogger):
    logger = plogger

    def choose_g3_computation_method(g3_computation, dataset_size):
        if g3_computation == 'auto':
            if dataset_size>4000: g3_computation='approx'
            else: g3_computation='exact'
        return g3_computation


    # Callback for data update and calculations ()
    @dash.callback(
        [
            Output('alert-timeout', 'is_open'),
            Output('data-analysed-prop', 'children'),
            Output('mode', 'disabled'),
            Output('view', 'disabled'),
            Output('select-infos-after-analysis', 'style')
        ],
        [
            Input('analyse_btn','n_clicks')
        ],
        [
            State('left-attrs','value'),
            State('right-attrs','value'),
            State('thresold_table_features', 'data'),
            State('thresold_table_target', 'data'),
            State('g3_computation','value'),
            State('session-id', 'children')
        ]
    )
    def handle_analysis(n_clicks, left_attrs, right_attrs, left_tols, right_tols, g3_computation, session_id):
        logger.debug("handle_analysis callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        is_open = False

        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate

        # API Calculations if requested
        if not left_attrs or not right_attrs: 
            return is_open, dash.no_update, True, True, {'visibility' : 'hidden'}

        # Setting left and right tolerances
        xparams=data_utils.parse_attributes_settings(left_tols, dh['user_columns'])
        yparams=data_utils.parse_attributes_settings(right_tols, dh['user_columns'])

        time_infos = dh['time_infos']
        if time_infos['time_attribute'] is not None:
            for i in range(len(time_infos['computation_cache'])):
                curr_df = dh['time_infos']['computation_cache'][i]['df']
                n_tuples = len(curr_df.index)
                dh['time_infos']['computation_cache'][i] = fastg3_utils.make_analysis(
                    curr_df, 
                    xparams, 
                    yparams, 
                    choose_g3_computation_method(g3_computation, n_tuples)
                )
            data = time_infos['computation_cache'][time_infos['current_time_period']]
        else:
            data = fastg3_utils.make_analysis(dh['data']['df'], xparams, yparams, choose_g3_computation_method(g3_computation, len(dh['data']['df'].index)))

        if data is None: 
            return [True]+[dash.no_update]*4

        dh['X'], dh['Y'] = list(xparams.keys()), list(yparams.keys())
        dh['data'] = data
        overwrite_session_data_holder(session_id, dh, source='handle_analysis')
        return is_open, '', False, False, {}
        

    @dash.callback(
        [Output('bottom-fixed-computation', 'style'),
        Output('collapse-viz', 'is_open'),
        Output('collapse-indicators', 'style'),
        Output('collapse-ceviz', 'is_open'),
        Output('collapse-legend', 'is_open')],
        [Input('data-loaded','children'),
        Input('data-analysed-prop','children')],
        [State('bottom-fixed-computation', 'style'),
        State('collapse-indicators', 'style')]
    )
    def update_collapses(data_loaded, data_analysed, bottom_style, indicators_stats):
        logger.debug("update_collapses callback")

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id == 'data-loaded.children':
            bottom_style['visibility'] = 'visible'
            indicators_stats['display'] = 'none'
            return bottom_style, True, indicators_stats, True, False
        else:
            del indicators_stats['display']
            return dash.no_update, dash.no_update, indicators_stats, dash.no_update, True

    @dash.callback(
        Output('data_updated', 'children'),
        [
            Input({'type': 'minmax_changed', 'index': ALL}, 'children'),
            Input('time-period-dropdown', 'value'),
            Input('current-time-range', 'children')
        ],
        State('session-id', 'children')
    )
    def update_data(minmax_changed, time_attribute, time_changed, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'update_data callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate        

        dh = session_data['data_holder']
        if dh is not None:
            time_infos = dh['time_infos']

            if 'minmax_changed' in changed_id or dh['df_minmax'] is None:
                if time_infos['time_attribute'] is not None:
                    time_infos['computation_cache']=[None]*(len(time_infos['time_periods_list'])-1)

                # computing minmax
                query_lines = []
                for (attr_name, attr) in dh['user_columns'].items():
                    if attr.is_numerical():
                        attr_range = attr.get_minmax()
                        if attr_range!=attr.get_minmax(original=True):
                            query_lines.append(f'{attr_range[0]} <= `{attr_name}` <= {attr_range[1]}')
                if query_lines:
                    query = " and ".join(query_lines)
                    dh['df_minmax'] = dh['df_full'].query(query)
                else:
                    dh['df_minmax'] = dh['df_full'].copy()

            # applying time filters
            if time_infos['time_attribute'] is not None:
                time_attr, curr_index, periods_list = time_infos['time_attribute'], time_infos['current_time_period'], time_infos['time_periods_list']
                if time_infos['computation_cache'][curr_index] is None:
                    df_minmax = dh['df_minmax']
                    for i in range(len(periods_list)-1):
                        period_min, period_max = periods_list[i], periods_list[i+1]
                        time_infos['computation_cache'][i] = default_data.copy()
                        time_infos['computation_cache'][i]['df'] = df_minmax.loc[(df_minmax[time_attr]>period_min) & (df_minmax[time_attr]<period_max)]
                data = time_infos['computation_cache'][curr_index]
            else:
                data = default_data.copy()
                data['df'] = dh['df_minmax'].copy()

            dh['data'] = data
            dh['time_infos'] = time_infos
            overwrite_session_data_holder(session_id, dh, source='update_data')
            return ""
        else:
            raise PreventUpdate       


    # ==========================================================
    # ================= Time related callbacks =================
    # ==========================================================
    @dash.callback(
        [
            Output('time-attribute-dropdown', 'options'),
            Output('time-attribute-dropdown', 'value')
        ],
        Input('data-loaded','children'),
        State('session-id', 'children')
    )
    def handle_time_attribute_options(data_loaded, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'handle_time_attribute_options callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data['data_holder']
        if dh is not None:
            time_cols_options = [{'label': 'No attribute selected', 'value': 'noattradesit'}]
            for (attr_name, attr) in dh['user_columns'].items():
                if attr.is_datetime(): time_cols_options.append({'label': attr_name, 'value': attr_name})
            return time_cols_options, 'noattradesit'
        else:
            raise PreventUpdate

    @dash.callback(
        [
            Output('time-period-dropdown', 'options'),
            Output('time-period-dropdown', 'value'),
            Output('time-range', 'children'),
            Output('timetrace-tab', 'disabled')
        ],
        Input('time-attribute-dropdown', 'value'),
        State('session-id', 'children')
    )
    def handle_time_period_options(time_attribute, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'handle_time_period_options callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh = session_data['data_holder']
        if dh is None: raise PreventUpdate

        period_options = [{'label': 'Full period', 'value': 'nogroup'}]
        if time_attribute=='noattradesit':
            dh['df_full'] = dh['df_full'].sort_values(by=[ADESIT_INDEX])
            dh['df_minmax'] = None
            dh['data'] = default_data
            dh['time_infos'] = default_time_infos
            overwrite_session_data_holder(session_id, dh, source='handle_time_period_options1')

            return period_options, 'nogroup', "Attribute period: N/A", True
        else:
            # finding max and min time and delttas
            df = dh['df_full'].sort_values(by=time_attribute)
            time_min, time_max = df[time_attribute].min(), df[time_attribute].max()
            diff = df[time_attribute][1:]-df[time_attribute][:-1]
            min_delta = min(diff[pd.notnull(diff)])

            # finding viable cuts
            for time_cut in DEFAULT_TIME_CUTS:
                td = DEFAULT_TIME_CUTS[time_cut]['timedelta']
                if td>=10*min_delta:
                    period_options.append({'label': time_cut, 'value': time_cut})

            # storing time attribute and minmax 
            dh['time_infos']['time_attribute'] = time_attribute
            dh['time_infos']['time_minmax'] = [time_min, time_max]

            # saving data
            dh['df_full'] = df
            dh['df_minmax'] = None
            dh['data'] = default_data
            overwrite_session_data_holder(session_id, dh, source='handle_time_period_options2')

            return period_options, 'nogroup', data_utils.format_date_period(time_min, time_max), False

    @dash.callback(
        [
            Output('current-time-range', 'children'),
            Output('current-time-range-number', 'children'),
            Output('max-time-range-number', 'children')
        ],
        [  
            Input('time-period-dropdown', 'value'),
            Input('time-backward-button', 'n_clicks'),
            Input('time-forward-button', 'n_clicks')
        ],
        State('session-id', 'children')
    )
    def handle_time_period_value(time_period_value, bf_nclicks, bb_nclicks, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug(f'handle_time_period_value callback because of {changed_id}')
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        dh = session_data['data_holder']
        if dh is None or dh['time_infos']['time_attribute'] is None: raise PreventUpdate

        time_infos = dh['time_infos']
        if "n_clicks" in changed_id:
            curr_index = time_infos["current_time_period"]
            periods_list = time_infos['time_periods_list']
            if changed_id=='time-backward-button.n_clicks' and curr_index>0: curr_index-=1 
            elif changed_id=='time-forward-button.n_clicks' and curr_index<len(periods_list)-2: curr_index+=1 
            period_min, period_max = periods_list[curr_index], periods_list[curr_index+1]
            dh['time_infos']["current_time_period"]=curr_index
        else:
            if time_period_value=="nogroup":
                list=dh['time_infos']['time_minmax']
                dh['time_infos']['date_format']=None
            else:
                time_min, time_max = dh['time_infos']['time_minmax']
                freq=DEFAULT_TIME_CUTS[time_period_value]['freq_symbol']
                list = pd.date_range(time_min, time_max, freq=freq)
                dh['time_infos']['date_format']=DEFAULT_TIME_CUTS[time_period_value]['date_format']
            period_min, period_max = list[0], list[1]
            dh['time_infos']['time_periods_list']=list
            dh['time_infos']['current_time_period']= 0
            dh['time_infos']['computation_cache']=[None]*(len(list)-1)
            
        overwrite_session_data_holder(session_id, dh, source='handle_time_period_value2')

        time_infos = dh['time_infos']
        n_periods = len(time_infos['time_periods_list'])-1
        date_format = time_infos["date_format"]
        curr_index = time_infos["current_time_period"]
        return data_utils.format_date_period(period_min, period_max, date_format), curr_index+1, n_periods

    @dash.callback(
        [Output('time-backward-button', 'disabled'),
        Output('time-forward-button', 'disabled')],
        [Input('current-time-range', 'children')],
        [State('session-id', 'children')]
    )
    def handle_time_period_buttons_state(current_time_range, session_id):
        logger.debug("handle_time_period_buttons_state callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        time_infos = session_data['data_holder']['time_infos']
        if time_infos is not None:
            list_len = len(time_infos['time_periods_list'])
            curr_index = time_infos["current_time_period"]
            if list_len==2:
                return True, True
            if curr_index==0:
                return True, False
            elif curr_index==list_len-2:
                return False, True
            else:
                return False, False
        else:
            return True, True

    dash.clientside_callback(
        """
        function(value) {
            if(value==='noattradesit'){
                return {'opacity': 0.2};
            } else {
                return {'opacity': 1};
            }
            
        }
        """,
        Output('sub-time-elements', 'style'),
        Input('time-attribute-dropdown', 'value'),
    )