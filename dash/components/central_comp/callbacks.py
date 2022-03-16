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

    def handle_graph_click_data(clickData, df, graph, xaxis_column_name, yaxis_column_name):
        clickData=clickData['points'][0]
        points=df.loc[(df[xaxis_column_name]==clickData['x']) & (df[yaxis_column_name]==clickData['y'])]
        all_points_ids=list(points.index)
        if graph is not None: involved_points=[point for point in all_points_ids if point in graph]
        else: involved_points=[]
        if involved_points: selected_point_id = involved_points[0]
        else: selected_point_id = all_points_ids[0]
        return selected_point_id


    @dash.callback(
        [
            Output('selection_changed', 'children'),
            Output('ceviz_selection_infos', 'children'),
            Output('selection-table-collapse', 'is_open'),
            Output('selection-graph-collapse', 'is_open'),
            Output('clear-selection-button', 'disabled')
        ],
        [
            Input('data-analysed-prop', 'children'),
            Input('data_updated', 'children'),
            Input('view2d-graph','clickData'),
            Input('timetrace-graph','clickData'),
            Input('cytoscape_ce_graph', 'tapNodeData'),
            Input('clear-selection-button','n_clicks'),
            Input('main-datatable', 'active_cell'),
            Input('selection-datatable', 'active_cell'),
        ],
        [
            State('view2d-xaxis-dropdown', 'value'),
            State('view2d-yaxis-dropdown', 'value'),
            State('timetrace-yaxis-dropdown', 'value'),
            State('session-id', 'children')
        ]
    )
    def handle_selection(
        data_analysed, 
        data_updated, 
        view2d_clickData, 
        timetrace_clickData, 
        cytoData, 
        clear_session_ncliks, 
        active_cell, 
        active_cell_ce, 
        view2d_xaxis,
        view2d_yaxis, 
        timetrace_yaxis,
        session_id
    ):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug("update_selection_from_graph callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data['data_holder']
        if dh is None: raise PreventUpdate

        df=dh['data']['df']
        if df is None: raise PreventUpdate
        
        graph=dh['data']['graph']
        background_needs_update = False
        clear_selection_disabled = False
        if changed_id == 'clear-selection-button.n_clicks': 
            selected_point_id = None
        elif changed_id == 'data_updated.children': 
            background_needs_update = True
            selected_point_id = None
        elif changed_id == 'data-analysed-prop.children':
            background_needs_update = True
            if session_data['selection_infos']['point'] is not None:
                selected_point_id = session_data['selection_infos']['point'].name
            else: 
                selected_point_id = None
        elif changed_id == 'main-datatable.active_cell' and active_cell is not None: # TABLE TAB LINE CLICK
            selected_point_id = active_cell['row_id']
        elif changed_id == 'cytoscape_ce_graph.tapNodeData' and cytoData is not None: # CE GRAPH NODE CLICK
            selected_point_id = int(cytoData['label'])
        elif changed_id == 'selection-datatable.active_cell' and active_cell_ce is not None: # CE TABLE LINE CLICK
            selected_point_id = active_cell_ce['row_id']
        elif changed_id == 'view2d-graph.clickData' and view2d_clickData is not None: # 2D VIEW POINT CLICK
            selected_point_id = handle_graph_click_data(view2d_clickData, df, graph, view2d_xaxis, view2d_yaxis)
        elif changed_id == 'timetrace-graph.clickData' and timetrace_clickData is not None: # TIME TRACE VIEW POINT CLICK
            time_attribute = dh['time_infos']['time_attribute']
            selected_point_id = handle_graph_click_data(timetrace_clickData, df, graph, time_attribute, timetrace_yaxis)
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
            'background_needs_update': background_needs_update,
            'point': selected_point,
            'in_violation_with': in_violation_with
        }
        overwrite_session_selection_infos(session_id, selection_infos)

        return [
            "", 
            ceviz_infos, 
            (selected_point is not None), 
            (not selection_infos['in_violation_with'].empty), 
            (selected_point is None)
        ]