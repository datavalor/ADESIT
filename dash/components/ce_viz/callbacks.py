import dash
import dash_html_components as html
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
        Input('graph_depth_slider', 'value'),
        Input('cytoscape_ce_graph', 'mouseoverNodeData')],
        [State('cytoscape_ce_graph', 'elements'),
        State('session-id', 'children')]
    )
    def handle_ceviz_cyto(selection_changed, max_depth, hovered_data, previous_elements, session_id):
        logger.debug("handle_ceviz_cyto callback")

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id=='cytoscape_ce_graph.mouseoverNodeData':
            if hovered_data is not None:
                hovered_id = str(hovered_data["id"])
                for i, el in enumerate(previous_elements):
                    if str(el["data"].get("id", "NO"))==hovered_id:
                        previous_elements[i]["classes"] = f'{el["classes"]} hovered'
                    else:
                        previous_elements[i]["classes"] = el["classes"].split(" ")[0]
                return previous_elements, dash.no_update
            else:
                raise PreventUpdate

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

    @app.callback(Output('ceviz_hovered_node', 'children'),
                  [Input('cytoscape_ce_graph', 'mouseoverNodeData'),
                  Input('selection_changed', 'children')],
                  [State('session-id', 'children')])
    def displayHoveredNodeData(data, selec, session_id):
        def gen_content(tuple, id, features=[], target=[], other=[]):
            content = []
            content.append(html.Div(f"[id]: {id}"))
            for f in features:
                val = tuple[f]
                content.append(html.Div(f"[F] {f}: {val}"))
            for t in target:
                val = tuple[t]
                content.append(html.Div(f"[T] {t}: {val}"))
            for o in other:
                val = tuple[o]
                content.append(html.Div(f"{o}: {val}"))
            return content

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id=='cytoscape_ce_graph.mouseoverNodeData' and data is not None:
            hovered_id = data['id']
            dh = get_data(session_id)["data_holder"]
            df = dh["data"]
            features = dh["X"]
            target = dh["Y"]
            other = dh["user_columns"]
            for f in features: other.remove(f)
            for t in target: other.remove(t)
            return gen_content(df.loc[int(hovered_id)], hovered_id, features, target, other)
        else:
            return ""