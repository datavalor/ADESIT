import dash
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
    @app.callback(Output('viz_table_container', 'children'),
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

        
            columns = [{"name": column, "id": column, "hideable":True} for column in data.columns if column not in [G12_COLUMN_NAME, G3_COLUMN_NAME, SELECTION_COLUMN_NAME, ADESIT_INDEX]]
            columns = [{"name": ADESIT_INDEX, "id": ADESIT_INDEX, "hideable":False}]+columns

            output_df = data[[c["name"] for c in columns]].copy()
            overwrite_session_table_data(session_id, output_df)

            n_rows=len(output_df.index)
            table = dash_table.DataTable(
                id="viz_datatable",
                export_format='csv',
                columns=columns,
                page_current=0,
                page_size=TABLE_MAX_ROWS,
                page_count=math.ceil(n_rows/TABLE_MAX_ROWS),
                page_action='custom',
                style_data_conditional=[
                    {
                        'if': { 'column_id': ADESIT_INDEX },
                        'fontStyle': 'italic'
                    },
                ],
                style_as_list_view=True
            )
            return table
        else:
            raise PreventUpdate
    
    @app.callback(
    Output('viz_datatable', 'data'),
    [Input('viz_datatable', "page_current"),
    Input('viz_datatable', "page_size")],
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

    @app.callback(
        Output("viz_datatable", "style_data_conditional"),
        Input("viz_datatable", "active_cell")
    )
    def style_selected_rows(active_cell):
        if active_cell is None:                                                                                                                                                                                                                      
            raise PreventUpdate
        val = [
            {"if": {"filter_query": "{{id}} ={}".format(active_cell['row_id'])}, "backgroundColor": SELECTED_COLOR,}
        ]   
        return val