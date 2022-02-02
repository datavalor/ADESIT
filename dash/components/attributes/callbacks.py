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
import utils.histogram_utils as histogram_utils

def register_callbacks(app, plogger):
    logger = plogger

    @dash.callback(
        [Output({'type': 'attr_histogram', 'index': MATCH}, 'children'),
        Output({'type': 'minmax_changed', 'index': MATCH}, 'children')],
        [Input({'type': 'minmax_slider', 'index': MATCH}, 'value'),
        Input({'type': 'minmax_slider', 'index': MATCH}, 'id')],
        [State('session-id', 'children')]
    )
    def attributes_sliders_update(slider_range, slider_id, session_id):
        logger.debug("attributes_sliders_update callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate        
        
        dh = session_data['data_holder']
        if dh is not None:
            dh['columns_minmax'][slider_id["index"]] = slider_range
            overwrite_session_data_holder(session_id, dh)
            return dash.no_update, ""
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
            for i, attr in enumerate(dh['user_columns']):
                if i>0 and i%4==0:
                    content.append(dbc.Row(current_row))
                    current_row = []
                
                figure = go.Figure()
                histogram_utils.add_attribute_histogram(
                    figure,
                    dh["data"],
                    attr,
                    10,
                    dh
                )
                figure.update_layout(
                    title=f'{attr} ({dh["columns_type"][attr]})',
                    margin={'l': 0, 'b': 0, 't': 60, 'r': 0},
                    height = 300,
                )
                col_content = html.Div([
                    dcc.Graph(
                        figure=figure,
                    )],
                    id={
                        'type': 'attr_histogram',
                        'index': attr
                    },
                    style={"height": 350}
                )
                if data_utils.is_numerical(attr, dh):
                    attr_min, attr_max = dh["columns_minmax"][attr]
                    res = min(data_utils.find_res(attr_min), data_utils.find_res(attr_max), data_utils.find_res(dh["columns_resolution"][attr]))
                    res = max(0.001, res)
                    col_content.children.append(
                        dcc.RangeSlider(
                            id={
                                'type': 'minmax_slider',
                                'index': attr
                            },
                            min=attr_min,
                            max=attr_max,
                            step=res,
                            value=[attr_min, attr_max],
                            tooltip={"placement": "bottom", "always_visible": True},
                        )                        
                    )
                    col_content.children.append(
                        html.P(
                            id={
                                'type': 'minmax_changed',
                                'index': attr
                            }
                        )
                    )

                figure.update_xaxes(
                    range=data_utils.attribute_min_max(
                        attr, dh, 
                        rel_margin=0.1
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