import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import queue

import dash_table

# Miscellaneous
import pandas as pd
import math
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

    @app.callback(
        [Output('cytoscape_ce_graph', 'elements'),
        Output('cytoscape_ce_graph', 'layout')],
        [Input('selection_changed', 'children'),
        Input('graph_depth_slider', 'value')],
        [State('session-id', 'children')]
    )
    def handle_ceviz_cyto(selection_changed, max_depth, session_id):
        logger.debug("handle_ceviz_cyto callback")

        session_data = get_data(session_id)
        dh = session_data["data_holder"]
        selected_points = session_data["selected_point"]
        
        if dh is not None and dh["graph"] is not None and selected_points is not None and selected_points['point'] is not None:
            graph=dh["graph"]
            root=selected_points['point']
            selected_class = 'selected_node_bad' if selected_points["in_violation_with"] else 'selected_node_good'
            elements = [{
                'data': {
                    'id': root, 
                    'label': f"{root}",
                },
                'classes': selected_class,
            }]
        
            if selected_points["in_violation_with"]:
                # Creates graph in a DFS fashion
                explored_list = {}
                q = queue.LifoQueue()
                q.put(root)
                nodes = {}
                edges = {}
                nodes[root] = 0
                while not q.empty():
                    v = q.get()
                    depth = nodes[v]
                    if v not in explored_list:
                        explored_list[v]=True
                        for w in graph[v]:
                            if depth+1 <= max_depth:
                                if w not in nodes: nodes[w]=depth+1
                                norm_edge = tuple(sorted([v,w]))
                                if norm_edge not in edges: edges[norm_edge]=depth+1
                                q.put(w)
            for node, depth in nodes.items():
                elements.append({
                    'data': {
                        'id': node, 
                        'label': f"{node}"
                    },
                    'classes': 'ce_node'
                })
            for edge, depth in edges.items():
                if depth>1: edge_class = 'undirect_edges'
                else: edge_class = 'direct_edges'
                elements.append({
                    'data': {
                        'source': edge[0], 
                        'target': edge[1]
                    },
                    'classes': edge_class
                })
            return elements, {'name': 'breadthfirst', 'roots': f'[id = "{root}"]'}
        else:
            return [], {'name': 'breadthfirst'}