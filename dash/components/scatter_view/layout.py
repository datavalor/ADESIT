from dash import dcc
from dash import html

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
            html.H5("View settings"),
            html.Div("Mode:"),
            dcc.Dropdown(
                id='2d-viewmode',
                options=[
                    {'label': 'Scatter plot', 'value': 'scatter'},
                    {'label': 'Heatmap', 'value': 'heat'}
                ],
                value='scatter',
                style={'width' : '100%', 'marginBottom' : '10px'},
                clearable=False
            ),
            
            html.Div(
                [
                html.Span("Heatmap nbins:"),
                dcc.Slider(
                    id='heatmap_resolution_slider',
                    min=1,
                    max=30,
                    step=1,
                    value=10,
                    marks={n:str(n) for n in [1]+list(range(5, 35, 5))},
                    disabled=False
                )
                ]
            ),
            html.Div("X-Axis:"),
            dcc.Dropdown(id='x-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            html.Div("Y-Axis:"),
            dcc.Dropdown(id='y-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            
            html.Hr(),

            html.Div([
                html.H5("Box select infos"),
                html.Ul([
                    html.Li([html.Span("0", id="ntuples-selection"), " tuples selected."]),
                    html.Li(["Tuple involved in a counterexample: ", html.Span("0", id="nviolating-selection")]),
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