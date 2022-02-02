import dash_bootstrap_components as dbc
from dash import dcc
from dash import html

from utils.dash_utils import gen_modal

def render():
    return [
        html.Div([],
            id="time_trace_tab",
        )
    ]