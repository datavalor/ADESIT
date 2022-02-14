from utils.dash_utils import hr_tooltip
from dash import html

help_infos = {
    'time-attribute-help': '''
    If ADESIT detects datetime attributes in the dataset, they will be listed in this dropdown.
    By selecting one of them, you are informing ADESIT that your dataset is a time series and new analysis tools will be available.

    This is optional.
    ''',
    'g3-computation-help': '''
    Computing the learnability indicator (1-g3) is a NP-Complete problem related to the Minimum Vertex Cover. 
    You can choose to compute it exactly (for medium size datasets), approximately (for large ones) or let us choose for you!
    '''
}