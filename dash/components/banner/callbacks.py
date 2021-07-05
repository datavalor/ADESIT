import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Miscellaneous
import pandas as pd
pd.options.mode.chained_assignment = None

def register_callbacks(app, plogger):
    logger = plogger

    @app.callback(
        Output("user_guide_modal", "is_open"),
        [Input("user_guide_open", "n_clicks"), Input("user_guide_modal_close", "n_clicks")],
        [State("user_guide_modal", "is_open")],
    )
    def toggle_user_guide_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("about_modal", "is_open"),
        [Input("about_open", "n_clicks"), Input("about_modal_close", "n_clicks")],
        [State("about_modal", "is_open")],
    )
    def toggle_about_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output("concepts_modal", "is_open"),
        [Input("concepts_open", "n_clicks"), Input("concepts_modal_close", "n_clicks")],
        [State("concepts_modal", "is_open")],
    )
    def toggle_concepts_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open