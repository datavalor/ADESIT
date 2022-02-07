import dash
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dash_table

# Miscellaneous
import pandas as pd
import math
import random
import queue
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *
from .cyto_utils import gen_cyto

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(Output('ceviz_table_container', 'children'),
                Input('selection_changed', 'children'),
                [State('session-id', 'children')])
    def handle_ceviz_table(selection_changed, session_id):
        logger.debug("handle_ceviz_table callback")

        session_data = get_data(session_id)
        dh = session_data['data_holder']
        point = session_data['selected_point']['point']
        in_violation_with = session_data['selected_point']['in_violation_with']
        if dh is not None and dh['data']['df'] is not None:
            user_columns_names=list(dh['user_columns'].keys())
            for c in dh["X"]+dh["Y"]: user_columns_names.remove(c)

            # Create column list for datatable
            column_id = [{"name": ["", ADESIT_INDEX], "id": ADESIT_INDEX}]
            columns_other = [{"name": ["Others", column], "id": column} for column in user_columns_names]
            columns_X = [{"name": ["Feature(s)", column], "id": column} for column in dh["X"]]
            columns_Y = [{"name": ["Target", column], "id": column} for column in dh["Y"]]
            columns = column_id+columns_other+columns_X+columns_Y
            
            # Forces others column to have white background
            white_back = []
            for c in user_columns_names:
                white_back.append({
                    'if': { 'column_id': c },
                    'backgroundColor': 'white',
                    'color': 'black'
                })

            if point is None:
                output_df = pd.DataFrame(columns=[c["name"][1] for c in columns])
                style_data_conditional = None
                n_rows = 0
            else:
                output_df = pd.concat([pd.DataFrame([point]), in_violation_with])
                n_rows=len(output_df.index)
                selection_color = SELECTED_COLOR_BAD if not in_violation_with.empty else SELECTED_COLOR_GOOD
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
                merge_duplicate_headers=True
            )
               
            return table
        else:
            raise PreventUpdate

    @dash.callback(
        Output('cyto_container', 'children'),
        [Input('selection_changed', 'children'),
        Input('graph_depth_slider', 'value')],
        [State('session-id', 'children')]
    )
    def handle_ceviz_cyto(selection_changed, max_depth, session_id):
        logger.debug("handle_ceviz_cyto callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh = session_data['data_holder']
        selected_points = session_data["selected_point"]
        in_violation_with = selected_points["in_violation_with"]
        if dh is not None and dh["graph"] is not None and selected_points is not None and selected_points['point'] is not None:
            df = session_data['data_holder']['data']['df']
            root = selected_points['point'].name

            nodes = {}
            nodes[root] = 0        
            edges = {}
            if not in_violation_with.empty:
                # Creates graph in a DFS fashion
                graph=dh["graph"]
                explored_list = {}
                q = queue.LifoQueue()
                q.put(root)
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
            
            elements = []
            modified_node_name = {}
            for node, depth in nodes.items():
                if node==root:
                    selected_class = 'selected_node_bad' if not in_violation_with.empty else 'selected_node_good'
                else:
                    selected_class = 'ce_node'
                modified_node_name[node] = f"{node}_{'{:.6f}'.format(random.random())}"
                elements.append({
                    'data': {
                        'id': modified_node_name[node], 
                        'label': str(df.loc[node][ADESIT_INDEX])
                    },
                    'classes': selected_class
                })

            for edge, depth in edges.items():
                if depth>1: edge_class = 'undirect_edges'
                else: edge_class = 'direct_edges'
                elements.append({
                    'data': {
                        'source': modified_node_name[edge[0]], 
                        'target': modified_node_name[edge[1]]
                    },
                    'classes': edge_class
                })
            return gen_cyto(elements, {'name': 'breadthfirst', 'roots': f'[id = "{modified_node_name[root]}"]'})
        else:
            return gen_cyto()

    @dash.callback(
        Output('cytoscape_ce_graph', 'elements'),
        [Input('cytoscape_ce_graph', 'mouseoverNodeData')],
        [State('cytoscape_ce_graph', 'elements')]
    )
    def highlightHoveredNode(hovered_data, previous_elements):
        logger.debug("handle_hovered_ceviz_cyto callback")

        if hovered_data is not None:
            hovered_id = str(hovered_data["id"])
            for i, el in enumerate(previous_elements):
                if str(el['data'].get('id', 'NO'))==hovered_id:
                    previous_elements[i]['classes'] = f'{el["classes"]} hovered'
                else:
                    previous_elements[i]['classes'] = el['classes'].split(" ")[0]
            return previous_elements
        else:
            raise PreventUpdate

    @dash.callback(Output('ceviz_hovered_node', 'children'),
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
            clicked_id = data['label']
            dh = get_data(session_id)['data_holder']
            df = dh['data']['df']
            features = dh['X']
            target = dh['Y']
            other = list(dh['user_columns'].keys())
            for f in features: other.remove(f)
            for t in target: other.remove(t)
            return gen_content(df.loc[int(clicked_id)], clicked_id, features, target, other)
        else:
            return ""