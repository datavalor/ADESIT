import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from .help import help_infos
from utils.dash_utils import gen_help_tooltips
import utils.viz.indicator_utils as indicator_utils

def render():
    return dcc.Loading(dbc.Collapse(html.Div(
        [
            html.H5([
                "Counterexample Performance Indicators", 
                html.I(
                    id="counterexample-help",
                    className="fas fa-question-circle",
                    style={
                        'display' : 'inline-block',
                        'margin' :'5px',
                    }
                ),
            ]),
            html.Ul([
                html.H6(
                    [
                        "Generalized g1 indicator",
                        html.I(
                            id='g1-help',
                            className="fas fa-question-circle",
                            style={
                                'display' : 'inline-block',
                                'margin' :'5px',
                            }
                        ),
                    ], 
                    style={'marginTop':'10px'}
                ),
                dcc.Graph(
                    id='g1_indicator',
                    figure=indicator_utils.bullet_indicator(),
                    style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                ),
                html.H6(
                    [
                        "Generalized g2 indicator",
                        html.I(
                            id='g2-help',
                            className="fas fa-question-circle",
                            style={
                                'display' : 'inline-block',
                                'margin' :'5px',
                            }
                        ),
                    ], 
                    style={'marginTop':'10px'}
                ),
                dcc.Graph(
                    id='g2_indicator',
                    figure=indicator_utils.bullet_indicator(),
                    style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                ),
                html.H6("110 tuples over 150 are involved in at least one counterexample.", id='ntuples_involved', style={'textAlign':'center', 'marginTop':'10px'}),
            ], style={'textAlign':'center', 'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.H6(
                    [
                        "Function Existence Degree in Your Data",
                        html.I(
                            id='g3-help',
                            className="fas fa-question-circle",
                            style={
                                'display' : 'inline-block',
                                'margin' :'5px',
                            }
                        ),
                    ], 
                    style={'marginTop':'10px'}
                ),
                html.H6("Upper bound for a machine learning problem (generalized g3)", style={'textAlign':'center'}),
                dcc.Graph(
                    id='learnability_indicator',
                    figure=indicator_utils.gauge_indicator(),
                    style={'width':'260px', 'height':'150px', 'margin':'0 auto'}
                ),
            ], style={'textAlign':'center', 'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top', 'borderLeft': '1px solid', 'borderColor': 'lightgrey'}),
            *gen_help_tooltips(help_infos),
            html.Hr(),
        ]), 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%'
        },
        id="collapse-stats",
        is_open=False
    ), type="circle", fullscreen=False)