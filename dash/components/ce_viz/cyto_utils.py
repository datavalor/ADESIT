import dash_cytoscape as cyto

from constants import *

def gen_cyto(elements = [], layout = {'name': 'breadthfirst'}):
    return cyto.Cytoscape(
        id='cytoscape_ce_graph',
        layout=layout,
        stylesheet=[
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)',
                    'borderColor': 'black',
                    'borderOpacity': '1',
                    'borderWidth': '2px'
                }
            },
            {
                'selector': '.hovered',
                'style': {
                    'borderWidth': '6px',
                }
            },
            {
                'selector': '.selected_node_bad',
                'style': {'background-color': SELECTED_COLOR_BAD}
            },
            {
                'selector': '.selected_node_good',
                'style': {'background-color': SELECTED_COLOR_GOOD}
            },
            {
                'selector': '.ce_node',
                'style': {'background-color': CE_COLOR}
            },
            {
                'selector': '.undirect_edges',
                'style': {'line-color': 'lightgray'}
            },
            {
                'selector': '.direct_edges',
                'style': {'line-color': 'darkgray'}
            }
        ],
        elements=elements,
        style={'width': '100%', 'height': '100%', 'backgroundColor': GRAPHS_BACKGROUND}
    )