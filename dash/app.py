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
from callbacks.viz_callbacks import register_viz_callbacks
from callbacks.fd_settings_callbacks import register_fd_settings_callbacks
from callbacks.table_callbacks import register_table_callbacks
from callbacks.data_callbacks import register_data_callbacks
import utils.cache_utils as cache_utils

callbacks = [
    register_viz_callbacks,
    register_fd_settings_callbacks,
    register_table_callbacks,
    register_data_callbacks
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
    for callback in callbacks: callback(app, plogger=logger)

    if args.debug: app.run_server(debug=True)
    else: app.run_server(debug=False, host='0.0.0.0')
        