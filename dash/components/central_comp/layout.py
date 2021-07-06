import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from components import table as table_component
from components import scatter_view as scatter_view_component

def render():
    return dbc.Collapse(
        [
            dbc.Tabs([
                dbc.Tab(scatter_view_component.render(), label="Scatter view"),
                dbc.Tab(table_component.render(), label="Table view")
            ])
        ], 
        style={
            'marginLeft' : '0%', 
            'marginRight' : '0%',
            'height': '650px'
        },
        id="collapse-viz",
        is_open=False
    )