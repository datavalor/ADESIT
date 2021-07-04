import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 
import numpy as np

# Personnal imports
import fastg3.crisp as g3crisp
import fastg3.ncrisp as g3ncrisp
import figure_generator as fig_gen
from utils.data_utils import parse_attributes_settings, num_or_cat
from utils.cache_utils import *
from callbacks.constants import *

def register_fd_settings_callbacks(app, plogger):
    logger = plogger

    # Callback for Dimensions (attribute) options in dropdowns (b->c,d,f)
    @app.callback([Output('right-attrs', 'options'),
                Output('left-attrs', 'options'),
                Output('right-attrs', 'value'),
                Output('left-attrs', 'value')],
                [Input('data-loaded','children')],
                [State('session-id', 'children')])
    def update_options(data_loaded, session_id):
        logger.debug("update_options")
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            df_parsed=dh["data"]
            options=[{'label': str(col), 'title' : str(df_parsed.dtypes[str(col)]) ,'value': str(col)} for col in df_parsed.columns]
            return options, options, None, None
        else:
            return [], [], None, None

        # Callback for Left Tolerances Output ()
    @app.callback([Output('thresold_table_features', 'data'),
                Output('thresold_table_target', 'data')],
                [Input('data-loaded','children'),
                Input('left-attrs','value'),
                Input('right-attrs','value')],
                [State('thresold_table_features', 'data'),
                State('thresold_table_target', 'data'),
                State('session-id', 'children')])
    def handle_thresolds(data_loaded, left_attrs, right_attrs, fthresolds, tthresolds, session_id):
        logger.debug("handle_thresolds callback")

        # Detect which attributes changed
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id=='data-loaded.children': return [], []
        if changed_id=='left-attrs.value': inputtols,inputattr=fthresolds,left_attrs
        else: inputtols, inputattr=tthresolds, right_attrs

        # Update tolerances
        dh=get_data(session_id)["data_holder"]
        if inputattr is not None and dh is not None:
            df=dh["data"]

            # Retrieve previous settings
            new_attributes_settings = parse_attributes_settings(inputtols, df)
            attributes_settings = get_data(session_id)["thresolds_settings"]
            if new_attributes_settings is not None:
                for attr in new_attributes_settings.keys(): attributes_settings[attr] = new_attributes_settings[attr]
                overwrite_session_thresolds_settings(session_id, attributes_settings)            
            
            outuput_thresolds = []
            for attr in inputattr:
                attr_type = num_or_cat(attr, df)
                if attr_type is not None:
                    if attr_type == "categorical":
                        outuput_thresolds.append({'attribute': attr, 'absolute': 'is', 'relative': 'categorical...'})
                    elif attr_type == "numerical":
                        outuput_thresolds.append({'attribute': attr, 
                            'absolute': attributes_settings.get(attr, {"params":[0,0]})["params"][0], 
                            'relative': attributes_settings.get(attr, {"params":[0,0]})["params"][1]
                        })
            
            if changed_id=='left-attrs.value': return outuput_thresolds, tthresolds
            else: return fthresolds, outuput_thresolds
        else:
            if changed_id=='left-attrs.value': return [], tthresolds
            else: return fthresolds, []


    # Callback for Analyse button state
    @app.callback([Output('analyse_btn', 'disabled'),
                Output('g3_computation', 'disabled')],
                [Input('left-attrs','value'),
                Input('right-attrs','value')])
    def handle_analyse_btn_state(left_attrs, right_attrs):
        logger.debug("analyse_btn_state callback")
        if left_attrs and right_attrs: return False, False
        else: return True, True

    # Callback for data update and calculations ()
    @app.callback([Output('loading_screen','fullscreen'),
                Output('alert-timeout', 'is_open'),
                Output('data-analysed', 'children'),
                Output('learnability_indicator', 'figure'),
                Output('g2_indicator', 'figure'),
                Output('g1_indicator', 'figure'),
                Output('ntuples_involved', 'children'),
                Output('collapse-stats', 'is_open'),
                Output('mode', 'disabled'),
                Output('view', 'disabled')],
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
                State('session-id', 'children')])
    def handle_analysis(data_updated, n_clicks, left_attrs, right_attrs, left_tols, right_tols, g3_computation, learnability_indicator, g2_indicator, g1_indicator, ncountexample_indicator, session_id):
        logger.debug("handle_analysis callback")
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        is_open = False
        dh=get_data(session_id)["data_holder"]
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
                xparams=parse_attributes_settings(left_tols, df)
                yparams=parse_attributes_settings(right_tols, df)

                # Setting up solver
                VPE = g3ncrisp.create_vpe_instance(
                    df, 
                    xparams, 
                    yparams,
                    verbose=False
                )
                rg3 = g3ncrisp.RSolver(VPE, precompute=True)

                # Enumerating violating pairs
                vps = rg3.get_vps()
                dh["graph"] = rg3.get_vps(as_map=True)

                involved_tuples = np.unique(np.array(vps))

                # Creating figures
                if involved_tuples is not None:
                    df_calc[G12_COLUMN_NAME][involved_tuples] = 1
                    # Computing G1, G2
                    ncounterexample = involved_tuples.size
                    ncounterexample_fig = f"({ncounterexample} tuples over {n_tuples} are involved in at least one counterexample)"
                    g1 = round(len(vps)/n_tuples**2,4)
                    g1_fig=fig_gen.bullet_indicator(value=(1-g1)*100, reference=g1_indicator['data'][0]['value'])
                    g2 = round(ncounterexample/n_tuples, 4)
                    g2_fig=fig_gen.bullet_indicator(value=(1-g2)*100, reference=g2_indicator['data'][0]['value'])
                    # Computing G3
                    if g3_computation=="exact": 
                        cover = rg3.exact(method="wgyc", return_cover=True)
                        g3 = len(cover)/n_tuples
                        if not g3 is None:
                            accuracy_ub = 1-g3
                            g3_indicator = fig_gen.gauge_indicator(value=accuracy_ub*100, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                        else:
                            is_open=True
                            g3_indicator = fig_gen.gauge_indicator(value=0, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                    else:
                        gic, approx2 = rg3.upper_bound(method="gic", return_cover=True), rg3.upper_bound(method="2approx", return_cover=True)
                        cover = gic if len(gic)<len(approx2) else approx2
                        g3_up = len(cover)/n_tuples
                        g3_lb = rg3.lower_bound(method="maxmatch")
                        lb_acc, ub_acc = (1-g3_up)*100, (1-g3_lb)*100
                        g3_indicator = fig_gen.gauge_indicator(value=(lb_acc+ub_acc)*0.5, reference=learnability_indicator['data'][0]['value'], lower_bound=lb_acc, upper_bound=ub_acc)

                    # Merging
                    df_calc[G3_COLUMN_NAME][cover] = 1
                    dh["data"]=df_calc
                    overwrite_session_data_holder(session_id, dh)
                    overwrite_session_graphs(session_id)
                    overwrite_session_selected_point(session_id)
                    return True, is_open, "Done", g3_indicator, g2_fig, g1_fig, ncounterexample_fig, True, False, False
                else:
                    is_open=True
            overwrite_session_data_holder(session_id, dh)
            overwrite_session_graphs(session_id)
            default_g3 = fig_gen.gauge_indicator(reference=learnability_indicator['data'][0]['value'])
            default_g2 = fig_gen.bullet_indicator(reference=g2_indicator['data'][0]['value'])
            default_g1 = fig_gen.bullet_indicator(reference=g1_indicator['data'][0]['value'])
            default_ncounterexample = ""
            overwrite_session_selected_point(session_id)
            return True, is_open, "Done", default_g3, default_g2, default_g1, default_ncounterexample, False, True, True
        else:
            raise PreventUpdate