import dash
from dash.dependencies import Input, Output, State, ALL
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

    def find_res(n):
        a, b = "{:e}".format(n).split("e")
        b = int(b.split('+')[-1])
        a = a.split('.')[1]
        i = len(a)-1
        while i>=0 and a[i]=='0':
            i-=1 
        i+=1
        return 10**(-i+b)

    @dash.callback(
        [Output({'type': 'attr_histogram', 'index': ALL}, 'children'),
        Output("a_min_max_has_been_changed", 'children')],
        [Input({'type': 'minmax_slider', 'index': ALL}, 'value')],
        [Input({'type': 'minmax_slider', 'index': ALL}, 'id'),
        State('session-id', 'children')]
    )
    def attributes_sliders_update(sliders_ranges, sliders_ids, session_id):
        logger.debug("attributes_sliders_update callback")
        session_data = get_data(session_id)
        if session_data is None: raise PreventUpdate        
        
        dh = session_data["data_holder"]
        if dh is not None:
            query_lines = []
            for i in range(len(sliders_ranges)):
                attr = sliders_ids[i]["index"]
                attr_range = sliders_ranges[i]
                dh['columns_minmax'][attr] = attr_range
                query_lines.append(f'{attr_range[0]} <= `{attr}` <= {attr_range[1]}')
            query = " and ".join(query_lines)
            dh['data'] = dh['full_data'].query(query)
            overwrite_session_data_holder(session_id, dh)
            return [dash.no_update]*(len(sliders_ranges)+1), ""
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

        dh = session_data["data_holder"]
        if dh is not None:
            content = []
            current_row = []
            for i, attr in enumerate(dh["columns_type"]):
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
                    # id=f'{dh["columns_stripped_id"][attr]}_histogram',
                    id={
                        'type': 'attr_histogram',
                        'index': attr
                    },
                    style={"height": 350}
                )
                if data_utils.is_numerical(attr, dh):
                    attr_min, attr_max = dh["columns_minmax"][attr]
                    res = min(find_res(attr_min), find_res(attr_max), find_res(dh["columns_resolution"][attr]))
                    res = max(0.001, res)
                    col_content.children.append(
                        dcc.RangeSlider(
                            id={
                                'type': 'minmax_slider',
                                'index': attr
                            },
                            # id=f'{dh["columns_stripped_id"][attr]}_minmax_slider',
                            min=attr_min,
                            max=attr_max,
                            step=res,
                            value=[attr_min, attr_max],
                            tooltip={"placement": "bottom", "always_visible": True},
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
                # print(content)
            if current_row!=[]:
                content.append(dbc.Row(current_row))
            
            return content, " "
        else:
            return PreventUpdate