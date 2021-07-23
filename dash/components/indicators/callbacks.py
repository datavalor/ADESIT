import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None


def register_callbacks(app, plogger):
    logger = plogger
