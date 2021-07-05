import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from utils.dash_utils import gen_modal
from .about import about_content
from .concepts import concepts_content
from .user_guide import user_guide_content

def render(app, banner=True):
    return dbc.Collapse(
        [
            html.Div(
                [
                    html.Img(src=app.get_asset_url('logo_white.png'), style={'height':'100px', 'position': 'absolute', 'top': '30px'}),
                ], 
                style={'paddingLeft': '2%', 'width': '20%', 'display' : 'inline-block'}
            ),
            html.Div(
                [
                    dcc.Markdown('''
                        Before training the last top-notch learning algorithm, why not starting by questionning the very existence of a model in your data and maybe spare some precious time?
                        ADESIT proposes exactly that: given a dataset and a supervised learning problem, we propose a counterexample analysis of your data to help you understand what could go wrong or maybe just confirm that you are ready to go!

                        *This is only a preview so bear in mind that you may be limited in computation resources (we will let you know) and that some bugs may remain.*
                    '''),
                    dbc.Button(
                        'Context and Concepts', 
                        color="light", 
                        id='concepts_open', 
                    ),
                    gen_modal(id='concepts_modal', title='Context and Concepts', content=concepts_content),
                    dbc.Button(
                        'User guide', 
                        color="light", 
                        id='user_guide_open', 
                        style={'marginLeft' : '5px'}
                    ),
                    gen_modal(id='user_guide_modal', title='User guide', content=user_guide_content),
                    dbc.Button(
                        'About', 
                        color="light",
                        id='about_open', 
                        style={'marginLeft' : '5px'}
                    ),
                    gen_modal(id='about_modal', title='About', content=about_content),
                ], 
                style={'paddingLeft': '2%', 'borderLeft': '1px solid', 'width': '80%', 'display' : 'inline-block', 'paddingRight': '2%', 'textAlign':'justify'}
            ),
        ], 
        style={'backgroundColor': 'black', 'color': 'white', 'paddingTop': '30px', 'paddingBottom': '2%',  'borderRadius': '0px 0px 6px 6px'},
        id="collapse-pres",
        is_open=banner
    )