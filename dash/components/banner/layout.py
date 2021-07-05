import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from utils.dash_utils import Modal

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
                        'User guide', 
                        color="light", 
                        id='user_guide_btn', 
                        # style={'width' : '100%'}
                    ),
                    Modal(id='user_guide_modal'),
                    dbc.Button(
                        'About', 
                        color="light",
                        id='about_btn', 
                        style={'marginLeft' : '5px'}
                    )
                ], 
                style={'paddingLeft': '2%', 'borderLeft': '1px solid', 'width': '80%', 'display' : 'inline-block', 'paddingRight': '2%', 'textAlign':'justify'}
            ),
        ], 
        style={'backgroundColor': 'black', 'color': 'white', 'paddingTop': '30px', 'paddingBottom': '2%',  'borderRadius': '0px 0px 6px 6px'},
        id="collapse-pres",
        is_open=banner
    )