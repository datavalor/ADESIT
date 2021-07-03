# Dash imports
import dash
import dash_bootstrap_components as dbc
import argparse, functools

# Handling cache and sessions
from flask_caching import Cache
import logging

# Personnal imports
from layout import index_string, serve_layout
from callbacks import register_callbacks
import utils.cache_utils as cache_utils

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

    if args.debug:
        cache_utils.logger.setLevel(logging.DEBUG)
        register_callbacks(app, logging_level=logging.DEBUG)
        app.run_server(debug=True)
    else:
        register_callbacks(app)
        app.run_server(debug=False, host='0.0.0.0')
        