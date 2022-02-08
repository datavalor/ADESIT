from utils.dash_utils import hr_tooltip
from dash import html

help_infos = {
    'time-attribute-help': '''
    If ADESIT detects datetime attributes in the dataset, they will be listed in this dropdown.
    By selecting one of them, you are informing ADESIT that your dataset is a time series and new analysis tools will be available.

    This is optional.
    '''
}