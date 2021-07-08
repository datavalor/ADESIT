import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from components import table as table_component
from components import ce_viz as ce_viz_component

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),
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
            html.H5("Scatter settings"),
            html.Div("X-Axis:"),
            dcc.Dropdown(id='x-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            html.Div("Y-Axis:"),
            dcc.Dropdown(id='y-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            
            html.Hr(),

            html.Div([
                html.H5("Box select infos"),
                html.Ul([
                    html.Li(["Number of tuples: ", html.Span("0", id="ntuples-selection")]),
                    html.Li(["Number of violating tuples: ", html.Span("0", id="nviolating-selection")]),
                    html.Li([
                        html.Div("SQL Query:"),
                        dcc.Textarea(id='sql-query', value="", style={'width':'100%', 'height': 90,'color':'#A3A3A3'})
                    ],id='sql-div',style={'width':'100%'})
                ], style={'width':'100%', 'display' : 'inline-block', 'verticalAlign': 'top'}),
            ], style={"marginTop": "10px"})
        ], style={
            'width': '29%',
            'display': 'inline-block',
            'verticalAlign': 'top'
        })
    ]