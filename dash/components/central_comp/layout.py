import dash_bootstrap_components as dbc
from dash import html

from components import table as table_component
from components import scatter_view as scatter_view_component
from components import attributes as attributes_component

from utils.dash_utils import Tooltip, hr_tooltip
from .legend import gen_analysed_legend, gen_time_controller
from constants import *

def render():
    return dbc.Collapse(
        [
            html.H5("Dataset exploration"),
            dbc.Collapse(
                [gen_analysed_legend(),
                gen_time_controller()],
                id="collapse-legend",
                is_open=True,
                style={
                    "width": "100%",
                    'margin': '0 auto',
                    'marginTop': '20px',
                    'marginBottom': '20px',
                    'textAlign': 'center'
                }
            ),
            dbc.Tabs([
                dbc.Tab(table_component.render(), label="Table"),
                dbc.Tab(scatter_view_component.render(), label="2D View"),
                dbc.Tab(attributes_component.render(), label="Attributes"),
            ])
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
            'height': '865px'

        },
        id="collapse-viz",
        is_open=False
    )