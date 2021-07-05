import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import uuid

from components import banner as banner_component
from components import fd_settings as fd_settings_component
from components import stats as stats_component
from components import viz as viz_component

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

        <body style="font-family: Inter,sans-serif; scroll-behavior: smooth;">

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

    return html.Div(
        [
            html.Div(session_id, id='session-id', style={'display': 'none'}),
            html.Span("", id='data-loaded', style={'display': 'none'}),
            html.Span("", id='data-updated', style={'display': 'none'}),
            html.Span("", id='data-analysed', style={'display': 'none'}),
            dcc.Loading(id="loading-screen1", type="circle", fullscreen=False),
            html.Span("", id='test-callback', style={'display': 'none'}),

            dbc.Alert(
                "The computation has exceeded the time limit. Try again with different settings.",
                id="alert-timeout",
                dismissable=True,
                is_open=False,
                color='danger',
                fade='True',
                duration=5000,
                style={'position':'absolute', 'z-index': '99', 'top': '5%', 'left': '5%'}
            ),

            dbc.Alert(
                "Projections are computed on the features, please select more features in order to continue.",
                id="alert-projection",
                dismissable=True,
                is_open=False,
                color='danger',
                fade='True',
                duration=5000,
                style={'position':'absolute', 'z-index': '99', 'top': '5%', 'left': '5%'}
            ),

            banner_component.render(app, banner=banner),
            fd_settings_component.render(),
            stats_component.render(),
            viz_component.render(),

            html.Div([
                ""
            ], style={"width": "100%", "height": "10px"})
    ], 
    style={
        'width' : '90%', 
        'margin' : '0 auto'
    })