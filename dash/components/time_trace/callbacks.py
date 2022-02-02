import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate

def register_callbacks(plogger):
    logger = plogger