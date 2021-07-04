import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 

# Personnal imports
import figure_generator as fig_gen
from utils.cache_utils import *
from callbacks.constants import *

def register_data_callbacks(app, plogger):
    logger = plogger

    @app.callback([Output('data-loaded','children'),
                Output('dataset_confirm', 'children'),
                Output('left-attrs', 'disabled'),
                Output('right-attrs', 'disabled'),
                Output('collapse-viz', 'is_open')],
                [Input('toy-dataset-iris','n_clicks'),
                Input('toy-dataset-housing','n_clicks'),
                Input('toy-dataset-tobacco','n_clicks'),
                Input('toy-dataset-kidney','n_clicks'),
                Input('upload-form', 'contents')],
                [State('upload-form', 'filename'),
                State('session-id', 'children')])
    def handle_data(iris, housing, tobacco, kidney, contents, filename, session_id):
        logger.debug('handle_data callback')
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        clear_session(session_id)
        if "toy-dataset" in changed_id:
            toy_dataset = changed_id.split(".")[0].split("-")[-1]
            clear_session(session_id)
            dh = get_data(session_id, filename=toy_dataset, pydata=True)["data_holder"]
            n = len(dh["data"].index) if dh is not None else 0
            return toy_dataset, fig_gen.dataset_infos(toy_dataset, n, len(dh["data"].columns)), False, False, True
        elif filename is not None: 
            clear_session(session_id)
            dh = get_data(session_id, filename=filename, contents=contents)["data_holder"]
            n = len(dh["data"].index) if dh is not None else 0
            return filename, fig_gen.dataset_infos(filename, n, len(dh["data"].columns)), False, False, True
        else:
            raise PreventUpdate