import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from components import table as table_component
from components import ce_viz as ce_viz_component

def render():
    return dbc.Collapse(
        [
            html.H5("Interactive counterexample visualization and selection"),       
            # Graph (e)
            html.Div([
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
            ], style={
                'width': '29%',
                'display': 'inline-block',
                'verticalAlign': 'top'
            }),
            dbc.Tabs([
                dbc.Tab(table_component.render(), label="Full dataset"),
                dbc.Tab(ce_viz_component.render(), label="Interactive graph")
            ])
        ], style={
            'marginLeft' : '0%', 
            'marginRight' : '0%'
        },
        id="collapse-viz",
        is_open=False
    )