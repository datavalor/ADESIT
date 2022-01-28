import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils

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
        
        dh = session_data["data_holder"]
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

    @dash.callback(
        Output('time-attribute-dropdown', 'options'),
        [Input('data-loaded','children')],
        [State('session-id', 'children')]
    )
    def handle_time_attribute_options(data_loaded, session_id):
        logger.debug("handle_time_attribute_options callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh = session_data["data_holder"]
        if dh is not None:
            time_cols_options = [{'label': 'No attribute selected', 'value': 'noattradesit'}]
            for time_col in dh["time_columns"]:
                time_cols_options.append({'label': time_col, 'value': time_col})
            return time_cols_options
        else:
            raise PreventUpdate

    @dash.callback(
        [Output('time-period-dropdown', 'options'),
        Output('time-range', 'children')],
        [Input('time-attribute-dropdown', 'value')],
        [State('session-id', 'children')]
    )
    def handle_time_period_options(time_attribute, session_id):
        logger.debug("handle_time_attribute_options callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh = session_data["data_holder"]
        if dh is not None:
            df = dh["full_data"]
            period_options = [{'label': 'Don\'t group', 'value': 'nogroup'}]
            if(time_attribute=='noattradesit'):
                df.index = df[ADESIT_INDEX]
                df = df.sort_index()
                dh["data"] = df
                dh["full_data"] = df
                overwrite_session_data_holder(session_id, dh)
                return period_options, "Attribute period: N/A"
            else:
                # setting time as index
                df.index = pd.to_datetime(df[time_attribute], infer_datetime_format=True)#.astype("datetime64[ns]").astype("int64")
                df = df.sort_index()

                # finding max and min time and delttas
                time_min, time_max = df.index.min(), df.index.max()
                diff = df.index[1:]-df.index[:-1]
                min_delta, max_delta = min(diff), max(diff)

                for time_cut in DEFAULT_TIME_CUTS:
                    td = DEFAULT_TIME_CUTS[time_cut]["timedelta"]
                    if td>=10*min_delta:
                        period_options.append({'label': time_cut, 'value': time_cut})

                # saving data
                df.index = df.index.astype("datetime64[ns]").view("int64")
                df = df.sort_index()
                dh["data"] = df
                dh["full_data"] = df
                overwrite_session_data_holder(session_id, dh)

                return period_options, f'{time_min} → {time_max}'
        else:
            raise PreventUpdate

    @dash.callback(
        [Output("current-time-range", "children"),
        Output('current-time-range-number', 'children'),
        Output('max-time-range-number', 'children')],
        [Input('time-period-dropdown', 'value'),
        Input('time-backward-button', 'n_clicks'),
        Input('time-forward-button', 'n_clicks')],
        [State('session-id', 'children')]
    )
    def handle_time_period_value(time_period_value, bf_nclicks, bb_nclicks, session_id):
        logger.debug("handle_time_period_value callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]

        dh = session_data["data_holder"]
        if dh is not None:
            time_infos = dh["time_infos"]
            if "n_clicks" in changed_id:
                curr_index = time_infos["current_time_period"]
                periods_list = time_infos["time_periods_list"]
                if changed_id=='time-backward-button.n_clicks' and curr_index>0:
                    curr_index-=1 
                elif changed_id=='time-forward-button.n_clicks' and curr_index<len(periods_list)-2:
                    curr_index+=1 
                period_min, period_max = periods_list[curr_index], periods_list[curr_index+1]
                period_min64, period_max64 = period_min.to_datetime64().view("int64"), period_max.to_datetime64().view("int64")
                dh["data"]=dh["full_data"].loc[period_min64:period_max64]
                dh["time_infos"]["current_time_period"]=curr_index
            else:
                if time_period_value=="nogroup":
                    dh["time_infos"] = None
                    dh["data"] = dh["full_data"]
                    overwrite_session_data_holder(session_id, dh)
                    return f'N/A', "1", "1"
                else:
                    df = dh["full_data"]
                    time_min, time_max = df.index.min(), df.index.max()
                    freq=DEFAULT_TIME_CUTS[time_period_value]["freq_symbol"]
                    list = pd.date_range(time_min, time_max, freq=freq)
                    period_min, period_max = list[0], list[1]
                    period_min64, period_max64 = period_min.to_datetime64().view("int64"), period_max.to_datetime64().view("int64")
                    dh["data"]=dh["full_data"].loc[period_min64:period_max64]
                    dh["time_infos"]= {
                        "time_periods_list": list,
                        "current_time_period": 0,
                        "date_format": DEFAULT_TIME_CUTS[time_period_value]["date_format"]
                    }
            overwrite_session_data_holder(session_id, dh)
            time_infos = dh["time_infos"]
            n_tuples = len(dh["data"].index)
            n_periods = len(time_infos["time_periods_list"])-1
            date_format = time_infos["date_format"]
            curr_index = time_infos["current_time_period"]
            return f'{data_utils.format_date_period(period_min, period_max, date_format)} ({n_tuples} tuples)', curr_index+1, n_periods
        else:
            raise PreventUpdate

    @dash.callback(
        [Output("time-backward-button", "disabled"),
        Output('time-forward-button', 'disabled')],
        [Input('current-time-range', 'children')],
        [State('session-id', 'children')]
    )
    def handle_time_period_buttons_state(current_time_range, session_id):
        logger.debug("handle_time_period_buttons_state callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        time_infos = session_data["data_holder"]["time_infos"]
        if time_infos is not None:
            list_len = len(time_infos["time_periods_list"])
            curr_index = time_infos["current_time_period"]
            if list_len==2:
                return True, True
            if curr_index==0:
                return True, False
            elif curr_index==list_len-2:
                return False, True
            else:
                return False, False
        else:
            return True, True