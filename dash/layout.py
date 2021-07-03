
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import dash_table
import figure_generator as fig_gen
import uuid

from utils.dash_utils import hr_tooltip, Tooltip, Modal

index_string = '''
        <!DOCTYPE html>
        <html>

        <head>
        {%css%}
        {%favicon%}
        <script src="https://kit.fontawesome.com/f5e0d5a64c.js" crossorigin="anonymous"></script>
        <meta charset="utf-8">
        <title>ADESIT</title>
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

            dbc.Collapse(
                [
                    html.Div(
                        [
                            # html.H1("ADESIT"),
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
            ),

            # Header & Primary Inputs
            html.Div([
                #html.Br(),
                html.H4("Supervised learning problem settings"),
                # File Input and params (b)
                html.Div([
                    html.Div("Select dataset"),
                    html.Div([
                        dcc.Upload(
                            dbc.Button('Upload File', color="primary", style={'width' : '100%',}),
                            id='upload-form',
                            style={'marginBottom' : '10px',},
                            max_size=10000000
                        ),
                    ], style={ 'width' : '49%', 'display' : 'inline-block'}),
                    
                    html.Div([
                        dbc.DropdownMenu(
                            label="Toy datasets", 
                            color="primary", 
                            children=[
                                dbc.DropdownMenuItem("Iris", id="toy-dataset-iris"),
                                dbc.DropdownMenuItem("Housing", id="toy-dataset-housing"),
                                dbc.DropdownMenuItem("Tobacco", id="toy-dataset-tobacco"),
                                dbc.DropdownMenuItem("Kidney", id="toy-dataset-kidney"),
                            ],
                            direction="down",
                            style= {'display':'inline-block', 'width' : '100%'}
                        ),
                    ], style= {'width' : '49%', 'display' : 'inline-block', 'float' : 'right'}),
                    
                    dcc.Markdown("No dataset selected!", id="dataset_confirm"),

                ],style={'width' : '25%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
                
                # Setting features and class
                html.Div([
                    #  Left-hand side of the 'DF' (c)
                    html.Div([
                        html.Div("Feature(s)"),
                        dcc.Dropdown(id='left-attrs', 
                            multi=True,
                            placeholder="Select the features", 
                            disabled=True,
                            style={'marginBottom' : '10px',}),
                        Tooltip(children=
                            ['You need to define similarity thresolds for each attribute. They take the form:', 
                                html.Br(), 
                                'a±(abs+rel*|a|)', 
                                html.Br(), 
                                'Therefore, two values a and b are considered as equal if:', 
                                html.Br(), 
                                "|a-b|≤abs+rel*max(|a|,|b|)"
                            ], 
                            target='help-thresolds'),
                        html.Div(id="left-tols"),
                        html.I("Uncertainties"),
                        html.I(
                            id="help-thresolds",
                            className="fas fa-question-circle",
                            style={
                                'display' : 'inline-block',
                                'margin' :'5px'}
                        ),
                        dash_table.DataTable(
                            id='thresold_table_features',
                            columns=(
                                [{'id': 'attribute', 'name': 'attribute'}, 
                                {'id': 'absolute', 'name': 'absolute'}, 
                                {'id': 'relative', 'name': 'relative'}]
                            ),
                            data=[],
                            editable=True
                        ),                        
                    ],style={'width' : '48%', 'verticalAlign': 'top', 'display' : 'inline-block'}),
                    
                    html.I(
                        className="fas fa-arrow-right",
                        style={
                            'display' : 'inline-block',
                            'marginTop': '30px',
                            'marginLeft': '15px',
                        }
                    ),

                    # Right-hand side of the 'DF' (d)
                    html.Div([
                        html.Div("Target"),
                        dcc.Dropdown(id='right-attrs', 
                            multi=True, 
                            placeholder="Select the target",
                            disabled=True,
                            style={'marginBottom' : '10px',}),
                        html.Div(id="right-tols"),
                        html.I(" d", style={"visibility":'hidden'}),
                        html.I(
                            id="help-thresolds-hidden",
                            className="fas fa-question-circle",
                            style={
                                "visibility":'hidden',
                                'display' : 'inline-block',
                                'margin' :'5px'}
                        ),
                        dash_table.DataTable(
                            id='thresold_table_target',
                            columns=(
                                [{'id': 'attribute', 'name': 'attribute'}, 
                                {'id': 'absolute', 'name': 'absolute'}, 
                                {'id': 'relative', 'name': 'relative'}]
                            ),
                            data=[],
                            editable=True
                        ), 
                    ],style={'width' : '48%', 'verticalAlign': 'top', 'float': 'right', 'display' : 'inline-block'}),                       
                ],style={'width' : '75%', 'display' : 'inline-block', 'paddingLeft' : '4%'}),


                html.Div([
                    html.Div(style={'width' : '70%', 'display' : 'inline-block',}),
                    html.Div([
                        dcc.Dropdown(
                            id = "g3_computation",
                            options=[
                                {'label': 'G3 Approximation', 'value': 'approx'},
                                {'label': 'G3 Exact', 'value': 'exact'}
                            ],
                            value='approx',
                            disabled=True,
                            clearable=False
                        ),
                    ], style={ 'width' : '20%', 'display' : 'inline-block', 'paddingRight' : '1%'}),
                    html.Div([
                        dbc.Button('Analyse', 
                            color="primary", 
                            disabled=True, 
                            id='analyse_btn', 
                            style={'width' : '100%'}
                        ),
                    ], style={'width' : '10%', 'display' : 'inline-block', 'float' : 'right'}),
                ], style={ 'width' : '100%', 'display' : 'block', 'marginTop': '20px'}), 
            ], style={
                'marginTop' : '1%',
                'marginBottom' : '1%',
                'padding' : '1% 1% 1% 1%',
                'borderLeft' : '10px solid',
                # 'border': '1px solid',
                'backgroundColor' : 'RGB(249,249,249)'
            }),

            # Statistics section
            dcc.Loading(dbc.Collapse(html.Div(
                [
                    html.H5([html.Span("Counterexample", id="counterexample-tooltip", style={'textDecoration': 'underline', 'cursor': 'pointer'}), " performance indicators"]),
                    html.Ul([
                        html.H6("Generalized g1 indicator", id='g1-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer', 'marginTop':'10px'}),
                        dcc.Graph(
                            id='g1_indicator',
                            figure=fig_gen.bullet_indicator(),
                            style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                        ),
                        html.H6("Generalized g2 indicator", id='g2-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                        dcc.Graph(
                            id='g2_indicator',
                            figure=fig_gen.bullet_indicator(),
                            style={'width':'100%', 'height':'50px', 'margin':'0 auto'}
                        ),
                        html.H6("110 tuples over 150 are involved in at least one counterexample.", id='ntuples_involved', style={'textAlign':'center', 'marginTop':'10px'}),
                    ], style={'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
                    html.Div([
                        html.H6("Function Existence Degree in Your Data", id='learnability-tooltip', style={'textAlign':'center', 'textDecoration': 'underline', 'cursor': 'pointer'}),
                        html.H6("Upper bound for a machine learning problem (generalized g3)", style={'textAlign':'center'}),
                        dcc.Graph(
                            id='learnability_indicator',
                            figure=fig_gen.gauge_indicator(),
                            style={'width':'260px', 'height':'150px', 'margin':'0 auto'}
                        ),
                    ], style={'width':'49%', 'display' : 'inline-block', 'verticalAlign': 'top', 'borderLeft': '1px solid', 'borderColor': 'lightgrey'}),
                    Tooltip(children=['1-g2 : percentage of tuples not involved in a counterexample', hr_tooltip, "Indicator of dataset purity."], target='g2-tooltip'),
                    Tooltip(children=['1-g1 : percentage of pairs of tuples that are not counterexamples', hr_tooltip, "Indicator of dataset purity."], target='g1-tooltip'),
                    Tooltip(children=['1-g3 : Maximum percentage of tuples keepable while removing every counterexample.', hr_tooltip, "Provides a theoretical upper bound on the best accuracy obtainable with an ideal model."], target='learnability-tooltip'),
                    Tooltip(children='Two tuples are considered as counterexamples if they have the same sets of features (in respect to the defined thresolds) and different targets.', target='counterexample-tooltip'),
                    html.Hr(),
                ]), 
                style={
                    'marginLeft' : '0%', 
                    'marginRight' : '0%'
                },
                id="collapse-stats",
                is_open=False
            ), id="loading_screen", type="circle", fullscreen=True),
            
            # Visualization section
            dbc.Collapse(
                [
                    html.H5("Interactive counterexample visualization and selection"),       
                    # Graph (e)
                    html.Div([
                            #dcc.Loading(id="loading-graph", children=[html.Div(dcc.Graph(id='main-graph'))], type="circle"),
                            html.Div(dcc.Graph(id='main-graph', clear_on_unhover=True))
                        ], 
                        style={
                            'textAlign' : 'center',
                            'width': '69%',
                            'display': 'inline-block',
                            'marginBottom' : '25px',
                        }
                    ),
                    
                    # Main Commands Board (f)
                    html.Div([
                        html.H5("Visualization settings"),
                        html.Div("X-Axis:"),
                        dcc.Dropdown(id='x-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
                        html.Div("Y-Axis:"),
                        dcc.Dropdown(id='y-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
                        
                        html.Hr(),
                        html.Div("Color in red:"),
                        dcc.Dropdown(id='mode', 
                            options=[
                                {'label': 'Tuples involved in a violating pair', 'value': 'color_involved'},
                                {'label': 'Tuples to suppress to remove violating pairs (G3)', 'value': 'color_g3'}
                            ],
                            value='color_involved',
                            clearable=False,
                            disabled=True
                        ),
                        html.Div("Select:"),
                        dcc.Dropdown(id='view', 
                            options=[
                                {'label': 'All', 'value': 'ALL'},
                                {'label': 'Blue Only', 'value': 'NP'},
                                {'label': 'Red Only', 'value': 'P'},
                            ],
                            value='ALL',
                            disabled=True,
                            clearable=False
                        ),
                        html.Div([
                            dbc.Button('Clear selected points', 
                                color="secondary", 
                                id='clear-selection', 
                                disabled=True,
                                style={'display':'inline-block'}
                            ),
                        ], style= {'margin' : '0 auto', "marginTop": "5px"}),

                        html.Hr(),
                        html.Div([
                            html.H5("Selection infos"),
                            html.Ul([
                                html.Li(["Number of tuples: ", html.Span("0", id="ntuples-selection")]),
                                html.Li(["Number of violating tuples: ", html.Span("0", id="nviolating-selection")]),
                                html.Li([
                                    html.Div("SQL Query:"),
                                    dcc.Textarea(id='sql-query', value="", style={'width':'100%', 'height': 90,'color':'#A3A3A3'})
                                ],id='sql-div',style={'width':'100%'})
                            ], style={'width':'100%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
                    ])
                ], 
                style={
                    'width': '29%',
                    'display': 'inline-block',
                    'verticalAlign': 'top'
                }),
            

                html.Div(
                    [
                        dash_table.DataTable(
                            id="dataTable",
                            page_size=15
                        )
                    ], 
                    id="table-container"
                )
            ], 
            style={
                'marginLeft' : '0%', 
                'marginRight' : '0%'
            },
            id="collapse-viz",
            is_open=False
        ),  
        
    ], 
    style={
        'width' : '90%', 
        'margin' : '0 auto'
    })