import dash_bootstrap_components as dbc

tab_help_modal_titles = {
    'table': 'Table',
    'view2d': '2D View',
    'attributes': 'Attributes',
    'timetrace': 'Time Trace',
}

tab_help_modal_content = {
    'table': '''
In this tab, you can visualise your data as a table. 
Attributes minmax filters and temporal filters change the table content.
When the data is analysed, you can click on any tuple to select it.
    ''',
    'view2d': '''
In this tab, you can visualise your data in a 2d plot. 
You can choose the axes, switch between scatter plot and heatmap.
When the number of features is sufficient, projection axis are available (PCA, MCA or FAMD depending on the type of the features).
Attributes minmax filters and temporal filters change the view content.
When the data is analysed, you can click on any point/tuple to select it.
    ''',
    'attributes': '''
In this tab, each attribute gets its own histogram to visualise its distribution.
You can also use this tab to filter out subsets of the attributes. These filters will directly reflect on all tabs.
A faded histogram of the full unfiltered dataset is always available in the background of each plot.
    ''',
    'timetrace': '''
Comming soon.
    ''',
}