import dash
import math

from constants import *
import utils.viz.figure_utils as figure_utils

default_style_data_conditional = [
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
        # 'border': '3px solid black'
    },
    {
        'if': {
            'state': 'active',
            'filter_query': '{_violating_tuple} = 1' 
        },
        'backgroundColor': SELECTED_COLOR_BAD,
        'color': 'black',
        'border': '3px solid black'
    }
]

id_column_sdc = {
    'if': { 'column_id': ADESIT_INDEX },
    'backgroundColor': 'white',
    'fontStyle': 'italic',
    'color': 'black'
}

def data_preprocessing_for_table(session_infos, data_key='df', by_data_type=True, output_df=None):
    if output_df is None: output_df = session_infos['data'][data_key].copy()
    if by_data_type:
        columns = []
        for column in output_df.columns:
            if column in session_infos['user_columns']:
                columns.append({'name': [session_infos['user_columns'][column].get_type(), column], 'id': column, 'hideable':True})
        columns = sorted(columns, key=lambda x: "".join(x["name"][0]), reverse=False)
        pre_sdc = default_style_data_conditional.copy()
        post_sdc = [id_column_sdc]
    else:
        Xs, Ys = session_infos["X"], session_infos["Y"]
        user_columns_names=list(session_infos['user_columns'].keys())
        for c in Xs+Ys: user_columns_names.remove(c)
        columns_other = [{"name": ["Other(s)", column], "id": column} for column in user_columns_names]
        columns_X = [{"name": ["Feature(s)", column], "id": column} for column in Xs]
        columns_Y = [{"name": ["Target(s)", column], "id": column} for column in Ys]
        columns = columns_other+columns_X+columns_Y

        white_back = []
        if session_infos['data']['df_free'] is not None:
            for c in user_columns_names:
                white_back.append({
                    'if': { 'column_id': c },
                    'backgroundColor': 'white',
                    'color': 'black'
                })
                white_back.append({
                    'if': { 'state': 'active', 'column_id': c },
                    'backgroundColor': 'white',
                    'color': 'black',
                    'border': '3px solid black'
                })

        pre_sdc = default_style_data_conditional.copy()
        post_sdc = white_back+[id_column_sdc.copy()]


    output_df[TABLE_ROWNUM_NAME] = output_df.reset_index(drop=True).index
    hidden_columns = [TABLE_ROWNUM_NAME]
    if G12_COLUMN_NAME in output_df.columns:
            hidden_columns.append(G12_COLUMN_NAME)
            columns = columns+[{'name': ['system', G12_COLUMN_NAME], 'id': G12_COLUMN_NAME}]   
    columns = columns+[{'name': ['system', TABLE_ROWNUM_NAME], 'id': TABLE_ROWNUM_NAME}]
    columns = [{'name': ['', 'id'], 'id': ADESIT_INDEX, "hideable":False}]+columns
    output_df['id'] = output_df.index
    output_df = output_df[[c['id'] for c in columns]]

    table_data = {
        'df_table': output_df,
        'pre_sdc': pre_sdc,
        'post_sdc': post_sdc,
    } 

    return columns, hidden_columns, table_data

def generate_selection_sdc(session_infos, selection_infos, table_data):
    if selection_infos['point'] is None: return table_data['pre_sdc']+table_data['post_sdc'], dash.no_update

    selection_style = figure_utils.choose_selected_point_style(session_infos, selection_infos)[:2]
    sdc = table_data['pre_sdc']
    sdc.append(
        {
            'if': {
                'filter_query': f'{{id}} = {selection_infos["point"].name}'
            }, 
            'backgroundColor': selection_style[0],
            'color': selection_style[1],
            'border': '3px solid black'
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
            'border': '3px solid black'
            }
        )
    sdc += table_data['post_sdc']
    row_num = table_data['df_table'].loc[selection_infos["point"].name][TABLE_ROWNUM_NAME]
    page = math.floor((row_num)/TABLE_MAX_ROWS)

    return sdc, page