import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import dash_table

# Miscellaneous
import pandas as pd
import math
import numpy as np
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

def register_callbacks(app, plogger):
    logger = plogger

    @app.callback(Output('ceviz_table_container', 'children'),
                [Input('clear-selection', 'disabled')#,Input('clear-selection','n_clicks')
                ],
                [State('session-id', 'children')])
    def handle_ceviz_table(clear_selection_disabled, session_id):
        logger.debug("handle_table callback")
        # label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        session_data = get_data(session_id)
        dh = session_data["data_holder"]
        selected_points = session_data["selected_point"]
        
        if dh is not None and dh["data"] is not None and selected_points is not None:
            df=dh["data"]
            column_id = [{"name": ["", ADESIT_INDEX], "id": ADESIT_INDEX}]
            columns_X = [{"name": ["Feature(s)", column], "id": column} for column in dh["X"]]
            columns_Y = [{"name": ["Target", column], "id": column} for column in dh["Y"]]
            columns = column_id+columns_X+columns_Y
            
            if clear_selection_disabled:
                output_df = None
                style_data_conditional = None
                n_rows = 0
            else:
                output_df = df.loc[selected_points][[c["name"][1] for c in columns]]
                n_rows=len(output_df.index)
                output_df = output_df.to_dict('records')
                style_data_conditional=[
                    {
                        'if': {'column_editable': False},
                        'backgroundColor': '#EF553B',
                        'color': 'white'
                    },
                    {
                        'if': { 'row_index': 0 },
                        'backgroundColor': '#eff22c',
                        'color': 'black'
                    },
                    {
                        'if': { 'column_id': ADESIT_INDEX },
                        'backgroundColor': 'white',
                        'fontStyle': 'italic',
                        'color': 'black'
                    },
                ]

            table = dash_table.DataTable(
                data=output_df,
                id="ceviz_datatable",
                columns=columns,
                page_current=0,
                page_size=TABLE_MAX_ROWS,
                page_count=math.ceil(n_rows/TABLE_MAX_ROWS),
                style_data_conditional=style_data_conditional,
                # style_as_list_view=True,
                merge_duplicate_headers=True
            ),
               
            return table
        else:
            raise PreventUpdate