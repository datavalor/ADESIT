import dash_bootstrap_components as dbc
from dash import html

import uuid

from components import banner as banner_component
from components import fd_settings as fd_settings_component
from components import indicators as indicators_component
from components import central_comp as central_comp_component
from components import selection_infos as selection_infos_component
from components import computation_footer as computation_footer_component

from constants import *

index_string = '''
        <!DOCTYPE html>
        <html>

        <head>
        {%css%}
        {%favicon%}
        <script src="https://kit.fontawesome.com/f5e0d5a64c.js" crossorigin="anonymous"></script>
        <meta charset="utf-8">
        <title>ADƎSIT</title>
        <style type="text/css">
        .collapsing {
            -webkit-transition: none !important;
            transition: none !important;
            display: none !important;
        }
        </style>
        </head>


        <body style="font-family: sans-serif; font-size: medium;">

            <section id="tool" style="background-color: white;">
                <div style ="max-width: 1700px; margin: 0 auto;">
                    {%app_entry%}
                </div>
            </section>

            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>

        </body>
        </html>
    '''

def serve_layout(banner, app):
    session_id = str(uuid.uuid4())

    return dbc.Container(
        [
            html.P(session_id, id='session-id', style={'display': 'none'}),
            html.P(id='data-loaded', style={'display': 'none'}),
            html.P(id='data-analysed-prop', style={'display': 'none'}),
            html.P(id='selection_changed', style={'display': 'none'}),
            html.P(id='data_updated', style={'display': 'none'}),
            html.P(id='view2d_axes_have_changed', style={'display': 'none'}),

            dbc.Alert(
                f"Error while loading dataset. Note that there is a limit of {MAX_N_TUPLES} tuples and {MAX_N_ATTRS} attributes on this online version.",
                id="alert-data_not_loaded",
                dismissable=True,
                is_open=False,
                color='danger',
                style={'position':'absolute', 'z-index': '99', 'top': '5%', 'left': '5%'}
            ),

            dbc.Alert(
                "The computation has exceeded the time limit (dataset too large, too many counterexamples...). Try again with different settings.",
                id="alert-timeout",
                dismissable=True,
                is_open=False,
                color='danger',
                style={'position':'absolute', 'z-index': '99', 'top': '5%', 'left': '5%'}
            ),

            banner_component.render(app, banner=banner),
            fd_settings_component.render(),
            indicators_component.render(),
            central_comp_component.render(),
            selection_infos_component.render(),


            computation_footer_component.render(),


            html.Div([
                ""
            ], style={"width": "100%", "height": "300px"}),
        ],
        fluid=True
    )