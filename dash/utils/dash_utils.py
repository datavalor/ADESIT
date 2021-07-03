import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

hr_tooltip = html.Hr(style={'border': 'none', 'height': '2px', 'backgroundColor': '#FFF', 'marginTop': '2px', 'marginBottom': '2px'})

def Tooltip(**kwargs):
    #style = kwargs.pop('style')
    style_with_defaults = {'font-size': '14px'}
    return dbc.Tooltip(style=style_with_defaults, **kwargs)

def Modal(id):
    return dbc.Modal(
            [
                dbc.ModalHeader("Header"),
                dbc.ModalBody("This is the content of the modal"),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close", id="close", className="ml-auto", n_clicks=0
                    )
                ),
            ],
            id=id,
            is_open=False,
    )