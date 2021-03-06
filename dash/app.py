# Dash imports
import dash
import dash_bootstrap_components as dbc
import argparse, functools

# Handling cache and sessions
from flask_caching import Cache
import logging
logging.basicConfig()

# Personnal imports
from layout import index_string, serve_layout
import utils.cache_utils as cache_utils

from components import banner as banner_component
from components import fd_settings as fd_settings_component
from components import indicators as indicators_component
from components import selection_infos as selection_infos_component
from components import computation_footer as computation_footer_component

from components import central_comp as central_comp_component
from components.central_comp.tabs import view2d_tab as view2d_tab_component
from components.central_comp.tabs import time_trace_tab as time_trace_tab_component
from components.central_comp.tabs import attributes_tab as attributes_tab_component
from components.central_comp.tabs import table_tab as table_tab_component

import constants

components = [
    banner_component,
    fd_settings_component,
    indicators_component,
    table_tab_component,
    selection_infos_component,
    central_comp_component,
    view2d_tab_component,
    attributes_tab_component,
    computation_footer_component,
    time_trace_tab_component
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ADESIT')
    parser.add_argument('-d', '--debug', const=True, nargs='?', help='Debug mode')
    parser.add_argument('-r', '--resources', const=True, nargs='?', help='Resource Limits')
    parser.add_argument('-b', '--banner', const=True, nargs='?', help='Removes the banner')
    args = parser.parse_args()

    external_stylesheets = [dbc.themes.LUMEN, "/dist/css/bootstrap/tabulator_bootstrap4.min.css"]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.index_string = index_string

    if args.resources: constants.RESOURCE_LIMITED = True

    serve_layout_final = functools.partial(serve_layout, not args.banner, app)
    app.layout = serve_layout_final

    # Setting cache
    cache_config={
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_THRESHOLD': 100
    }
    if constants.RESOURCE_LIMITED: cache_config['CACHE_DEFAULT_TIMEOUT']=10*60
    else: cache_config['CACHE_DEFAULT_TIMEOUT']=0
    cache_utils.cache = Cache(app.server, config=cache_config)

    logging_level = logging.DEBUG if args.debug else logging.INFO

    logger=logging.getLogger('adesit_callbacks')
    cache_utils.logger.setLevel(logging_level)
    logger.setLevel(logging_level)
    for component in components: component.register_callbacks(plogger=logger)

    if args.debug: app.run_server(debug=True)
    else: app.run_server(debug=False, host='0.0.0.0')
        