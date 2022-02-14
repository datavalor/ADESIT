import dash_bootstrap_components as dbc
from dash import html

from constants import *
from utils.dash_utils import gen_modal
from .modals_content.about import about_content
from .modals_content.concepts import concepts_content
from .modals_content.user_guide import user_guide_content
from .modals_content.overview import overview_content

def generate_banner_button(name, id, content):
    return html.Span([
        dbc.Button(
            name, 
            color="light", 
            id={
                'type': 'modal_open',
                'index': id
            }, 
            style={
                'marginLeft': '5px'
            }
        ),
        gen_modal(id=id, title=name, content=content)
    ])

def render(app, banner=True):
    return dbc.Collapse(
        [
            html.Div(
                [
                    html.Img(
                        src=app.get_asset_url('logo_white.png'), 
                        style={'height':'80px', 'position': 'absolute', 'top': '10px'}
                    )
                ],
                style={'marginLeft': '30px', 'width': '100px', 'display' : 'inline-block'}
            ),
            html.Div(
                [
                    html.Span(f'Version: {ADESIT_VERSION}'),
                    html.Br(),
                    html.Span(f'Limited Resources: {RESOURCE_LIMITED}') 
                ],
                style={'marginLeft': '30px', 'display' : 'inline-block', 'color': 'darkgray'}
            ),
            html.Div(
                [
                    generate_banner_button('Quick Overview', 'quick_overview', overview_content),
                    generate_banner_button('Context and Concepts', 'context_and_concepts', concepts_content),
                    generate_banner_button('User Guide', 'user_guide', user_guide_content),
                    generate_banner_button('About', 'about', about_content),
                ], 
                style={
                    'marginRight' : '30px',
                    'float': 'right',
                }
            ),
        ], 
        style={
            'backgroundColor': 'black', 
            'color': 'white', 
            'paddingTop': '30px', 
            'paddingBottom': '2%',  
            'height': '110px',
            'borderRadius': '0px 0px 6px 6px',
            'marginBottom' : '10px'
        },
        id="collapse-pres",
        is_open=banner
    )