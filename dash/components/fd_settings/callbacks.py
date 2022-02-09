import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import numpy as np
import numpy as np


# Personnal imports
import utils.data_utils as data_utils
from utils.cache_utils import *
from constants import *

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
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
            dh = data.get('data_holder', None)
            n = len(dh['df_full'].index) if dh is not None else 0
            return '', data_utils.dataset_infos(filename, n, len(dh['user_columns'])), False, False, dash.no_update
        else:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, True
        

    # Callback for Dimensions (attribute) options in dropdowns (b->c,d,f)
    @dash.callback(
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

        dh=session_data['data_holder']
        if dh is not None:
            options = []
            for attr_name, attr in dh['user_columns'].items():
                options.append({'label': attr_name, 'title': attr.get_type(), 'value': attr_name})
            return options, options, None, None
        else:
            return [], [], None, None

    # Callback for Left Tolerances Output ()
    @dash.callback(
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
        dh=session_data['data_holder']
        if inputattr is not None and dh is not None:
            # Retrieve previous settings
            new_attributes_settings = data_utils.parse_attributes_settings(inputtols, dh['user_columns'])
            attributes_settings = get_data(session_id)["thresolds_settings"]
            if new_attributes_settings is not None:
                for attr in new_attributes_settings.keys(): attributes_settings[attr] = new_attributes_settings[attr]
                overwrite_session_thresolds_settings(session_id, attributes_settings)            
            
            outuput_thresolds = []
            for attr in inputattr:
                if dh['user_columns'].get(attr, None) is not None:
                    if dh['user_columns'][attr].is_categorical():
                        outuput_thresolds.append({'attribute': attr, 'absolute': 'is', 'relative': 'categorical...'})
                    elif dh['user_columns'][attr].is_numerical():
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
    @dash.callback(
        [Output('analyse_btn', 'disabled'),
        Output('g3_computation', 'disabled')],
        [Input('left-attrs','value'),
        Input('right-attrs','value')]
    )
    def handle_analyse_btn_state(left_attrs, right_attrs):
        logger.debug("analyse_btn_state callback")
        if left_attrs and right_attrs: return False, False
        else: return True, True