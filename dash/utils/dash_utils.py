import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

hr_tooltip = html.Hr(style={'border': 'none', 'height': '2px', 'backgroundColor': '#FFF', 'marginTop': '2px', 'marginBottom': '2px'})

def Tooltip(**kwargs):
    #style = kwargs.pop('style')
    style_with_defaults = {'font-size': '14px'}
    return dbc.Tooltip(style=style_with_defaults, **kwargs)

def gen_modal(id, title="Modal header", content="This is content"):
    return dbc.Modal(
            [
                dbc.ModalHeader(title),
                dbc.ModalBody(content),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id=f"{id}_close", className="ml-auto", n_clicks=0
                    )
                ),
            ],
            id=id,
            is_open=False,
            size="lg",
    )