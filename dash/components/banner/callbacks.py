import dash
from dash.dependencies import Input, Output, State, MATCH

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

def register_callbacks(plogger):
    logger = plogger

    @dash.callback(
        Output({'type': 'modal', 'index': MATCH}, 'is_open'),
        [
            Input({'type': 'modal_open', 'index': MATCH}, 'n_clicks'), 
            Input({'type': 'modal_close', 'index': MATCH}, 'n_clicks')
        ],
        State({'type': 'modal', 'index': MATCH}, 'is_open'),
    )
    def toggle_user_guide_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open