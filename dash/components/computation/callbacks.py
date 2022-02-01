import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate


from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.indicator_utils as indicator_utils

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

        dh=session_data["data_holder"]
        if dh is not None:
            df = dh["data"]
            ctypes = dh["columns_type"]
            # API Calculations if requested
            if changed_id=='analyse_btn.n_clicks' and left_attrs and right_attrs:
                # Init calc df
                df_calc = df.copy()
                n_tuples = len(df_calc.index)
                df_calc[G12_COLUMN_NAME] = 0
                df_calc[G3_COLUMN_NAME] = 0                
                
                # Setting left and right tolerances
                xparams=data_utils.parse_attributes_settings(left_tols, ctypes)
                yparams=data_utils.parse_attributes_settings(right_tols, ctypes)

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