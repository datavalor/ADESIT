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
import utils.viz.table_utils as table_utils
from utils.cache_utils import *

def register_callbacks(plogger):
    logger = plogger

    # Callback for Table Output (b,c,d,e,f,g->h) 
    @dash.callback(Output('viz_table_container', 'children'),
                [Input('data-loaded','children'),
                Input('main-graph','selectedData'),
                Input('view','value'),
                Input('mode','value'),
                Input('data-analysed', 'children'),
                Input('time-period-dropdown', 'options'),
                Input('data_filters_have_changed', 'children')],
                [State('session-id', 'children')])
    def handle_table(data_updated, selected_data, view, mode, analysed, time_period_options, filters_changed, session_id):
        logger.debug("handle_table callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        # label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=session_data['data_holder']
        if dh is not None:
            # select_problematics/non problematics according to mode and view
            data_key = 'df'
            if dh['data']['df_free'] is not None:
                if view == 'NP': data_key='df_free'
                elif view == 'P': data_key='df_prob'
            
            # if SELECTION_COLUMN_NAME in data.columns and len(np.unique(data[SELECTION_COLUMN_NAME]))!=1:
            #     data=data.loc[data[SELECTION_COLUMN_NAME]>0]

            by_data_type = True if dh['data']['df_free'] is None else False
            columns, hidden_columns, table_data = table_utils.data_preprocessing_for_table(dh, data_key=data_key, by_data_type=by_data_type)
            
            overwrite_session_table_data(session_id, table_data)

            n_rows=len(table_data['df_table'].index)
            table = dash_table.DataTable(
                id="viz_datatable",
                export_format='csv',
                columns=columns,
                page_current=0,
                page_size=TABLE_MAX_ROWS,
                page_count=math.ceil(n_rows/TABLE_MAX_ROWS),
                page_action='custom',
                hidden_columns = hidden_columns,
                style_data_conditional=table_data['pre_sdc']+table_data['post_sdc'],
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

        table_data = session_data['table_data']['df_table']
        if table_data is not None and page_current is not None:
            records = table_data.iloc[
                page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
            return records
        else:
            raise PreventUpdate

    @dash.callback(
        [Output('viz_datatable', 'style_data_conditional'),
        Output('viz_datatable', 'page_current')],
        Input('selection_changed', 'children'),
        [State('session-id', 'children')]
    )
    def style_selected_rows(selection_changed, session_id):
        logger.debug("handle_table callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        selection_infos = session_data['selection_infos']
        table_infos = session_data['table_data']
        dh=session_data['data_holder']
        if selection_infos['point'] is not None:
            if dh['data']['df_free'] is not None:
                selection_color = (SELECTED_COLOR_BAD, 'black') if not selection_infos['in_violation_with'].empty else (SELECTED_COLOR_GOOD, "white")
            else:
                selection_color = (NON_ANALYSED_COLOR, 'white')
            sdc = table_infos['pre_sdc']
            sdc.append(
                {
                    'if': {
                        'filter_query': f'{{id}} = {selection_infos["point"].name}'
                    }, 
                    'backgroundColor': selection_color[0],
                    'color': selection_color[1]
                }
            )
            for idx, _ in selection_infos['in_violation_with'].iterrows():
                sdc.append(
                    {
                    'if': {
                        'filter_query': f'{{id}} = {idx}'
                    },
                    'backgroundColor': CE_COLOR,
                    'color': 'white',
                    'border': '4px solid black'
                    }
                )
            sdc += table_infos['post_sdc']
            page = math.floor((selection_infos["point"].name-1)/TABLE_MAX_ROWS)
            return sdc, page
        else:
            return table_infos['pre_sdc']+table_infos['post_sdc'], dash.no_update