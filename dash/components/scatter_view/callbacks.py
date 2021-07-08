import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Projection tools
from sklearn.decomposition import PCA
import prince

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *
import utils.figure_utils as fig_gen
from utils.data_utils import which_proj_type

def register_callbacks(app, plogger):
    logger = plogger

    @app.callback([Output('x-axis', 'options'),
                Output('y-axis', 'options')],
                [Input('left-attrs','value')],
                [State('session-id', 'children')])
    def update_viz_options(left_attrs, session_id):
        logger.debug("update_viz_options")
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            ctypes=dh["user_columns_type"]
            options=[{'label': col, 'title' : col, 'value': col} for col in dh["user_columns"]]
            if left_attrs:
                for proj_name in PROJ_AXES:
                    disabled=False
                    if '1' in proj_name and len(left_attrs)<2: disabled=True
                    else: ext="1"
                    if '2' in proj_name and len(left_attrs)<3: disabled=True
                    else: ext="2"
                    options.append({'label': f"__proj:{which_proj_type(left_attrs, ctypes)}_{ext}", 'title' : proj_name ,'value': proj_name, 'disabled': disabled})
            return options, options
        else:
            raise PreventUpdate

    # Callback for setting default x axis for visualization
    @app.callback(Output('x-axis', 'value'),
                [Input('left-attrs','value')],
                [State('x-axis', 'value')])
    def handle_default_xaxis(left_attrs, x_axis):
        logger.debug("set_default_axis_left callback")
        if x_axis is None and left_attrs: return left_attrs[0]
        elif not (x_axis is None) and not left_attrs: return None
        else: raise PreventUpdate

    # Callback for setting default y axis for visualization
    @app.callback(Output('y-axis', 'value'),
                [Input('right-attrs','value')],
                [State('y-axis', 'value')])
    def handle_default_yaxis(right_attrs, y_axis):
        logger.debug("set_default_axis_right callback")
        if y_axis is None and right_attrs: return right_attrs[0]
        elif not (y_axis is None) and not right_attrs: return None
        else: raise PreventUpdate

    # Callback for Graph Output (f,g->e)
    @app.callback([Output('main-graph', 'figure'),
                Output('clear-selection', 'disabled')],
                [Input('data-loaded','children'),
                Input('data-analysed', 'children'),
                Input('x-axis', 'value'),
                Input('y-axis', 'value'),
                Input('view','value'),
                Input('mode','value'),
                Input('selection_changed', 'children')],
                [State('left-attrs','value'),
                State('right-attrs','value'),
                State('session-id', 'children')])
    def handle_graph(data_updated, data_analysed, xaxis_column_name, yaxis_column_name, view, mode, selection_changed, left_attrs, right_attrs, session_id):
        logger.debug("handle_graph callback")
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=get_data(session_id)["data_holder"]
        if changed_id != 'data-loaded.children' and dh is not None and yaxis_column_name is not None and xaxis_column_name is not None:          
            df=dh["data"]
            ctypes = dh["user_columns_type"]
            
            # handling projections if needed
            join_axes = [xaxis_column_name, yaxis_column_name]
            if changed_id!='selection_changed.children' and (PROJ_AXES[0] in join_axes or PROJ_AXES[1] in join_axes):
                if len(left_attrs)<2 and PROJ_AXES[0] in join_axes:
                    raise PreventUpdate
                if len(left_attrs)<3 and PROJ_AXES[1] in join_axes:
                    raise PreventUpdate

                proj_type = which_proj_type(left_attrs, ctypes)
                if proj_type=="PCA": # only numerical => PCA
                    proj = PCA(n_components=2).fit_transform(df[left_attrs])
                elif proj_type=="MCA": # only categorical => MCA
                    mca = prince.MCA(
                        n_components=2,
                        n_iter=3,
                        copy=True,
                        check_input=True,
                        engine='auto',
                        random_state=42
                    )
                    proj = mca.fit_transform(df[left_attrs])
                else: # mixed types => FAMD
                    famd = prince.FAMD(
                        n_components=2,
                        n_iter=3,
                        copy=True,
                        check_input=True,
                        engine='auto',
                        random_state=27
                    )
                    proj = famd.fit_transform(df[left_attrs])
                df[PROJ_AXES]=proj
                dh["data"]=df
                overwrite_session_data_holder(session_id, dh)
            
            # if calculations have been made
            if label_column in df.columns :
                # data has been hovered
                if get_data(session_id)["selected_point"]["point"] is not None:
                    selection_infos = get_data(session_id)["selected_point"]
                    highlighted_points = [selection_infos["point"]]+selection_infos["in_violation_with"]
                    fig_base=fig_gen.advanced_scatter(df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, selection=True, session_infos=dh)  
                    fig = fig_gen.add_selection_to_scatter(fig_base, df, right_attrs, xaxis_column_name, yaxis_column_name, selected=highlighted_points)
                    return fig, False

                # data has been analysed
                fig=fig_gen.advanced_scatter(df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, view, session_infos=dh)  
                return fig, True
            # if showing raw data
            else :
                return fig_gen.basic_scatter(df, xaxis_column_name, yaxis_column_name), True
        elif dh is not None and yaxis_column_name is None and xaxis_column_name is None:
            return {}, True
        else:
            raise PreventUpdate

    # Callback for SQL translation
    @app.callback([Output('sql-query', 'value'),
                Output('sql-div','style')],
                [Input('main-graph', 'selectedData'),
                Input('data-loaded', 'children')],
                [State('x-axis', 'value'),
                State('y-axis', 'value')])
    def handle_sql_query(selected_data, data_loaded, xaxis_column_name, yaxis_column_name):
        if str(selected_data)!="None" and selected_data.get("range") is not None:
            selection_range = selected_data.get("range")
            query = "SELECT * FROM Table WHERE "
            if selection_range.get('x') is not None: 
                query += str(xaxis_column_name) + " BETWEEN " + str(selection_range.get('x')[0]) + " AND "+ str(selection_range.get('x')[1])
                query += " AND " + str(yaxis_column_name) + " BETWEEN " + str(selection_range.get('y')[0]) + " AND "+ str(selection_range.get('y')[1])
            elif selection_range.get('x3') is not None:
                query += str(xaxis_column_name) + " BETWEEN " + str(selection_range.get('x3')[0]) + " AND "+ str(selection_range.get('x3')[1])
                query += " AND " + str(yaxis_column_name) + " BETWEEN " + str(selection_range.get('y4')[0]) + " AND "+ str(selection_range.get('y4')[1])
            return query, None
        else:
            return "", {}
        
    #Callback for Selection Info
    @app.callback([Output('ntuples-selection', 'children'),
                Output('nviolating-selection', 'children')],
                [Input('main-graph', 'selectedData'),
                Input('upload-form', 'contents'),
                Input('mode','value')],
                [State('x-axis', 'value'),
                State('y-axis', 'value'),
                State('analyse_btn', 'n_clicks'),
                State('session-id', 'children')])
    def handle_selection(selected_data, contents, mode, xaxis, yaxis, n_clicks, session_id):
        logger.debug("update_select callback")
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=get_data(session_id)["data_holder"]
        if dh is not None and str(selected_data)!="None":
            points = selected_data.get("points")
            data = dh["data"]
            data[SELECTION_COLUMN_NAME] = 0 
            selected_ids=[p["customdata"] for p in points if "customdata" in p]
            if label_column in data.columns:
                n_involved = len(data.loc[selected_ids].loc[data[label_column] > 0].index)
            else: 
                n_involved=0
            data[SELECTION_COLUMN_NAME][selected_ids]=1
            dh["data"]=data
            overwrite_session_data_holder(session_id, dh)
            return str(len(selected_ids)), str(n_involved)
        else:
            if dh is not None:
                dh["data"][SELECTION_COLUMN_NAME] = 0 
                overwrite_session_data_holder(session_id, dh)
            return "0", "0"