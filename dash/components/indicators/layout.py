import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from utils.dash_utils import Tooltip, hr_tooltip
import utils.viz.indicator_utils as indicator_utils

def render():
    return dcc.Loading(dbc.Collapse(html.Div(
        [
            html.H5([html.Span("Counterexample", id="counterexample-tooltip", style={'textDecoration': 'underline', 'cursor': 'pointer'}), " performance indicators"]),
            html.Ul([
                html.H6("Generalized g1 indicator", id='g1-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer', 'marginTop':'10px'}),
                dcc.Graph(
                    id='g1_indicator',
                    figure=indicator_utils.bullet_indicator(),
                    style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                ),
                html.H6("Generalized g2 indicator", id='g2-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                dcc.Graph(
                    id='g2_indicator',
                    figure=indicator_utils.bullet_indicator(),
                    style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                ),
                html.H6("110 tuples over 150 are involved in at least one counterexample.", id='ntuples_involved', style={'textAlign':'center', 'marginTop':'10px'}),
            ], style={'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.H6("Function Existence Degree in Your Data", id='learnability-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                html.H6("Upper bound for a machine learning problem (generalized g3)", style={'textAlign':'center'}),
                dcc.Graph(
                    id='learnability_indicator',
                    figure=indicator_utils.gauge_indicator(),
                    style={'width':'260px', 'height':'150px', 'margin':'0 auto'}
                ),
            ], style={'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top', 'borderLeft': '1px solid', 'borderColor': 'lightgrey'}),
            Tooltip(children=['1-g2 : percentage of tuples not involved in a counterexample', hr_tooltip, "Indicator of dataset purity."], target='g2-tooltip'),
            Tooltip(children=['1-g1 : percentage of pairs of tuples that are not counterexamples', hr_tooltip, "Indicator of dataset purity."], target='g1-tooltip'),
            Tooltip(children=['1-g3 : Maximum percentage of tuples keepable while removing every counterexample.', hr_tooltip, "Provides a theoretical upper bound on the best accuracy obtainable with an ideal model."], target='learnability-tooltip'),
            Tooltip(children='Two tuples are considered as counterexamples if they have the same sets of features (in respect to the defined thresolds) and different targets.', target='counterexample-tooltip'),
            html.Hr(),
        ]), 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%'
        },
        id="collapse-stats",
        is_open=False
    ), id="loading_screen", type="circle", fullscreen=True)