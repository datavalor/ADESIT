from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_table

# Miscellaneous
import pandas as pd
import numpy as np
import math
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

def register_callbacks(app, plogger):
    logger = plogger

    # Callback for Table Output (b,c,d,e,f,g->h) 
    @app.callback(Output('table-container', 'children'),
                [Input('data-loaded','children'),
                Input('main-graph','selectedData'),
                Input('view','value'),
                Input('mode','value')],
                [State('session-id', 'children')])
    def handle_table(data_updated, selected_data, view, mode, session_id):
        logger.debug("handle_table callback")
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            data=dh["data"]
            # select_problematics/non problematics according to mode and view
            if label_column in data.columns:
                if view == 'NP': data=data.loc[data[label_column] == 0]
                elif view == 'P': data=data.loc[data[label_column] > 0]
            
            if SELECTION_COLUMN_NAME in data.columns and len(np.unique(data[SELECTION_COLUMN_NAME]))!=1:
                data=data.loc[data[SELECTION_COLUMN_NAME]>0]

        
            columns = [{"name": column, "id": column} for column in data.columns if column not in [G12_COLUMN_NAME, G3_COLUMN_NAME, SELECTION_COLUMN_NAME]]

            output_df = data[[c["name"] for c in columns]].copy()
            overwrite_session_table_data(session_id, output_df)

            n_rows=len(output_df.index)
            rows_per_page = 15
            table = dash_table.DataTable(
                id="dataTable",
                export_format='csv',
                columns=columns,
                page_current=0,
                page_size=rows_per_page,
                page_count=math.ceil(n_rows/rows_per_page),
                page_action='custom')
            return table
        else:
            raise PreventUpdate
    
    @app.callback(
    Output('dataTable', 'data'),
    [Input('dataTable', "page_current"),
    Input('dataTable', "page_size")],
    [State('session-id', 'children')])
    def update_table(page_current, page_size, session_id):
        logger.debug("update_table callback")
        table_data=get_data(session_id)["table_data"]
        if table_data is not None and page_current is not None:
            return table_data.iloc[
                page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
        else:
            raise PreventUpdate