from utils.dash_utils import hr_tooltip

help_infos = {
    'table-help': '''
In this tab, you can visualise your data as a table. 
Attributes minmax filters and temporal filters change the table content.
When the data is analysed, you can click on any tuple to select it.
    ''',
    'view2d-help': '''
In this tab, you can visualise your data in a 2d plot. 
You can choose the axes, switch between scatter plot and heatmap.
When the number of features is sufficient, projection axis are available (PCA, MCA or FAMD depending on the type of the features).
Attributes minmax filters and temporal filters change the view content.
When the data is analysed, you can click on any point/tuple to select it.
    ''',
    'attributes-help': '''
In this tab, each attribute gets its own histogram to visualise its distribution.
You can also use this tab to filter out subsets of the attributes. These filters will directly reflect on all tabs.
A faded histogram of the full unfiltered dataset is always available in the background of each plot.
    ''',
    'timetrace-help': '''
Comming soon.
    ''',
    'dataexploration-help': [
        'With this section, you can explore the dataset visually in view of counterexamples.'
    ],
    'free-tuple-help': 'Tuple involved in no counterexample.',
    'involved-tuple-help': 'Tuple involved in at least 1 counterexample.'
}