import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash import dash_table

from utils.dash_utils import Tooltip

def render():
    return html.Div(
        [
            html.H4("Data and problem settings"),

            # File Input and params (b)
            html.Div([
                html.Div("Select dataset"),
                html.Div([
                    dcc.Upload(
                        dbc.Button('Upload File', color="primary", style={'width' : '100%',}),
                        id='upload-form',
                        style={'marginBottom' : '10px',},
                        max_size=30000000
                    ),
                ], style={ 'width' : '49%', 'display' : 'inline-block'}),
                
                html.Div([
                    dbc.DropdownMenu(
                        label="Toy datasets", 
                        color="primary", 
                        children=[
                            dbc.DropdownMenuItem("Iris", id="toy-dataset-iris"),
                            dbc.DropdownMenuItem("Housing", id="toy-dataset-housing"),
                            dbc.DropdownMenuItem("Diamonds", id="toy-dataset-diamonds"),
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
                            {'id': 'absolute', 'name': 'abs'}, 
                            {'id': 'relative', 'name': 'rel'}]
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
                            {'id': 'absolute', 'name': 'abs'}, 
                            {'id': 'relative', 'name': 'rel'}]
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
                            {'label': 'g3 approximation', 'value': 'approx'},
                            {'label': 'g3 exact', 'value': 'exact'}
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
            'padding' : '1%',
            'borderLeft' : '10px solid',
            'backgroundColor' : 'RGB(249,249,249)'
        }
    )