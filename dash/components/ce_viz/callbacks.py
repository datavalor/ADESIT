import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import queue

import dash_table

# Miscellaneous
import pandas as pd
import math
import numpy as np
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

from constants import *

def register_callbacks(app, plogger):
    logger = plogger

    @app.callback(Output('ceviz_table_container', 'children'),
                Input('selection_changed', 'children'),
                [State('session-id', 'children')])
    def handle_ceviz_table(selection_changed, session_id):
        logger.debug("handle_ceviz_table callback")

        session_data = get_data(session_id)
        dh = session_data["data_holder"]
        selection_info = session_data["selected_point"]
        
        if dh is not None and dh["data"] is not None:
            df=dh["data"]
            user_cols=dh["user_columns"]
            for c in dh["X"]+dh["Y"]: user_cols.remove(c)

            # Create column list for datatable
            column_id = [{"name": ["", ADESIT_INDEX], "id": ADESIT_INDEX}]
            columns_other = [{"name": ["Others", column], "id": column} for column in user_cols]
            columns_X = [{"name": ["Feature(s)", column], "id": column} for column in dh["X"]]
            columns_Y = [{"name": ["Target", column], "id": column} for column in dh["Y"]]
            columns = column_id+columns_other+columns_X+columns_Y
            
            # Forces others column to have white background
            white_back = []
            for c in user_cols:
                white_back.append({
                    'if': { 'column_id': c },
                    'backgroundColor': 'white',
                    'color': 'black'
                })

            if selection_info["point"] is None:
                output_df = pd.DataFrame(columns=[c["name"][1] for c in columns])
                style_data_conditional = None
                n_rows = 0
            else:
                selected_points = [selection_info["point"]] + selection_info["in_violation_with"]
                output_df = df.loc[selected_points][[c["name"][1] for c in columns]]
                n_rows=len(output_df.index)
                selection_color = SELECTED_COLOR_BAD if selection_info["in_violation_with"] else SELECTED_COLOR_GOOD
                style_data_conditional=[
                    {
                        'if': {'column_editable': False},
                        'backgroundColor': CE_COLOR,
                        'color': 'white'
                    },
                    {
                        'if': { 'row_index': 0 },
                        'backgroundColor': selection_color,
                        'color': 'black'
                    },
                    {
                        'if': { 'column_id': ADESIT_INDEX },
                        'backgroundColor': 'white',
                        'fontStyle': 'italic',
                        'color': 'black'
                    },
                ]+white_back

            table = dash_table.DataTable(
                data=output_df.to_dict('records'),
                id="ceviz_datatable",
                columns=columns,
                page_current=0,
                page_size=TABLE_MAX_ROWS,
                page_count=math.ceil(n_rows/TABLE_MAX_ROWS),
                style_data_conditional=style_data_conditional,
                # style_as_list_view=True,
                merge_duplicate_headers=True
            )
               
            return table
        else:
            raise PreventUpdate

    # @app.callback(
    #     Output('cytoscape_ce_graph', 'elements'),
    #     [Input('clear-selection', 'disabled')],
    #     [State('session-id', 'children')]
    # )
    # def handle_ceviz_cyto(clear_selection_disabled, session_id):
    #     logger.debug("handle_ceviz_cyto callback")

    #     session_data = get_data(session_id)
    #     dh = session_data["data_holder"]
    #     selected_points = session_data["selected_point"]
        
    #     if dh is not None and dh["graph"] is not None and selected_points is not None:
    #         graph=dh["graph"]

    #         root=selected_points[0]
    #         elements = [{
    #             'data': {
    #                 'id': root, 
    #                 'label': f"{root}",
    #             },
    #             # 'position': {'x': 75, 'y': 75},
    #             # 'locked': True,
    #             'classes': 'selected_node'
    #         }]

    #         # Creates graph in a BFS fashion
    #         max_depth = 3
    #         explored_list = {}
    #         q = queue.LifoQueue()
    #         # explored_list[root]=True
    #         q.put((root, 0))
    #         while not q.empty() and max_depth>0:
    #             v, depth = q.get()
    #             if v not in explored_list:
    #                 explored_list[v]=True
    #                 for w in graph[v]:
    #                     elements.append({
    #                         'data': {
    #                             'id': w, 
    #                             'label': w
    #                         },
    #                         'classes': 'ce_node'
    #                     })
    #                     edge = {
    #                         'data': {
    #                             'source': v, 
    #                             'target': w
    #                         }
    #                     }
    #                     if depth>0: edge['classes'] = 'undirect_edges'
    #                     elements.append(edge)

    #                     if depth+1 <= max_depth:
    #                         q.put((w, depth+1))

    #         return elements
    #     else:
    #         raise PreventUpdate