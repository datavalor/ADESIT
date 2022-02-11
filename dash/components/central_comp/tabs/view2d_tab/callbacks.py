import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots

# Projection tools
from sklearn.decomposition import PCA
import prince
import plotly.graph_objects as go

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

from constants import *
from utils.cache_utils import *
import utils.viz.scatter_utils as scatter_gen
import utils.viz.heatmap_utils as heatmap_gen
import utils.viz.figure_utils as figure_utils
import utils.viz.selection_utils as selection_utils
from utils.data_utils import which_proj_type

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        [
            Output('view2d-xaxis-dropdown', 'options'),
            Output('view2d-yaxis-dropdown', 'options')
        ],
        [Input('left-attrs','value')],
        [State('session-id', 'children')]
    )
    def update_viz_options(left_attrs, session_id):
        logger.debug("update_viz_options")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate

        options=[{'label': col, 'title' : col, 'value': col} for col in dh['user_columns']]
        if left_attrs:
            for proj_name in PROJ_AXES:
                disabled=False
                if '1' in proj_name:
                    ext="1"
                    if len(left_attrs)<2: disabled=True
                if '2' in proj_name:
                    ext="2"
                    if len(left_attrs)<3: disabled=True
                options.append({'label': f"__proj:{which_proj_type(left_attrs, dh['user_columns'])}_{ext}", 'title' : proj_name ,'value': proj_name, 'disabled': disabled})
        return options, options

    # Callback for setting default x axis for visualization
    @dash.callback(
        Output('view2d-xaxis-dropdown', 'value'),
        [Input('left-attrs','value')],
        [State('view2d-xaxis-dropdown', 'value')]
    )
    def handle_default_xaxis(left_attrs, x_axis):
        logger.debug("set_default_axis_left callback")
        if x_axis is None and left_attrs: return left_attrs[0]
        elif not (x_axis is None) and not left_attrs: return None
        else: raise PreventUpdate

    # Callback for setting default y axis for visualization
    @dash.callback(
        Output('view2d-yaxis-dropdown', 'value'),
        [Input('right-attrs','value')],
        [State('view2d-yaxis-dropdown', 'value')]
    )
    def handle_default_yaxis(right_attrs, y_axis):
        logger.debug("set_default_axis_right callback")
        if y_axis is None and right_attrs: return right_attrs[0]
        elif not (y_axis is None) and not right_attrs: return None
        else: raise PreventUpdate

    @dash.callback(
        [
            Output('view2d_xaxis_resolution_slider', 'disabled'),
            Output('view2d_yaxis_resolution_slider', 'disabled'),
            Output('view2d_axes_have_changed', 'children')
        ],
        [
            Input('view2d-xaxis-dropdown', 'value'),
            Input('view2d-yaxis-dropdown', 'value')
        ],
        [State('session-id', 'children')]
    )
    def handle_view2d_axis(xaxis_column_name, yaxis_column_name, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug("handle_view2d_axis callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate

        # handling projections if needed
        join_axes = [xaxis_column_name, yaxis_column_name]
        if (PROJ_AXES[0] in join_axes or PROJ_AXES[1] in join_axes):
            if len(left_attrs)<2 and PROJ_AXES[0] in join_axes:
                raise PreventUpdate
            if len(left_attrs)<3 and PROJ_AXES[1] in join_axes:
                raise PreventUpdate

            proj_type = which_proj_type(left_attrs, dh['user_columns'])
            if proj_type=="PCA": # only numerical => PCA
                proj = PCA(n_components=2).fit_transform(df[left_attrs])
            elif proj_type=="MCA": # only categorical => MCA
                mca = prince.MCA(
                    n_components=2, n_iter=3, copy=True, check_input=True, engine='auto', random_state=42
                )
                proj = mca.fit_transform(df[left_attrs])
            else: # mixed types => FAMD
                famd = prince.FAMD(
                    n_components=2, n_iter=3, copy=True, check_input=True, engine='auto', random_state=27
                )
                proj = famd.fit_transform(df[left_attrs])
            df[PROJ_AXES]=proj
            dh['data']['df']=df
            overwrite_session_data_holder(session_id, dh, source='handle_graph')
        
        # handling disabled sliders
        xslider_disabled, yslider_disabled = True, True
        if xaxis_column_name is None: xslider_disabled=dash.no_update
        elif dh['user_columns'][xaxis_column_name].is_numerical(): xslider_disabled=False
        if yaxis_column_name is None: yslider_disabled=dash.no_update
        elif dh['user_columns'][yaxis_column_name].is_numerical(): yslider_disabled=False

        return xslider_disabled, yslider_disabled, ''

    # Callback for Graph Output (f,g->e)
    @dash.callback(
        Output('view2d-graph', 'figure'),
        [
            Input('data_updated', 'children'),
            Input('selection_changed', 'children'),
            Input('view2d_axes_have_changed', 'children'),
            Input('2d-viewmode', 'value'),
            Input('view2d_xaxis_resolution_slider', 'value'),
            Input('view2d_yaxis_resolution_slider', 'value'),
            Input('view','value'),
            Input('mode','value'),
        ],
        [
            State('left-attrs','value'),
            State('right-attrs','value'),
            State('view2d-graph', 'figure'),
            State('view2d-xaxis-dropdown', 'value'),
            State('view2d-yaxis-dropdown', 'value'),
            State('session-id', 'children')
        ]
    )
    def handle_view2d_graph(data_updated, selection_changed, axes_have_changed, d2_viewmode, xaxis_res, yaxis_res, view, mode, left_attrs, right_attrs, scatter_fig, xaxis_column_name, yaxis_column_name, session_id):
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        logger.debug("handle_view2d_graph callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate
        
        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate
        
        if yaxis_column_name is not None and xaxis_column_name is not None:
            df=dh['data']['df']
            selection_infos = session_data['selection_infos']
            
            selection_changed = (changed_id == 'selection_changed.children')
            if not selection_changed or (selection_changed and selection_infos['background_needs_update']):
                print("------------------------------------------- FFFFFFFFFUUUUUUUUUUUUUUUUL UPDATE")
                if dh['data']['df_free'] is not None:
                    if(d2_viewmode=="scatter"):
                        fig = scatter_gen.advanced_scatter(dh, xaxis_column_name, yaxis_column_name, xaxis_res, yaxis_res, view) 
                    else:
                        fig = heatmap_gen.advanced_heatmap(dh, xaxis_column_name, yaxis_column_name, xaxis_res, yaxis_res)  
                else:
                    if(d2_viewmode=="scatter"):
                        fig = scatter_gen.basic_scatter(dh, xaxis_column_name, yaxis_column_name, xaxis_res, yaxis_res)
                    else:
                        fig = heatmap_gen.basic_heatmap(dh, xaxis_column_name, yaxis_column_name, xaxis_res, yaxis_res)
            else:
                fig = figure_utils.gen_subplot_fig(
                    xaxis_column_name,
                    yaxis_column_name,
                    make_subplot_args={
                        'figure': go.Figure(scatter_fig)
                    }
                )
            selection_utils.add_selection_as_scatterpoints(fig, dh, selection_infos, xaxis_column_name, yaxis_column_name)
            selection_utils.add_selection_as_vertical_lines(
                fig, dh, selection_infos, 
                xaxis_column_name, '', 
                minmax=[0, len(df.index)],
                add_trace_args = {
                    'row': 1,
                    'col': 1
                },
                remove_previous_selections=False
            )
            selection_utils.add_selection_as_vertical_lines(
                fig, dh, selection_infos, 
                '', yaxis_column_name, 
                minmax=[0, len(df.index)],
                add_trace_args = {
                    'row': 2,
                    'col': 2
                },
                orientation = 'h',
                remove_previous_selections=False
            )
            return fig
        else:
            return go.Figure()
        
    #Callback for Selection Info
    @dash.callback(
        [
            Output('ntuples-selection', 'children'),
            Output('nviolating-selection', 'children')
        ],
        [
            Input('view2d-graph', 'selectedData'),
            Input('upload-form', 'contents'),
            Input('mode','value')
        ],
        [
            State('view2d-xaxis-dropdown', 'value'),
            State('view2d-yaxis-dropdown', 'value'),
            State('analyse_btn', 'n_clicks'),
            State('session-id', 'children')
        ]
    )
    def handle_lasso_box_selection(selected_data, contents, mode, xaxis, yaxis, n_clicks, session_id):
        logger.debug("handle_lasso_box_selection callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        label_column = G12_COLUMN_NAME if mode == 'color_involved' else G3_COLUMN_NAME
        
        dh=session_data['data_holder']
        if dh is None: raise PreventUpdate
        if str(selected_data)=='None':return "0", "0"

        points = selected_data.get("points")
        data = dh['data']['df']
        data[SELECTION_COLUMN_NAME] = 0
        selected_ids=[]
        for p in points:
            if "customdata" in p:
                selected_ids.append(p['customdata'][-1])
            elif "pointIndex" in p:
                selected_ids.append(p['pointIndex'])

        if label_column in data.columns:
            n_involved = len(data.loc[selected_ids].loc[data[label_column] > 0].index)
        else: 
            n_involved=0
        percent = round(100*n_involved/len(selected_ids))
        return str(len(selected_ids)), f"{n_involved} ({percent}%)"