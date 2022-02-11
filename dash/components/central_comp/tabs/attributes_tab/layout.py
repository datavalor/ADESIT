import dash_bootstrap_components as dbc
from dash import html

from constants import *

def render():
    return [
        # dbc.Checklist(
        #     options=[
        #         {'label': 'Show full dataset in overlay', "value": 0}
        #     ],
        #     value=[0],
        #     id='attrs-viz-switches',
        #     switch=True,
        # ),
        html.Div([],
            id="attrs-hist-div",
            style={
                'overflowX': 'hidden',
                'overflowY': 'auto',
                'height': '100%',
                'marginLeft' : '1%', 
                'marginRight' : '1%',
            },
        )
    ]