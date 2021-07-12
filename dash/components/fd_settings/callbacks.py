import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 
import numpy as np
import multiprocessing as mp

# Personnal imports
import fastg3.ncrisp as g3ncrisp
import utils.figure_utils as fig_gen
from utils.data_utils import parse_attributes_settings
from utils.cache_utils import *
from utils.resource_utils import timeout
from utils.fastg3_utils import make_analysis
import constants
from constants import *

def register_callbacks(app, plogger):
    logger = plogger

    @app.callback(
        [Output('data-loaded','children'),
        Output('dataset_confirm', 'children'),
        Output('left-attrs', 'disabled'),
        Output('right-attrs', 'disabled'),
        Output('alert-data_not_loaded', 'is_open')],
        [Input('toy-dataset-iris','n_clicks'),
        Input('toy-dataset-housing','n_clicks'),
        Input('toy-dataset-diamonds','n_clicks'),
        Input('toy-dataset-kidney','n_clicks'),
        Input('upload-form', 'contents')],
        [State('upload-form', 'filename'),
        State('session-id', 'children')]
    )
    def handle_data(iris, housing, diamonds, kidney, contents, filename, session_id):
        logger.debug('handle_data callback')
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        clear_session(session_id)
        data=None
        if "toy-dataset" in changed_id:
            toy_dataset = changed_id.split(".")[0].split("-")[-1]
            filename = toy_dataset
            data = get_data(session_id, filename=toy_dataset, pydata=True)
        elif filename is not None: 
            data = get_data(session_id, filename=filename, contents=contents)
        else:
            raise PreventUpdate

        if data is not None:
            dh = data.get("data_holder", None)
            n = len(dh["data"].index) if dh is not None else 0
            return filename, fig_gen.dataset_infos(filename, n, len(dh["data"].columns)), False, False, dash.no_update
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, True
        

    # Callback for Dimensions (attribute) options in dropdowns (b->c,d,f)
    @app.callback(
        [Output('right-attrs', 'options'),
        Output('left-attrs', 'options'),
        Output('right-attrs', 'value'),
        Output('left-attrs', 'value')],
        [Input('data-loaded','children')],
        [State('session-id', 'children')]
    )
    def update_options(data_loaded, session_id):
        logger.debug("update_options  callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh=session_data["data_holder"]
        if dh is not None:
            df_parsed=dh["data"]
            user_cols=dh["user_columns"]
            options=[{'label': str(col), 'title' : str(df_parsed.dtypes[str(col)]), 'value': str(col)} for col in user_cols]
            return options, options, None, None
        else:
            return [], [], None, None

    # Callback for Left Tolerances Output ()
    @app.callback(
        [Output('thresold_table_features', 'data'),
        Output('thresold_table_target', 'data')],
        [Input('data-loaded','children'),
        Input('left-attrs','value'),
        Input('right-attrs','value')],
        [State('thresold_table_features', 'data'),
        State('thresold_table_target', 'data'),
        State('session-id', 'children')]
    )
    def handle_thresolds(data_loaded, left_attrs, right_attrs, fthresolds, tthresolds, session_id):
        logger.debug("handle_thresolds callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        # Detect which attributes changed
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id=='data-loaded.children': return [], []
        if changed_id=='left-attrs.value': inputtols,inputattr=fthresolds,left_attrs
        else: inputtols, inputattr=tthresolds, right_attrs

        # Update tolerances
        dh=session_data["data_holder"]
        if inputattr is not None and dh is not None:
            ctypes = dh["user_columns_type"]

            # Retrieve previous settings
            new_attributes_settings = parse_attributes_settings(inputtols, ctypes)
            attributes_settings = get_data(session_id)["thresolds_settings"]
            if new_attributes_settings is not None:
                for attr in new_attributes_settings.keys(): attributes_settings[attr] = new_attributes_settings[attr]
                overwrite_session_thresolds_settings(session_id, attributes_settings)            
            
            outuput_thresolds = []
            for attr in inputattr:
                attr_type = ctypes[attr]
                if attr_type is not None:
                    if attr_type == "categorical":
                        outuput_thresolds.append({'attribute': attr, 'absolute': 'is', 'relative': 'categorical...'})
                    elif attr_type == "numerical":
                        outuput_thresolds.append({'attribute': attr, 
                            'absolute': attributes_settings.get(attr, {"params":[0,0]})["params"][0], 
                            'relative': attributes_settings.get(attr, {"params":[0,0]})["params"][1]
                        })
            
            if changed_id=='left-attrs.value': return outuput_thresolds, dash.no_update
            else: return dash.no_update, outuput_thresolds
        else:
            if changed_id=='left-attrs.value': return [], dash.no_update
            else: return dash.no_update, []


    # Callback for Analyse button state
    @app.callback(
        [Output('analyse_btn', 'disabled'),
        Output('g3_computation', 'disabled')],
        [Input('left-attrs','value'),
        Input('right-attrs','value')]
    )
    def handle_analyse_btn_state(left_attrs, right_attrs):
        logger.debug("analyse_btn_state callback")
        if left_attrs and right_attrs: return False, False
        else: return True, True

    # Callback for data update and calculations ()
    @app.callback(
        [Output('loading_screen','fullscreen'),
        Output('alert-timeout', 'is_open'),
        Output('data-analysed', 'children'),
        Output('learnability_indicator', 'figure'),
        Output('g2_indicator', 'figure'),
        Output('g1_indicator', 'figure'),
        Output('ntuples_involved', 'children'),
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
            ctypes = dh["user_columns_type"]
            # API Calculations if requested
            if changed_id=='analyse_btn.n_clicks' and left_attrs and right_attrs:
                # Init calc df
                df_calc = df.copy()
                n_tuples = len(df_calc.index)
                df_calc[G12_COLUMN_NAME] = 0
                df_calc[G3_COLUMN_NAME] = 0                
                
                # Setting left and right tolerances
                xparams=parse_attributes_settings(left_tols, ctypes)
                yparams=parse_attributes_settings(right_tols, ctypes)

                
                
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
                    g1 = round(len(vps)/n_tuples**2,4)
                    g1_fig=fig_gen.bullet_indicator(value=(1-g1)*100, reference=g1_indicator['data'][0]['value'])
                    g2 = round(ncounterexample/n_tuples, 4)
                    g2_fig=fig_gen.bullet_indicator(value=(1-g2)*100, reference=g2_indicator['data'][0]['value'])
                    # Computing G3
                    if g3_computation=="exact": 
                        cover = return_dict["g3_exact_cover"]
                        g3 = len(cover)/n_tuples
                        if not g3 is None:
                            accuracy_ub = 1-g3
                            g3_indicator = fig_gen.gauge_indicator(value=accuracy_ub*100, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                        else:
                            is_open=True
                            g3_indicator = fig_gen.gauge_indicator(value=0, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                    else:
                        cover = return_dict["g3_ub_cover"]
                        g3_up = len(cover)/n_tuples
                        g3_lb = return_dict["g3_lb"]
                        lb_acc, ub_acc = (1-g3_up)*100, (1-g3_lb)*100
                        g3_indicator = fig_gen.gauge_indicator(value=(lb_acc+ub_acc)*0.5, reference=learnability_indicator['data'][0]['value'], lower_bound=lb_acc, upper_bound=ub_acc)

                    # Merging
                    df_calc[G3_COLUMN_NAME][cover] = 1
                    dh["data"]=df_calc
                    dh["X"]=list(xparams.keys())
                    dh["Y"]=list(yparams.keys())
                    overwrite_session_data_holder(session_id, dh)
                    overwrite_session_graphs(session_id)
                    overwrite_session_selected_point(session_id)
                    return True, is_open, "True", g3_indicator, g2_fig, g1_fig, ncounterexample_fig, False, False
                else:
                    is_open=True
            return True, is_open, "False", dash.no_update, dash.no_update, dash.no_update, " ", True, True
        else:
            raise PreventUpdate

    @app.callback(
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