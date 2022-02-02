import dash_bootstrap_components as dbc
from dash import html

from components import table as table_component
from components import scatter_view as scatter_view_component
from components import attributes as attributes_component
from components import time_trace as time_trace_component

from utils.dash_utils import Tooltip, hr_tooltip
from .legend import gen_analysed_legend
from constants import *

def generate_help_button(tab_name):
    return [
        html.Div(
            dbc.Button(
                "How to use this tab", 
                color="secondary", 
                id={
                    'type': 'modal_open_button',
                    'index': tab_name
                },
                n_clicks=0,
            ),
            style={
                "marginTop": "10px",
                "marginBottom": "10px",
                "width": "100%",
                "textAlign": "center",
            }
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", 
                        id={
                            'type': 'modal_close_button',
                            'index': tab_name
                        },
                        className="ms-auto", 
                        n_clicks=0
                    )
                ),
            ],
            id={
                'type': 'modal',
                'index': tab_name
            },
            is_open=False,
        ),
    ]

def render():
    return dbc.Collapse(
        [
            html.H5("Dataset exploration"),
            dbc.Collapse(
                [gen_analysed_legend()],
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
                dbc.Tab(generate_help_button('table')+table_component.render(), label="Table"),
                dbc.Tab(generate_help_button('view2d')+scatter_view_component.render(), label="2D View"),
                dbc.Tab(generate_help_button('attributes')+attributes_component.render(), label="Attributes"),
                dbc.Tab(generate_help_button('timetrace')+time_trace_component.render(), label="Time Trace"),
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