import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate


import multiprocessing as mp

from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.viz.indicator_utils as indicator_utils
from utils.fastg3_utils import make_analysis

def register_callbacks(plogger):
    logger = plogger

    # Callback for data update and calculations ()
    @dash.callback(
        [Output('loading_screen','fullscreen'),
        Output('alert-timeout', 'is_open'),
        Output('data-analysed', 'children'),
        Output('learnability_indicator', 'figure'),
        Output('g2_indicator', 'figure'),
        Output('g1_indicator', 'figure'),
        Output('ntuples_involved', 'children'),
        Output('mode', 'disabled'),
        Output('view', 'disabled'),
        Output('select-infos-after-analysis', 'style')],
        [Input('data-loaded','children'),
        Input('analyse_btn','n_clicks')],
        [State('left-attrs','value'),
        State('right-attrs','value'),
        State('thresold_table_features', 'data'),
        State('thresold_table_target', 'data'),
        State('g3_computation','value'),
        State('learnability_indicator', 'figure'),
        State('g2_indicator', 'figure'),
        State('g1_indicator', 'figure'),
        State('ntuples_involved', 'children'),
        State('session-id', 'children')]
    )
    def handle_analysis(data_updated, n_clicks, left_attrs, right_attrs, left_tols, right_tols, g3_computation, learnability_indicator, g2_indicator, g1_indicator, ncountexample_indicator, session_id):
        logger.debug("handle_analysis callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        is_open = False

        dh=session_data['data_holder']
        if dh is not None:
            df = dh["data"]

            # API Calculations if requested
            if changed_id=='analyse_btn.n_clicks' and left_attrs and right_attrs:
                # Init calc df
                df_calc = df.copy()
                n_tuples = len(df_calc.index)
                df_calc[G12_COLUMN_NAME] = 0
                df_calc[G3_COLUMN_NAME] = 0                
                
                # Setting left and right tolerances
                xparams=data_utils.parse_attributes_settings(left_tols, dh['user_columns'])
                yparams=data_utils.parse_attributes_settings(right_tols, dh['user_columns'])

                # Making analysis
                manager = mp.Manager()
                return_dict = manager.dict()
                process = mp.Process(target=make_analysis, args=(df, xparams, yparams, g3_computation=="exact", return_dict,))
                process.daemon = True
                process.start()
                if constants.RESOURCE_LIMITED: 
                    process.join(VPE_TIMEOUT)
                    if process.is_alive():
                        process.terminate()
                        return [dash.no_update, True]+[dash.no_update]*7
                else: 
                    process.join()

                vps = return_dict["vps"]
                dh["graph"] = return_dict["vps_al"]
                involved_tuples = np.unique(np.array(vps))

                # Creating figures
                if involved_tuples is not None:
                    df_calc[G12_COLUMN_NAME][involved_tuples] = 1
                    # Computing G1, G2
                    ncounterexample = involved_tuples.size
                    ncounterexample_fig = f"({ncounterexample} tuples over {n_tuples} are involved in at least one counterexample)"
                    inv_g1, inv_g1_prefix = 100*(1-len(vps)/n_tuples**2), ''
                    if inv_g1>99.99 and inv_g1<100:
                        inv_g1, inv_g1_prefix = 99.99, '>'
                    g1_fig=indicator_utils.bullet_indicator(value=inv_g1, reference=g1_indicator['data'][0]['value'], prefix=inv_g1_prefix)
                    g2 = ncounterexample/n_tuples
                    g2_fig=indicator_utils.bullet_indicator(value=(1-g2)*100, reference=g2_indicator['data'][0]['value'])
                    # Computing G3
                    if g3_computation=="exact": 
                        cover = return_dict["g3_exact_cover"]
                        g3 = len(cover)/n_tuples
                        if not g3 is None:
                            accuracy_ub = 1-g3
                            g3_indicator = indicator_utils.gauge_indicator(value=accuracy_ub*100, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                        else:
                            is_open=True
                            g3_indicator = indicator_utils.gauge_indicator(value=0, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                    else:
                        cover = return_dict["g3_ub_cover"]
                        g3_up = len(cover)/n_tuples
                        g3_lb = return_dict["g3_lb"]
                        lb_acc, ub_acc = (1-g3_up)*100, (1-g3_lb)*100
                        g3_indicator = indicator_utils.gauge_indicator(value=(lb_acc+ub_acc)*0.5, reference=learnability_indicator['data'][0]['value'], lower_bound=lb_acc, upper_bound=ub_acc)

                    # Merging
                    df_calc[G3_COLUMN_NAME][cover] = 1
                    dh["data"]=df_calc
                    dh["X"]=list(xparams.keys())
                    dh["Y"]=list(yparams.keys())
                    overwrite_session_data_holder(session_id, dh)
                    overwrite_session_graphs(session_id)
                    overwrite_session_selected_point(session_id)
                    return True, is_open, "True", g3_indicator, g2_fig, g1_fig, ncounterexample_fig, False, False, {}
                else:
                    is_open=True
            return True, is_open, "False", dash.no_update, dash.no_update, dash.no_update, " ", True, True, {'visibility' : 'hidden'}
        else:
            raise PreventUpdate

    @dash.callback(
        [Output('collapse-viz', 'is_open'),
        Output('collapse-stats', 'is_open'),
        Output('collapse-ceviz', 'is_open'),
        Output('collapse-legend', 'is_open')],
        [Input('data-loaded','children'),
        Input('data-analysed','children')]
    )
    def update_collapses(data_loaded, data_analysed):
        logger.debug("update_collapses callback")

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id == 'data-loaded.children':
            return True, False, False, False
        else:
            return True, True, True, True

    @dash.callback(
        Output('data_filters_have_changed', 'children'),
        [Input({'type': 'minmax_changed', 'index': ALL}, 'children'),
        Input('current-time-range', 'children')],
        [State('session-id', 'children')]
    )
    def data_filters_changed(minmax_changed, time_changed, session_id):
        logger.debug("data_filters_changed callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate        

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        dh = session_data['data_holder']
        if dh is not None:
            time_infos = dh['time_infos']
            filtered_df = dh['full_data']

            # the current time range may have already bin calculated in the past
            if 'current-time-range' in changed_id:
                if time_infos is not None: #shouldn't be none but who knows...
                    curr_index = time_infos['current_time_period']
                    if time_infos['computation_cache'][curr_index] is not None:
                        dh['data'] = time_infos['computation_cache'][curr_index]
                        overwrite_session_data_holder(session_id, dh)
                        return ""

            
            # if minmax changes, we need to reset all the computation cache
            if 'minmax_changed' in changed_id and time_infos is not None:
                time_infos['computation_cache']=[None]*(len(time_infos['time_periods_list'])-1)

            # minmax filtering
            query_lines = []
            for (attr_name, attr) in dh['user_columns'].items():
                if attr.is_numerical():
                    attr_range = attr.get_minmax()
                    query_lines.append(f'{attr_range[0]} <= `{attr_name}` <= {attr_range[1]}')
            query = " and ".join(query_lines)
            filtered_df = dh['full_data'].query(query)

            # applying time filters
            time_infos = dh['time_infos']
            if time_infos is not None:
                curr_index = time_infos["current_time_period"]
                periods_list = time_infos['time_periods_list']
                period_min, period_max = periods_list[curr_index], periods_list[curr_index+1]
                period_min64, period_max64 = period_min.to_datetime64().view("int64"), period_max.to_datetime64().view("int64")
                filtered_df=filtered_df.loc[period_min64:period_max64]                

            dh['data'] = filtered_df
            overwrite_session_data_holder(session_id, dh)
            return ""
        else:
            raise PreventUpdate       


    # ==========================================================
    # ================= Time related callbacks =================
    # ==========================================================
    @dash.callback(
        Output('time-attribute-dropdown', 'options'),
        [Input('data-loaded','children')],
        [State('session-id', 'children')]
    )
    def handle_time_attribute_options(data_loaded, session_id):
        logger.debug("handle_time_attribute_options callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data['data_holder']
        if dh is not None:
            time_cols_options = [{'label': 'No attribute selected', 'value': 'noattradesit'}]
            for (attr_name, attr) in dh['user_columns'].items():
                if attr.is_datetime(): time_cols_options.append({'label': attr_name, 'value': attr_name})
            return time_cols_options
        else:
            raise PreventUpdate

    @dash.callback(
        [Output('time-period-dropdown', 'options'),
        Output('time-range', 'children')],
        [Input('time-attribute-dropdown', 'value')],
        [State('session-id', 'children')]
    )
    def handle_time_period_options(time_attribute, session_id):
        logger.debug("handle_time_attribute_options callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh = session_data['data_holder']
        if dh is not None:
            df = dh['full_data']
            period_options = [{'label': 'Don\'t group', 'value': 'nogroup'}]
            if(time_attribute=='noattradesit'):
                df.index = df[ADESIT_INDEX]
                df = df.sort_index()
                dh["data"] = df
                dh['full_data'] = df
                overwrite_session_data_holder(session_id, dh)
                return period_options, "Attribute period: N/A"
            else:
                # setting time as index
                df.index = pd.to_datetime(df[time_attribute], infer_datetime_format=True)#.astype("datetime64[ns]").astype("int64")
                df = df.sort_index()

                # finding max and min time and delttas
                time_min, time_max = df.index.min(), df.index.max()
                diff = df.index[1:]-df.index[:-1]
                min_delta, max_delta = min(diff), max(diff)

                for time_cut in DEFAULT_TIME_CUTS:
                    td = DEFAULT_TIME_CUTS[time_cut]["timedelta"]
                    if td>=10*min_delta:
                        period_options.append({'label': time_cut, 'value': time_cut})

                # saving data
                df.index = df.index.astype("datetime64[ns]").view("int64")
                df = df.sort_index()
                dh["data"] = df
                dh['full_data'] = df
                overwrite_session_data_holder(session_id, dh)

                return period_options, f'{time_min} → {time_max}'
        else:
            raise PreventUpdate

    @dash.callback(
        [Output("current-time-range", "children"),
        Output('current-time-range-number', 'children'),
        Output('max-time-range-number', 'children')],
        [Input('time-period-dropdown', 'value'),
        Input('time-backward-button', 'n_clicks'),
        Input('time-forward-button', 'n_clicks')],
        [State('session-id', 'children')]
    )
    def handle_time_period_value(time_period_value, bf_nclicks, bb_nclicks, session_id):
        logger.debug("handle_time_period_value callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        dh = session_data['data_holder']
        if dh is not None:
            time_infos = dh['time_infos']
            if "n_clicks" in changed_id:
                curr_index = time_infos["current_time_period"]
                dh['time_infos']["computation_cache"][curr_index]=dh['data']
                periods_list = time_infos['time_periods_list']
                if changed_id=='time-backward-button.n_clicks' and curr_index>0:
                    curr_index-=1 
                elif changed_id=='time-forward-button.n_clicks' and curr_index<len(periods_list)-2:
                    curr_index+=1 
                period_min, period_max = periods_list[curr_index], periods_list[curr_index+1]
                dh['time_infos']["current_time_period"]=curr_index
            else:
                if time_period_value=="nogroup":
                    dh['time_infos'] = None
                    overwrite_session_data_holder(session_id, dh)
                    return f'N/A', "1", "1"
                else:
                    df = dh['full_data']
                    time_min, time_max = df.index.min(), df.index.max()
                    freq=DEFAULT_TIME_CUTS[time_period_value]["freq_symbol"]
                    list = pd.date_range(time_min, time_max, freq=freq)
                    period_min, period_max = list[0], list[1]
                    dh['time_infos']= {
                        'time_periods_list': list,
                        'current_time_period': 0,
                        'date_format': DEFAULT_TIME_CUTS[time_period_value]["date_format"],
                        'computation_cache': [None]*(len(list)-1)
                    }
            overwrite_session_data_holder(session_id, dh)
            time_infos = dh['time_infos']
            n_periods = len(time_infos['time_periods_list'])-1
            date_format = time_infos["date_format"]
            curr_index = time_infos["current_time_period"]
            return f'{data_utils.format_date_period(period_min, period_max, date_format)}', curr_index+1, n_periods
        else:
            raise PreventUpdate

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