import dash
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

def register_callbacks(plogger):
    logger = plogger

    @dash.callback([Output('selection_changed', 'children'),
                Output('ceviz_selection_infos', 'children'),
                Output('selection-table-collapse', 'is_open'),
                Output('selection-graph-collapse', 'is_open'),
                Output('clear-selection', 'disabled')],
                [Input('data-analysed', 'children'),
                Input('main-graph','clickData'),
                Input('cytoscape_ce_graph', 'tapNodeData'),
                Input('clear-selection','n_clicks'),
                Input('viz_datatable', 'active_cell'),
                Input('ceviz_datatable', 'active_cell'),
                Input('data_filters_have_changed', 'children')],
                [State('x-axis', 'value'),
                State('y-axis', 'value'),
                State('session-id', 'children')])
    def handle_selection(data_analysed, clickData, cytoData, clear_session_ncliks, active_cell, active_cell_ce, filters_changed, xaxis_column_name, yaxis_column_name, session_id):
        logger.debug("update_selection_from_graph callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data['data_holder']
        if dh is not None:
            df=dh['data']['df']
            graph=dh['graph']
            if df is not None:
                changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

                graph_is_open = True
                table_is_open = True
                clear_selection_disabled = False
                if changed_id == 'clear-selection.n_clicks' or changed_id == 'data-analysed.children' or changed_id == 'data_filters_have_changed.children': 
                    selected_point_id = None
                    graph_is_open, table_is_open = False, False
                elif changed_id == 'viz_datatable.active_cell' and active_cell is not None: # TABLE TAB LINE CLICK
                    selected_point_id = active_cell['row_id']
                elif changed_id == 'cytoscape_ce_graph.tapNodeData' and cytoData is not None: # CE GRAPH NODE CLICK
                    selected_point_id = int(cytoData['label'])
                elif changed_id == 'ceviz_datatable.active_cell' and active_cell_ce is not None: # CE TABLE LINE CLICK
                    selected_point_id = active_cell_ce['row_id']
                elif changed_id == 'main-graph.clickData' and clickData is not None: # 2D VIEW POINT CLICK
                    clickData=clickData['points'][0]
                    points=df.loc[(df[xaxis_column_name]==clickData['x']) & (df[yaxis_column_name]==clickData['y'])]
                    all_points_ids=list(points.index)
                    if graph is not None:
                        involved_points=[point for point in all_points_ids if point in graph]
                    else:
                        involved_points=[]
                    if involved_points: selected_point_id = involved_points[0]
                    else: selected_point_id = all_points_ids[0]
                else:
                    raise PreventUpdate

                # Getting and saving selected points
                if selected_point_id is not None:
                    selected_point = df.loc[selected_point_id]
                    if graph is not None and selected_point_id in graph :
                        involved_points_ids = [point_id for point_id in graph[selected_point_id]]
                        in_violation_with = df.loc[involved_points_ids]
                        ceviz_infos = f'Tuple {selected_point[ADESIT_INDEX]} is involved in {len(in_violation_with.index)} counterexamples.'
                    else:
                        in_violation_with = pd.DataFrame()
                        if graph is not None:
                            ceviz_infos = f'Tuple {selected_point[ADESIT_INDEX]} is not involved in any counterexample.'
                        else:
                            ceviz_infos = f'Tuple {selected_point[ADESIT_INDEX]} selected.'
                else:
                    selected_point = None
                    in_violation_with = pd.DataFrame()
                    ceviz_infos = 'Click on a point/line to select a tuple!'
                    clear_selection_disabled = True

                selection_infos = {
                    "point": selected_point,
                    "in_violation_with": in_violation_with
                }
                overwrite_session_selection_infos(session_id, selection_infos)

                if len(selection_infos['in_violation_with']) == 0: graph_is_open = False
                return "", ceviz_infos, table_is_open, graph_is_open, clear_selection_disabled
                    
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate