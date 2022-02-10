from dash import dcc
from dash import html

def render():
    return [
        html.Div("", style={'width': "100%", 'height': "10px"}),

        # Graph
        html.Div([
                dcc.Graph(figure={}, id='main-graph', clear_on_unhover=True)
            ], 
            style={
                'textAlign' : 'center',
                'width': '69%',
                'display': 'inline-block',
                'marginBottom' : '25px',
            }
        ),
        
        # Main Commands Board
        html.Div([
            html.H5("View settings"),
            html.Label("Mode"),
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
            
            html.Div([
                html.Label("Number of bins (numeric attributes)"),
                dcc.Slider(
                    id='heatmap_resolution_slider',
                    min=5,
                    max=30,
                    step=1,
                    value=10,
                    marks={n:str(n) for n in list(range(5, 35, 5))},
                    disabled=False
                )
            ]
            ),

            html.Hr(),

            html.Label("X-Axis"),
            dcc.Dropdown(id='x-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            html.Label("Y-Axis"),
            dcc.Dropdown(id='y-axis',style={'width' : '100%', 'marginBottom' : '10px'}),
            
            html.Hr(),

            html.Div([
                html.H5("Box/Lasso select infos"),
                html.Span("0", id="ntuples-selection"), " tuples selected.\n",
                html.Div(
                    [html.Span("0 (0%)", id="nviolating-selection"), " of them are involved in a counterexample."],
                    id="select-infos-after-analysis",
                    style={'visibility' : 'hidden'}
                )
            ], style={"marginTop": "10px"})
        ], style={
            'width': '29%',
            'display': 'inline-block',
            'verticalAlign': 'top'
        })
    ]