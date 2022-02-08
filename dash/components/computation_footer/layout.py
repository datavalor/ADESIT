from click import style
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from .help import help_infos
from utils.dash_utils import gen_help_tooltips

def render():
    return html.Div(
        [
            html.Div([
                html.Div(
                    dcc.Loading(
                        [
                            html.I(
                                id='time-attribute-help',
                                className="fas fa-question-circle",
                                style={
                                    'display' : 'inline-block',
                                    'margin' :'5px',
                                }
                            ),
                            html.Strong("Time attribute:", style={
                                "marginRight": "10px",
                            }),
                            dbc.Select(id='time-attribute-dropdown', 
                                options=[
                                    {'label': 'No attribute selected', 'value': 'noattradesit'}
                                ],
                                value='noattr',
                                disabled=False,
                                style={
                                    'display': 'inline-block', 
                                    'width': '200px',
                                    'marginRight': '20px'
                                }
                            ),
                            html.Span(
                                [
                                    html.Strong("Group by:", style={
                                        "marginRight": "10px",
                                    }),
                                    dbc.Select(id='time-period-dropdown', 
                                        options=[
                                            {'label': 'Don\'t group', 'value': 'nogroup'},
                                        ],
                                        value='nogroup',
                                        disabled=False,
                                        style={
                                            'display': 'inline-block', 
                                            'width': '150px'
                                        }
                                    ),
                                    html.Br(),
                                    html.Strong("Attribute period: "), html.Strong("N/A", id="time-range"),
                                    html.Br(),
                                    html.Strong("Current period: "), html.Strong("N/A", id="current-time-range"),
                                    html.Br(),
                                    dbc.Button(
                                        "←", id="time-backward-button", className="me-2", n_clicks=0,
                                        disabled=True
                                    ),
                                    html.Span("1", id="current-time-range-number"), 
                                    html.Span("/"),
                                    html.Span("1", id="max-time-range-number"),
                                    dbc.Button(
                                        "→", id="time-forward-button", className="me-2", n_clicks=0,
                                        disabled=True,
                                        style={"marginLeft":"10px"}
                                    )
                                ],
                                id='sub-time-elements',
                                style={
                                    'opacity': 0.2
                                }
                            )
                        ],
                        type="circle", fullscreen=False
                    ), 
                    style={ 
                        'width': '30%', 
                        'display': 'inline-block',
                        "textAlign": "center",
                        'width': '80%',
                        # 'marginTop': '20px'
                    }
                ),
                html.Div([
                    dcc.Dropdown(
                        id = "g3_computation",
                        options=[
                            {'label': 'g3 approximation', 'value': 'approx'},
                            {'label': 'g3 exact', 'value': 'exact'}
                        ],
                        value='approx',
                        disabled=True,
                        clearable=False, 
                        style={
                            'width' : '100%',
                            'marginBottom' : '5px'
                        }
                    ),
                    dbc.Button('Analyse', 
                        color="primary", 
                        disabled=True, 
                        id='analyse_btn', 
                        style={
                            'width' : '100%'
                        }
                    )], 
                    style={ 
                        'height': '100%',
                        'width' : '20%', 
                        'display' : 'inline-block', 
                        'position': 'relative',
                        'bottom' : '0'
                    }
                ), 
            ],
            style={
                "width": "950px",
                'margin': '0',
                'position': 'absolute',
                'top': '50%',
                'left': '50%',
                'transform': 'translate(-50%, -50%)'
            }),
            *gen_help_tooltips(help_infos)
        ], 
        style={
            'height': '190px',
            'position': 'fixed',
            'bottom': '0',
            'left': '0',
            'width': '100%',
            'zIndex': '10',
            'backgroundColor' : 'RGB(249,249,249)',
            'boxShadow': '-2px -2px 10px 8px rgb(0 0 0 / 10%)',
            'visibility' : 'hidden'
        },
        id="bottom-fixed-computation",
    )