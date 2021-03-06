import pandas as pd

ADESIT_VERSION = '2.0.0'

# COLUMN TYPES
NUMERICAL_COLUMN = "numerical"
CATEGORICAL_COLUMN = "categorical"
DATETIME_COLUMN = "datetime"

# ADESIT COLUMNS IN DATASET
ADESIT_INDEX = 'id'
G12_COLUMN_NAME = '_violating_tuple'
G3_COLUMN_NAME = '_g3_to_remove'
TABLE_ROWNUM_NAME = 'adesit_row_num'
SELECTION_COLUMN_NAME = '_selected'
PROJ_AXES = ['__PROJ1', '__PROJ2']

# MAX NUMBER OF ROWS IN DATATABLES
TABLE_MAX_ROWS = 17

# COLOR PALETTE
NON_ANALYSED_COLOR = '#000000'
SELECTED_NON_ANALYSED_COLOR = '#008000'
SELECTED_NON_ANALYSED_COLOR_OUTLINE = '#FFFFFF'
SELECTED_COLOR_BAD = '#EFF22C'
SELECTED_COLOR_BAD_OUTLINE = '#000000'
SELECTED_COLOR_GOOD = '#008000'
SELECTED_COLOR_GOOD_OUTLINE = '#FFFFFF'
CE_COLOR = '#EF553B'
FREE_COLOR = '#636EFA'
MEDIUM_COLOR = '#A9629B'
GRAPHS_BACKGROUND = '#E5ECF6'
CATEGORICAL_AXIS_ORDER = 'category descending'

# LIMITS WHEN RUNNING ON WEB
RESOURCE_LIMITED = False
MAX_N_TUPLES = 100000
MAX_N_ATTRS = 20
VPE_TIMEOUT = 10
G3_TIMEOUT = 10

DEFAULT_TIME_CUTS = {
    'day': {
        "timedelta": pd.Timedelta(1,'d'),
        "freq_symbol": "D",
        "date_format": '%Y-%m-%d'
    },
    'week': {
        "timedelta": pd.Timedelta(7,'d'),
        "freq_symbol": "W",
        "date_format": '%Y-%m-%d'
    },
    'month': {
        "timedelta": pd.Timedelta(30,'d'),
        "freq_symbol": "MS",
        "date_format": '%Y-%m'
    },
    'quarter': {
        "timedelta": pd.Timedelta(91,'d'),
        "freq_symbol": "QS",
        "date_format": '%Y-%m'
    },
    'year': {
        "timedelta": pd.Timedelta(365,'d'),
        "freq_symbol": "YS",
        "date_format": '%Y'
    },
}