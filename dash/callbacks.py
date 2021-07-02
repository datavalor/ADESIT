from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash, dash_table
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import pandas as pd

import logging
logging.basicConfig()

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None 
import numpy as np
import base64
import io
import math

import pydataset

# Personnal imports
import fastg3.crisp as g3crisp
import fastg3.ncrisp as g3ncrisp
import figure_generator as fig_gen
from utils import parse_attributes_settings, num_or_cat

# Constants definition
G12_COLUMN_NAME = "_violating_tuple"
G3_COLUMN_NAME = "_g3_to_remove"
SELECTION_COLUMN_NAME = "_selected"
ADESIT_COLUMNS = [G12_COLUMN_NAME, G3_COLUMN_NAME, SELECTION_COLUMN_NAME]

TSNE_AXES = ['__t-SNE1', '__t-SNE2']
PCA_AXES = ['__PCA1', '__PCA2']
VIZ_PROJ = PCA_AXES+TSNE_AXES

dataset_names={
    'iris':'iris',
    'housing': 'Housing',
    'tobacco': 'Tobacco',
    'kidney': 'kidney'
}

def register_callbacks(app, cache, logging_level=logging.INFO):
    logger=logging.getLogger('adesit_callbacks')
    logger.setLevel(logging_level)

    def get_data(session_id, pydata=False, clear=False, filename=None, contents=None, copy=None):    
        @cache.memoize()
        def handle_data(session_id):
            if not copy is None: 
                logger.debug("/!\ replacing stored data /!\\")
                return copy
            logger.debug(f"/!\ full data loading of {filename} /!\\")
            if pydata:
                df = pydataset.data(dataset_names[filename])
                data_holder = {
                    "data": df
                }
            elif not filename is None:
                _, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                try:
                    if 'csv' in filename:
                        # Assume that the user uploaded a CSV file
                        df = pd.read_csv(
                            io.StringIO(decoded.decode('utf-8')))
                    elif 'xls' in filename:
                        # Assume that the user uploaded an excel file
                        df = pd.read_excel(io.BytesIO(decoded))
                except Exception as e:
                    logger.error(e)
                    data_holder = None
                data_holder = {
                    "data": df,
                    "graph": None
                }
            else:
                data_holder = None

            return {
                "data_holder": data_holder,
                "graphs": {},
                "thresolds_settings": {},
                "table_data": None,
                "selected_point": None
            }

        if clear: 
            cache.delete_memoized(handle_data, session_id)
            return None
        else:
            return handle_data(session_id)

    def clear_session(session_id):
        get_data(session_id, clear=True)

    def overwrite_session_data_holder(session_id, dh=None):
        session_data=get_data(session_id)
        session_data["data_holder"]=dh
        clear_session(session_id)
        get_data(session_id, copy=session_data)

    def overwrite_session_graphs(session_id, graphs={}):
        session_data=get_data(session_id)
        session_data["graphs"]=graphs
        clear_session(session_id)
        get_data(session_id, copy=session_data)

    def overwrite_session_settings(session_id, thresolds_settings={}):
        session_data=get_data(session_id)
        session_data["thresolds_settings"]=thresolds_settings
        clear_session(session_id)
        get_data(session_id, copy=session_data)

    def overwrite_tabledata(session_id, table=None):
        session_data=get_data(session_id)
        session_data["table_data"]=table
        clear_session(session_id)
        get_data(session_id, copy=session_data)
    
    def overwrite_selected_point(session_id, selection=None):
        session_data=get_data(session_id)
        session_data["selected_point"]=selection
        clear_session(session_id)
        get_data(session_id, copy=session_data)

    @app.callback([Output('data-loaded','children'),
                Output('dataset_confirm', 'children'),
                Output('left-attrs', 'disabled'),
                Output('right-attrs', 'disabled'),
                Output('collapse-viz', 'is_open')],
                [Input('toy-dataset-iris','n_clicks'),
                Input('toy-dataset-housing','n_clicks'),
                Input('toy-dataset-tobacco','n_clicks'),
                Input('toy-dataset-kidney','n_clicks'),
                Input('upload-form', 'contents')],
                [State('upload-form', 'filename'),
                State('session-id', 'children')])
    def handle_data(iris, housing, tobacco, kidney, contents, filename, session_id):
        logger.debug('handle_data callback')
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        clear_session(session_id)
        if "toy-dataset" in changed_id:
            toy_dataset = changed_id.split(".")[0].split("-")[-1]
            clear_session(session_id)
            dh = get_data(session_id, filename=toy_dataset, pydata=True)["data_holder"]
            n = len(dh["data"].index) if dh is not None else 0
            return toy_dataset, fig_gen.dataset_infos(toy_dataset, n, len(dh["data"].columns)), False, False, True
        elif filename is not None: 
            clear_session(session_id)
            dh = get_data(session_id, filename=filename, contents=contents)["data_holder"]
            n = len(dh["data"].index) if dh is not None else 0
            return filename, fig_gen.dataset_infos(filename, n, len(dh["data"].columns)), False, False, True
        else:
            raise PreventUpdate

    # Callback for data update and calculations ()
    @app.callback([Output('loading_screen','fullscreen'),
                Output('alert-timeout', 'is_open'),
                Output('data-analysed', 'children'),
                Output('learnability_indicator', 'figure'),
                Output('g2_indicator', 'figure'),
                Output('g1_indicator', 'figure'),
                Output('ntuples_involved', 'children'),
                Output('collapse-stats', 'is_open'),
                Output('mode', 'disabled'),
                Output('view', 'disabled')],
                [Input('data-loaded','children'),
                Input('analyse_btn','n_clicks')],
                [State('left-attrs','value'),
                State('right-attrs','value'),
                State('thresold_table_features', 'data'),
                State('thresold_table_target', 'data'),
                State('g3_computation','value'),
                State('learnability_indicator', 'figure'),
                State('g2_indicator', 'figure'),
                State('g1_indicator', 'figure'),
                State('ntuples_involved', 'children'),
                State('session-id', 'children')])
    def handle_analysis(data_updated, n_clicks, left_attrs, right_attrs, left_tols, right_tols, g3_computation, learnability_indicator, g2_indicator, g1_indicator, ncountexample_indicator, session_id):
        logger.debug("handle_analysis callback")
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        is_open = False
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            df = dh["data"]
            # API Calculations if requested
            if changed_id=='analyse_btn.n_clicks' and left_attrs and right_attrs:
                # Init calc df
                df_calc = df.copy()
                n_tuples = len(df_calc.index)
                df_calc[G12_COLUMN_NAME] = 0
                df_calc[G3_COLUMN_NAME] = 0                
                
                # Setting left and right tolerances
                xparams=parse_attributes_settings(left_tols, df)
                yparams=parse_attributes_settings(right_tols, df)

                # Setting up solver
                VPE = g3ncrisp.create_vpe_instance(
                    df, 
                    xparams, 
                    yparams,
                    verbose=False
                )
                rg3 = g3ncrisp.RSolver(VPE, precompute=True)

                # Enumerating violating pairs
                vps = rg3.get_vps()
                dh["graph"] = rg3.get_vps(as_map=True)

                involved_tuples = np.unique(np.array(vps))

                # Creating figures
                if involved_tuples is not None:
                    df_calc[G12_COLUMN_NAME][involved_tuples] = 1
                    # Computing G1, G2
                    ncounterexample = involved_tuples.size
                    ncounterexample_fig = f"({ncounterexample} tuples over {n_tuples} are involved in at least one counterexample)"
                    g1 = round(len(vps)/n_tuples**2,4)
                    g1_fig=fig_gen.bullet_indicator(value=(1-g1)*100, reference=g1_indicator['data'][0]['value'])
                    g2 = round(ncounterexample/n_tuples, 4)
                    g2_fig=fig_gen.bullet_indicator(value=(1-g2)*100, reference=g2_indicator['data'][0]['value'])
                    # Computing G3
                    if g3_computation=="exact": 
                        cover = rg3.exact(method="wgyc", return_cover=True)
                        g3 = len(cover)/n_tuples
                        if not g3 is None:
                            accuracy_ub = 1-g3
                            g3_indicator = fig_gen.gauge_indicator(value=accuracy_ub*100, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                        else:
                            is_open=True
                            g3_indicator = fig_gen.gauge_indicator(value=0, reference=learnability_indicator['data'][0]['value'], lower_bound=0, upper_bound=0)
                    else:
                        gic, approx2 = rg3.upper_bound(method="gic", return_cover=True), rg3.upper_bound(method="2approx", return_cover=True)
                        cover = gic if len(gic)<len(approx2) else approx2
                        g3_up = len(cover)/n_tuples
                        g3_lb = rg3.lower_bound(method="maxmatch")
                        lb_acc, ub_acc = (1-g3_up)*100, (1-g3_lb)*100
                        g3_indicator = fig_gen.gauge_indicator(value=(lb_acc+ub_acc)*0.5, reference=learnability_indicator['data'][0]['value'], lower_bound=lb_acc, upper_bound=ub_acc)

                    # Merging
                    df_calc[G3_COLUMN_NAME][cover] = 1
                    dh["data"]=df_calc
                    overwrite_session_data_holder(session_id, dh)
                    overwrite_session_graphs(session_id)
                    overwrite_selected_point(session_id)
                    return True, is_open, "Done", g3_indicator, g2_fig, g1_fig, ncounterexample_fig, True, False, False
                else:
                    is_open=True
            overwrite_session_data_holder(session_id, dh)
            overwrite_session_graphs(session_id)
            default_g3 = fig_gen.gauge_indicator(reference=learnability_indicator['data'][0]['value'])
            default_g2 = fig_gen.bullet_indicator(reference=g2_indicator['data'][0]['value'])
            default_g1 = fig_gen.bullet_indicator(reference=g1_indicator['data'][0]['value'])
            default_ncounterexample = ""
            overwrite_selected_point(session_id)
            return True, is_open, "Done", default_g3, default_g2, default_g1, default_ncounterexample, False, True, True
        else:
            raise PreventUpdate

    # Callback for Dimensions (attribute) options in dropdowns (b->c,d,f)
    @app.callback([Output('right-attrs', 'options'),
                Output('left-attrs', 'options'),
                Output('right-attrs', 'value'),
                Output('left-attrs', 'value')],
                [Input('data-loaded','children')],
                [State('session-id', 'children')])
    def update_options(data_loaded, session_id):
        logger.debug("update_options")
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            df_parsed=dh["data"]
            options=[{'label': str(col), 'title' : str(df_parsed.dtypes[str(col)]) ,'value': str(col)} for col in df_parsed.columns]
            return options, options, None, None
        else:
            return [], [], None, None

        # Callback for Left Tolerances Output ()
    @app.callback([Output('thresold_table_features', 'data'),
                Output('thresold_table_target', 'data')],
                [Input('data-loaded','children'),
                Input('left-attrs','value'),
                Input('right-attrs','value')],
                [State('thresold_table_features', 'data'),
                State('thresold_table_target', 'data'),
                State('session-id', 'children')])
    def handle_thresolds(data_loaded, left_attrs, right_attrs, fthresolds, tthresolds, session_id):
        logger.debug("handle_thresolds callback")

        # Detect which attributes changed
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if changed_id=='data-loaded.children': return [], []
        if changed_id=='left-attrs.value': inputtols,inputattr=fthresolds,left_attrs
        else: inputtols, inputattr=tthresolds, right_attrs

        # Update tolerances
        dh=get_data(session_id)["data_holder"]
        if inputattr is not None and dh is not None:
            df=dh["data"]

            # Retrieve previous settings
            new_attributes_settings = parse_attributes_settings(inputtols, df)
            attributes_settings = get_data(session_id)["thresolds_settings"]
            if new_attributes_settings is not None:
                for attr in new_attributes_settings.keys(): attributes_settings[attr] = new_attributes_settings[attr]
                overwrite_session_settings(session_id, attributes_settings)            
            
            outuput_thresolds = []
            for attr in inputattr:
                attr_type = num_or_cat(attr, df)
                if attr_type is not None:
                    if attr_type == "categorical":
                        outuput_thresolds.append({'attribute': attr, 'absolute': 'is', 'relative': 'categorical...'})
                    elif attr_type == "numerical":
                        outuput_thresolds.append({'attribute': attr, 
                            'absolute': attributes_settings.get(attr, {"params":[0,0]})["params"][0], 
                            'relative': attributes_settings.get(attr, {"params":[0,0]})["params"][1]
                        })
            
            if changed_id=='left-attrs.value': return outuput_thresolds, tthresolds
            else: return fthresolds, outuput_thresolds
        else:
            if changed_id=='left-attrs.value': return [], tthresolds
            else: return fthresolds, []

    @app.callback([Output('x-axis', 'options'),
                Output('y-axis', 'options')],
                [Input('left-attrs','value')],
                [State('session-id', 'children')])
    def update_viz_options(left_attrs, session_id):
        logger.debug("update_viz_options")
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            df_parsed=dh["data"]
            options=[{'label': str(col), 'title' : str(df_parsed.dtypes[str(col)]) ,'value': str(col)} for col in df_parsed.columns if col not in ADESIT_COLUMNS]
            if left_attrs:
                for proj_name in VIZ_PROJ:
                    disabled=False
                    if '1' in proj_name and len(left_attrs)<2: disabled=True
                    elif '2' in proj_name and len(left_attrs)<3: disabled=True
                    options.append({'label': proj_name, 'title' : proj_name ,'value': proj_name, 'disabled': disabled})
            return options, options
        else:
            raise PreventUpdate

    # Callback for Analyse button state
    @app.callback([Output('analyse_btn', 'disabled'),
                Output('g3_computation', 'disabled')],
                [Input('left-attrs','value'),
                Input('right-attrs','value')])
    def handle_analyse_btn_state(left_attrs, right_attrs):
        logger.debug("analyse_btn_state callback")
        if left_attrs and right_attrs: return False, False
        else: return True, True

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
                Input('main-graph','clickData'),
                Input('clear-selection','n_clicks')],
                [State('left-attrs','value'),
                State('right-attrs','value'),
                State('session-id', 'children')])
    def handle_graph(data_updated, data_analysed, xaxis_column_name, yaxis_column_name, view, mode, clickData, clear_selection, left_attrs, right_attrs, session_id):
        logger.debug("handle_graph callback")
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME

        if changed_id == 'clear-selection.n_clicks': 
            overwrite_selected_point(session_id, selection=None)
        
        dh=get_data(session_id)["data_holder"]
        if changed_id != 'data-loaded.children' and dh is not None and yaxis_column_name is not None and xaxis_column_name is not None:          
            graph_df=dh["data"]
            
            # handling projections
            if left_attrs:
                join_axes = [xaxis_column_name, yaxis_column_name]
                if len(left_attrs)<3 and ('__PCA2' in join_axes or  '__t-SNE2' in join_axes):
                    raise PreventUpdate
                if len(left_attrs)<2 and ('__PCA1' in join_axes or  '__t-SNE1' in join_axes):
                    raise PreventUpdate
                if "PCA" in "".join(join_axes):
                    proj = PCA(n_components=2).fit_transform(graph_df[left_attrs])
                    graph_df[PCA_AXES]=proj
                if "t-SNE" in "".join([xaxis_column_name, yaxis_column_name]):
                    proj = TSNE(n_components=2, random_state=27).fit_transform(graph_df[left_attrs])
                    graph_df[TSNE_AXES]=proj
            
            # if calculations have been made
            if label_column in graph_df.columns :
                # data has been hovered
                if get_data(session_id)["selected_point"] is not None or (changed_id == 'main-graph.clickData' and clickData is not None):
                    highlighted_points = None
                    if changed_id == 'main-graph.clickData' and clickData is not None:
                        if 'points' not in clickData: raise PreventUpdate
                        clickData=clickData['points'][0]
                        points=graph_df.loc[(graph_df[xaxis_column_name]==clickData['x']) & (graph_df[yaxis_column_name]==clickData['y'])]
                        points=list(points.index)
                        points=[point for point in points if point in dh["graph"]]
                        if points:
                            hovered_point=points[0]
                            hovered_point_conflicts=dh["graph"][hovered_point]
                            highlighted_points=[hovered_point]+hovered_point_conflicts
                            overwrite_selected_point(session_id, selection=highlighted_points)
                    else:
                        highlighted_points = get_data(session_id)["selected_point"]
                        
                    if highlighted_points is not None:
                        fig_base=fig_gen.advanced_scatter(graph_df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, selection=True)  
                        fig = fig_gen.add_selection_to_scatter(fig_base, graph_df, right_attrs, xaxis_column_name, yaxis_column_name, selected=highlighted_points)
                        return fig, False

                # data has been analysed
                fig=fig_gen.advanced_scatter(graph_df, label_column, right_attrs, xaxis_column_name, yaxis_column_name, view)  
                return fig, True
            # if showing raw data
            else :
                return fig_gen.basic_scatter(graph_df, xaxis_column_name, yaxis_column_name), True
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
            style = {}
            return "", style
        
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
                

    # Callback for Table Output (b,c,d,e,f,g->h) 
    @app.callback(Output('table-container', 'children'),
                [Input('data-loaded','children'),
                Input('main-graph','selectedData'),
                Input('view','value'),
                Input('mode','value')],
                [State('session-id', 'children')])
    def handle_table(data_updated, selected_data, view, mode, session_id):
        logger.debug("handle_table callback")
        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=get_data(session_id)["data_holder"]
        if dh is not None:
            data=dh["data"]
            # select_problematics/non problematics according to mode and view
            if label_column in data.columns:
                if view == 'NP': data=data.loc[data[label_column] == 0]
                elif view == 'P': data=data.loc[data[label_column] > 0]
            
            if SELECTION_COLUMN_NAME in data.columns and len(np.unique(data[SELECTION_COLUMN_NAME]))!=1:
                data=data.loc[data[SELECTION_COLUMN_NAME]>0]

        
            columns = [{"name": column, "id": column} for column in data.columns if column not in [G12_COLUMN_NAME, G3_COLUMN_NAME, SELECTION_COLUMN_NAME]]

            output_df = data[[c["name"] for c in columns]].copy()
            overwrite_tabledata(session_id, output_df)

            n_rows=len(output_df.index)
            rows_per_page = 15
            table = dash_table.DataTable(
                id="dataTable",
                export_format='csv',
                columns=columns,
                page_current=0,
                page_size=rows_per_page,
                page_count=math.ceil(n_rows/rows_per_page),
                page_action='custom')
            return table
        else:
            raise PreventUpdate
    
    @app.callback(
    Output('dataTable', 'data'),
    [Input('dataTable', "page_current"),
    Input('dataTable', "page_size")],
    [State('session-id', 'children')])
    def update_table(page_current,page_size, session_id):
        logger.debug("update_table callback")
        table_data=get_data(session_id)["table_data"]
        if table_data is not None:
            return table_data.iloc[
                page_current*page_size:(page_current+ 1)*page_size
            ].to_dict('records')
# %%
