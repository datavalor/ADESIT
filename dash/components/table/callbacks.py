import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dash_table

# Miscellaneous
import pandas as pd
import numpy as np
import math
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *

def register_callbacks(plogger):
    logger = plogger

    default_style_data_conditional = [
        {
            'if': { 'column_id': ADESIT_INDEX },
            'fontStyle': 'italic'
        },
        {
            'if': { 'filter_query': '{_violating_tuple} = 1' },
            'backgroundColor': CE_COLOR,
            'color': 'white'
        },
        {
            'if': { 'filter_query': '{_violating_tuple} = 0' },
            'backgroundColor': FREE_COLOR,
            'color': 'white'
        },
        {
            'if': {
                'state': 'active',
                'filter_query': '{_violating_tuple} = 0' 
            },
            'backgroundColor': SELECTED_COLOR_GOOD,
            'color': 'white',
            'border': '3px solid black'
        },
        {
            'if': {
                'state': 'active',
                'filter_query': '{_violating_tuple} = 1' 
            },
            'backgroundColor': SELECTED_COLOR_BAD,
            'color': 'white',
            'border': '3px solid black'
        }
    ]

    # Callback for Table Output (b,c,d,e,f,g->h) 
    @dash.callback(Output('viz_table_container', 'children'),
                [Input('data-loaded','children'),
                Input('main-graph','selectedData'),
                Input('view','value'),
                Input('mode','value'),
                Input('data-analysed', 'children'),
                Input('time-period-dropdown', 'options'),
                Input('current-time-range', 'children')],
                [State('session-id', 'children')])
    def handle_table(data_updated, selected_data, view, mode, analysed, time_period_options, current_time_range, session_id):
        logger.debug("handle_table callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=session_data["data_holder"]
        if dh is not None:
            data=dh["data"]

            # filtering by time
            # if dh["time_infos"] is not None:
            #     curr_index = dh["time_infos"]["current_time_period"]
            #     low_cut, high_cut = dh["time_infos"]["time_periods_list"][curr_index:curr_index+2]
            #     data=data[low_cut:high_cut]

            col_types=dh["columns_type"]
            # select_problematics/non problematics according to mode and view
            if label_column in data.columns:
                if view == 'NP': data=data.loc[data[label_column] == 0]
                elif view == 'P': data=data.loc[data[label_column] > 0]
            
            if SELECTION_COLUMN_NAME in data.columns and len(np.unique(data[SELECTION_COLUMN_NAME]))!=1:
                data=data.loc[data[SELECTION_COLUMN_NAME]>0]

            columns = [{"name": [col_types[column], column], "id": column, "hideable":True} for column in data.columns if column in dh["user_columns"]]
            columns = sorted(columns, key=lambda x: "".join(x["name"]), reverse=True)
            if G12_COLUMN_NAME in data.columns:
                columns = [{"name": ["", G12_COLUMN_NAME], "id": G12_COLUMN_NAME}]+columns
            columns = [{"name": ["", ADESIT_INDEX], "id": ADESIT_INDEX, "hideable":False}]+columns
            
            output_df = data[[c["id"] for c in columns]]
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
                style_data_conditional=default_style_data_conditional,
                style_cell_conditional=[
                    {'if': {'column_id': G12_COLUMN_NAME,}, 'display': 'None',}
                ],
                merge_duplicate_headers=True
            )
            return table
        else:
            raise PreventUpdate
    
    @dash.callback(
    Output('viz_datatable', 'data'),
    [Input('viz_datatable', "page_current"),
    Input('viz_datatable', "page_size")],
    [State('session-id', 'children')])
    def update_table(page_current, page_size, session_id):
        logger.debug("update_table callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        table_data = session_data["table_data"]
        if table_data is not None and page_current is not None:
            return table_data.iloc[
                page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
        else:
            raise PreventUpdate

    @dash.callback(
        [Output("viz_datatable", "style_data_conditional"),
        Output("viz_datatable", "page_current")],
        Input('selection_changed', 'children'),
        [State('session-id', 'children')]
    )
    def style_selected_rows(selection_changed, session_id):
        selection_infos = get_data(session_id)["selected_point"]
        if selection_infos["point"] is not None:
            selection_color = (SELECTED_COLOR_BAD, "black") if selection_infos["in_violation_with"] else (SELECTED_COLOR_GOOD, "white")
            style_data_conditional = default_style_data_conditional+[
                {
                    "if": {
                        "filter_query": f'{{id}} = {selection_infos["point"]}'
                    }, 
                    "backgroundColor": selection_color[0],
                    "color": selection_color[1]
                }
            ] 
            for p in selection_infos["in_violation_with"]:
                style_data_conditional.append({
                    "if": {
                        "filter_query": f"{{id}} = {p}"
                    },
                    "backgroundColor": CE_COLOR,
                    "color": "white",
                    'border': '4px solid black'
                })
            page = math.floor((selection_infos["point"]-1)/TABLE_MAX_ROWS)
            return style_data_conditional, page
        else:
            return default_style_data_conditional, dash.no_update