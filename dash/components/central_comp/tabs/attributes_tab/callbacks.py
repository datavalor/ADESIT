import dash
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash.exceptions import PreventUpdate

from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go

from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.viz.histogram_utils as histogram_utils
import utils.viz.figure_utils as figure_utils

def register_callbacks(plogger):
    logger = plogger

    def generate_attribute_histogram(attr, attr_name, data_holder):
        figure = go.Figure()

        resolution, minmax = 10, attr.get_minmax(original=True)
        if attr.is_numerical():
            attr_min, attr_max = attr.get_minmax(original=False)
            figure.add_vrect(
                x0=attr_min, x1=attr_max,
                fillcolor="green", 
                opacity=0.1, 
                line_width=0
            )
        

        bins, bins_counts = histogram_utils.compute_1d_histogram(data_holder, attr_name, resolution, minmax=minmax, df=data_holder['df_full'])
        if data_holder['data']['df_prob'] is None:
            histogram_utils.add_basic_histograms(figure, data_holder, attr_name, resolution, minmax=minmax)
            upper_bound = list(figure.data[0].y)
        elif data_holder['data']['df'] is not None:
            histogram_utils.add_advanced_histograms(figure, data_holder, attr_name, resolution, minmax=minmax)
            upper_bound = [a+b for a,b in zip(figure.data[0].y, figure.data[1].y)]
        else:
            upper_bound = [0]*len(bins_counts)


        for i in range(len(bins_counts)):
            bins_counts[i]-=upper_bound[i]
            upper_bound[i]=upper_bound[i]+bins_counts[i]
        histogram_utils.add_basic_histograms(
            figure,
            data_holder,
            attr_name,
            resolution,
            minmax=attr.get_minmax(original=True),
            bar_args={'opacity': 0.5},
            computed_histogram=[bins, bins_counts]
        )

        figure.update_layout(
            title=f'{attr_name} ({attr.get_type()})',
            margin={'l': 0, 'b': 0, 't': 60, 'r': 0},
            height=280,
            barmode='stack',
            showlegend=False,
        )
        figure.update_xaxes(range=attr.get_minmax(original=True, auto_margin=True), fixedrange=True)
        figure.update_yaxes(range=[0, 1.1*max(upper_bound)])#, fixedrange=True)
        return figure

    def add_selection_to_histogram(figure, session_infos, attr_name, selection_infos):
        # Deleting previous selections
        figure.data = tuple([datum for datum in figure.data if datum['name']!='selection'])

        # Drawing lines
        point = selection_infos['point']
        if point is not None:
            in_violation_with = selection_infos['in_violation_with']
            n_tuples = len(session_infos['df_full'].index)
            point_line_color = figure_utils.choose_selected_point_style(session_infos, selection_infos)[0]
            figure.add_trace(
                go.Scatter(
                    x=[point[attr_name], point[attr_name]], 
                    y=[0,n_tuples], 
                    mode='lines', 
                    line=dict(color=point_line_color, width=3),
                    name='selection'
                ),
            )
            for _, row in in_violation_with.iterrows():
                figure.add_trace(
                    go.Scatter(
                        x=[row[attr_name],row[attr_name]], 
                        y=[0,n_tuples], 
                        mode='lines', 
                        line=dict(color=CE_COLOR, width=2),
                        name='selection'
                    ),
                )
        return figure


    @dash.callback(
        Output({'type': 'minmax_changed', 'index': MATCH}, 'children'),
        [Input({'type': 'minmax_slider', 'index': MATCH}, 'value'),
        Input({'type': 'minmax_slider', 'index': MATCH}, 'id')],
        [State('session-id', 'children')]
    )
    def attributes_minmax_update(slider_range, slider_id, session_id):
        logger.debug("attributes_minmax_update callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate      
        
        dh = session_data['data_holder']
        if dh is not None:
            attr_name=slider_id["index"]
            if dh['user_columns'][attr_name].get_minmax()!=slider_range:
                dh['user_columns'][attr_name].minmax = slider_range
                overwrite_session_data_holder(session_id, dh, source='attributes_minmax_update')
                return ""
            else:
                raise PreventUpdate
        else:
            raise PreventUpdate

    @dash.callback(
        Output({'type': 'attr_histogram', 'index': ALL}, 'figure'),
        [Input('data_updated', 'children'),
        Input('data-analysed', 'children'),
        Input('selection_changed', 'children')],
        [State({'type': 'attr_histogram', 'index': ALL}, 'id'),
        State({'type': 'attr_histogram', 'index': ALL}, 'figure'),
        State('session-id', 'children')]
    )
    def attributes_histograms_update(filters_changed, data_analysed, selection_changed, hists_ids, hists_figures, session_id):
        logger.debug("attributes_histograms_update callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate  

        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] 
        
        dh = session_data['data_holder']
        if dh is not None:
            figures = []
            if changed_id == 'selection_changed.children':
                for hist_id, figure_dict in zip(hists_ids, hists_figures):
                    figure = go.Figure(figure_dict)
                    attr_name = hist_id['index']
                    figure = add_selection_to_histogram(figure, dh, attr_name, get_data(session_id)["selection_infos"])
                    figures.append(figure)
            else: 
                for hist_id in hists_ids:
                    attr_name = hist_id['index']
                    attr = dh['user_columns'][attr_name]
                    figure = generate_attribute_histogram(attr, attr_name, dh)
                    figures.append(figure)
            return figures
        else:
            raise PreventUpdate

    @dash.callback(
        Output('attrs-hist-div', 'children'),
        [Input('data-loaded', 'children')],
        [State('session-id', 'children')]
    )
    def attributes_infos_tab_init(data_loaded, session_id):
        logger.debug("attributes_infos_tab_init callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate

        dh = session_data['data_holder']
        if dh is not None:
            content = []
            current_row = []
            for i, (attr_name, attr) in enumerate(dh['user_columns'].items()):
                if i>0 and i%4==0:
                    content.append(dbc.Row(current_row))
                    current_row = []
                
                col_content = html.Div([
                    dcc.Graph(
                        figure=go.Figure(),
                        id={
                            'type': 'attr_histogram',
                            'index': attr_name
                        },
                    )],
                    style={"height": 330}
                )
                if attr.is_numerical():
                    attr_min, attr_max = attr.get_minmax()
                    res = min(data_utils.find_res(attr_min), data_utils.find_res(attr_max), data_utils.find_res(attr.resolution))
                    res = max(0.001, res)
                    col_content.children.append(
                        html.Div(
                            dcc.RangeSlider(
                                id={
                                    'type': 'minmax_slider',
                                    'index': attr_name
                                },
                                min=attr_min,
                                max=attr_max,
                                step=res,
                                value=[attr_min, attr_max],
                                tooltip={"placement": "bottom", "always_visible": True},
                            ),
                            style={
                                'paddingLeft': '10px'
                            }
                        )
                    )
                    col_content.children.append(
                        html.P(
                            id={
                                'type': 'minmax_changed',
                                'index': attr_name
                            }
                        )
                    )

                current_row.append(
                    dbc.Col(
                        col_content, 
                        md=3
                    )
                )

            if current_row!=[]:
                content.append(dbc.Row(current_row))
            
            return content
        else:
            return PreventUpdate