from click import style
import dash
from dash.dependencies import Input, Output, State, MATCH
from dash.exceptions import PreventUpdate

from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go

from constants import *
from utils.cache_utils import *
import utils.data_utils as data_utils
import utils.viz.histogram_utils as histogram_utils

def register_callbacks(app, plogger):
    logger = plogger

    def generate_attribute_histogram(attr, attr_name, data_holder):
        figure = go.Figure()
        histogram_utils.add_basic_histograms(
            figure,
            data_holder["full_data"],
            attr_name,
            10,
            data_holder,
            minmax=attr.get_minmax(original=True)
        )
        figure.update_layout(
            title=f'{attr_name} ({attr.get_type()})',
            margin={'l': 0, 'b': 0, 't': 60, 'r': 0},
            height = 300,
        )
        if attr.is_numerical():
            attr_min, attr_max = attr.get_minmax(original=False)
            figure.add_vrect(
                x0=attr_min, x1=attr_max,
                fillcolor="green", 
                opacity=0.25, 
                line_width=0
            )
        figure.update_xaxes(
            range=attr.get_minmax(auto_margin=True, original=True)
        )
        return figure

    @dash.callback(
        [Output({'type': 'attr_histogram', 'index': MATCH}, 'figure'),
        Output({'type': 'minmax_changed', 'index': MATCH}, 'children')],
        [Input({'type': 'minmax_slider', 'index': MATCH}, 'value'),
        Input({'type': 'minmax_slider', 'index': MATCH}, 'id')],
        [State({'type': 'attr_histogram', 'index': MATCH}, 'figure'),
        State('session-id', 'children')]
    )
    def attributes_sliders_update(slider_range, slider_id, current_figure, session_id):
        logger.debug("attributes_sliders_update callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate        
        
        dh = session_data['data_holder']
        if dh is not None:
            attr_name=slider_id["index"]
            dh['user_columns'][attr_name].minmax = slider_range
            attr = dh['user_columns'][attr_name]
            figure = generate_attribute_histogram(attr, attr_name, dh)
            overwrite_session_data_holder(session_id, dh)
            return figure, ""
        else:
            raise PreventUpdate

    @dash.callback(
        [Output('attrs-hist-div', 'children'),
        Output('sliders_added', 'children')],
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
                
                figure = generate_attribute_histogram(attr, attr_name, dh)

                col_content = html.Div([
                    dcc.Graph(
                        figure=figure,
                        id={
                            'type': 'attr_histogram',
                            'index': attr_name
                        },
                    )],
                    style={"height": 350}
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
            
            return content, ""
        else:
            return PreventUpdate