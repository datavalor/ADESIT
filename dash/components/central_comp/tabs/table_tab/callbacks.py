import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dash_table

# Miscellaneous
import pandas as pd
import math
import numpy as np
pd.options.mode.chained_assignment = None

from constants import *
import utils.viz.table_utils as table_utils
from utils.cache_utils import *
import utils.viz.figure_utils as figure_utils

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        Output('viz_table_container', 'children'),
        [
            Input('selection_changed', 'children'),
            Input('view','value'),
            Input('mode','value'),
        ],
        [State('session-id', 'children')]
    )
    def update_table(selection_changed, view, mode, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug("update_table callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh=session_data['data_holder'].copy()
        if dh is None or dh['data']['df'] is None: raise PreventUpdate

        if changed_id == 'selection_changed.children':
            if not session_data['selection_infos']['background_needs_update']: 
                logger.debug("update_table callback ABORTED")
                raise PreventUpdate

        # select_problematics/non problematics according to mode and view
        data_key = 'df'
        if dh['data']['df_free'] is not None:
            if view == 'NP': data_key='df_free'
            elif view == 'P': data_key='df_prob'

        by_data_type = True if dh['data']['df_free'] is None else False
        columns, hidden_columns, table_data = table_utils.data_preprocessing_for_table(dh, data_key=data_key, by_data_type=by_data_type)
        overwrite_session_table_data(session_id, table_data)

        sdc, page = table_utils.generate_selection_sdc(dh, session_data['selection_infos'], table_data)
        if page==dash.no_update: page = 0

        n_rows=len(table_data['df_table'].index)
        table = dash_table.DataTable(
            id='main-datatable',
            export_format='csv',
            columns=columns,
            page_current=page,
            page_size=TABLE_MAX_ROWS,
            page_count=math.ceil(n_rows/TABLE_MAX_ROWS),
            page_action='custom',
            hidden_columns = hidden_columns,
            style_data_conditional=sdc,
            merge_duplicate_headers=True
        )
        return table
    
    @dash.callback(
        Output('main-datatable', 'data'),
        [
            Input('main-datatable', 'page_current'),
            Input('viz_table_container', 'children')
        ],
        [
            State('main-datatable', 'page_size'),
            State('session-id', 'children')
        ]
    )
    def update_table_records(page_current, viz_table_container, page_size, session_id):
        logger.debug("update_table_records callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        table_data = session_data['table_data']['df_table']
        if table_data is None or page_current is None: raise PreventUpdate
        records = table_data.iloc[
            page_current*page_size:(page_current+1)*page_size
        ].to_dict('records')
        return records            

    @dash.callback(
        [
            Output('main-datatable', 'style_data_conditional'),
            Output('main-datatable', 'page_current')
        ],
        Input('selection_changed', 'children'),
        State('session-id', 'children')
    )
    def style_selected_rows(selection_changed, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug("style_selected_rows callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        if changed_id == 'selection_changed.children':
            if session_data['selection_infos']['background_needs_update']: 
                logger.debug("style_selected_rows callback ABORTED")
                raise PreventUpdate
        logger.debug("style_selected_rows callback CONTINUED")

        dh = session_data['data_holder']
        if dh is None: raise PreventUpdate

        selection_infos = session_data['selection_infos']
        table_data = session_data['table_data']
        return table_utils.generate_selection_sdc(dh, selection_infos, table_data)
            