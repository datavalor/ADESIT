import dash_bootstrap_components as dbc
from dash import html

from constants import *

def render():
    return html.Div([
        html.H5("Pouet")
    ],
    id="attrs-hist-div",
    )