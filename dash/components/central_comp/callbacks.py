import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

def register_callbacks(plogger):
    logger = plogger

    @dash.callback([Output("selection_changed", "children"),
                Output("ceviz_selection_infos", "children")],
                [Input('data-analysed', 'children'),
                Input('main-graph','clickData'),
                Input('cytoscape_ce_graph', 'tapNodeData'),
                Input('clear-selection','n_clicks'),
                Input("viz_datatable", "active_cell"),
                Input("ceviz_datatable", "active_cell")],
                [State('x-axis', 'value'),
                State('y-axis', 'value'),
                State('session-id', 'children')])
    def handle_selection(data_analysed, clickData, cytoData, clear_session_ncliks, active_cell, active_cell_ce, xaxis_column_name, yaxis_column_name, session_id):
        logger.debug("update_selection_from_graph callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data['data_holder']
        if dh is not None:
            df=dh["data"]
            graph=dh["graph"]
            if df is not None and graph is not None:
                changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

                if changed_id == 'clear-selection.n_clicks' or changed_id == 'data-analysed.children': 
                    selected_point_id = None
                elif changed_id == 'viz_datatable.active_cell' and active_cell is not None:
                    selected_point_id = active_cell['row_id']
                elif changed_id == 'cytoscape_ce_graph.tapNodeData' and cytoData is not None:
                    selected_point_id = int(cytoData["label"])
                elif changed_id == 'ceviz_datatable.active_cell' and active_cell_ce is not None:
                    selected_point_id = active_cell_ce['row_id']
                elif changed_id == 'main-graph.clickData' and clickData is not None:
                    clickData=clickData['points'][0]
                    points=df.loc[(df[xaxis_column_name]==clickData['x']) & (df[yaxis_column_name]==clickData['y'])]
                    all_points=list(points.index)
                    involved_points=[point for point in all_points if point in graph]
                    if involved_points: selected_point_id = involved_points[0]
                    else: selected_point_id = all_points[0]
                else:
                    raise PreventUpdate

                # Getting and saving selected points
                selection_infos = {
                    "point": selected_point_id,
                    "in_violation_with": []
                }
                if selected_point_id is not None:
                    if selected_point_id in graph:
                        selection_infos["in_violation_with"] = graph[selected_point_id]
                        ceviz_infos = f'Tuple {selected_point_id} is involved in {len(selection_infos["in_violation_with"])} counterexamples.'
                    else:
                        ceviz_infos = f'Tuple {selected_point_id} is not involved in any counterexample.'
                else:
                    ceviz_infos = "No tuple selected."
                overwrite_session_selected_point(session_id, selection_infos)
                return "", ceviz_infos
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate