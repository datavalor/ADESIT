import dash_bootstrap_components as dbc
from dash import html

hr_tooltip = html.Hr(style={'border': 'none', 'height': '2px', 'backgroundColor': '#FFF', 'marginTop': '2px', 'marginBottom': '2px'})

def Tooltip(**kwargs):
    style_with_defaults = {'fontSize': '14px'}
    return dbc.Tooltip(style=style_with_defaults, **kwargs)

def gen_modal(id, title="Modal header", content="This is content"):
    return dbc.Modal(
        [
            dbc.ModalHeader(title),
            dbc.ModalBody(content, style={'textAlign': 'justify'}),
            dbc.ModalFooter(
                dbc.Button(
                    "Close", 
                    id={
                        'type': 'modal_close',
                        'index': id
                    }, 
                    className="ml-auto", 
                    n_clicks=0
                )
            ),
        ],
        id={
            'type': 'modal',
            'index': id
        },        
        is_open=False,
        size="xl",
    )

def gen_help_tooltips(help_infos):
    tooltips = []
    for id, content in help_infos.items():
        tooltips.append(Tooltip(children=content, target=id))
    return tooltips