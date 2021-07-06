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
from components import stats as stats_component
from components import table as table_component
from components import ce_viz as ce_viz_component
from components import central_comp as central_comp_component
from components import scatter_view as scatter_view_component

components = [
    banner_component,
    fd_settings_component,
    stats_component,
    table_component,
    ce_viz_component,
    central_comp_component,
    scatter_view_component
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='ADESIT')
    parser.add_argument('-d', '--debug', const=True, nargs='?', help='Debug mode')
    parser.add_argument('-t', '--timeout', const=True, nargs='?', help='No cache timeout')
    parser.add_argument('-b', '--banner', const=True, nargs='?', help='Removes the banner')
    args = parser.parse_args()

    external_stylesheets = [dbc.themes.LUMEN, "/dist/css/bootstrap/tabulator_bootstrap4.min.css"]
    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.index_string = index_string

    serve_layout_final = functools.partial(serve_layout, not args.banner, app)
    app.layout = serve_layout_final

    cache_config={
        'CACHE_TYPE': 'SimpleCache',
        'CACHE_THRESHOLD': 100
    }
    if not args.timeout: cache_config['CACHE_DEFAULT_TIMEOUT']=500
    cache_utils.cache = Cache(app.server, config=cache_config)

    logging_level = logging.DEBUG if args.debug else logging.INFO

    logger=logging.getLogger('adesit_callbacks')
    cache_utils.logger.setLevel(logging_level)
    logger.setLevel(logging_level)
    for component in components: component.register_callbacks(app, plogger=logger)

    if args.debug: app.run_server(debug=True)
    else: app.run_server(debug=False, host='0.0.0.0')
        