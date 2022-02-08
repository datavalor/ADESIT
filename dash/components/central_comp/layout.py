import dash_bootstrap_components as dbc
from dash import html
from dash import dcc

from .tabs import table_tab as table_tab_component
from .tabs import view2d_tab as view2d_tab_component
from .tabs import attributes_tab as attributes_tab_component
from .tabs import time_trace_tab as time_trace_tab_component

from .help import help_infos
from .legend import gen_analysed_legend
from constants import *
from utils.dash_utils import gen_help_tooltips

tab_help_modal_titles = {
    'table': 'Table',
    'view2d': '2D View',
    'attributes': 'Attributes',
    'timetrace': 'Time Trace',
}

def generate_help_button(tab_name):
    return [
        html.Div(
            html.I(
                id=f'{tab_name}-help',
                className="fas fa-question-circle",
                style={
                    'display' : 'inline-block',
                    'margin' :'5px',
                    'float' :'right'
                }
            ),
            style={
                "marginTop": "10px",
                "marginBottom": "10px",
                "width": "100%",
            }
        )
    ]

def create_tab(content, tab_name, tab_id):
    return dbc.Tab(
        dcc.Loading(
            html.Div(
                generate_help_button(tab_id)+content,
                style={
                    'height': '670px'
                }
            ),
            type="circle", 
            fullscreen=False,
        ),
        label=tab_name, 
        tab_style={"cursor": "pointer"},
        id=f'{tab_id}-tab'
    )

def render():
    return dbc.Collapse(
        [
            html.H5([
                'Dataset Exploration', 
                html.I(
                    id="dataexploration-help",
                    className="fas fa-question-circle",
                    style={
                        'display' : 'inline-block',
                        'margin' :'5px',
                    }
                ),
            ]),

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
                create_tab(table_tab_component.render(), 'Table', 'table'),
                create_tab(view2d_tab_component.render(), '2D View', 'view2d'),
                create_tab(attributes_tab_component.render(), 'Attributes', 'attributes'),
                create_tab(time_trace_tab_component.render(), 'Time Trace', 'timetrace'),
            ]),
            *gen_help_tooltips(help_infos)
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
        },
        id="collapse-viz",
        is_open=False
    )