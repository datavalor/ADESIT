from utils.dash_utils import hr_tooltip
from dash import html

help_infos = {
    'datasettings-help': [
        'In this section, you can upload your dataset and define the function you want to anaylse.',
        hr_tooltip,
        'The function is defined as a functionnal dependency. Therefore, a function Y=f(X) will be defined as X->Y.',
        hr_tooltip,
        'In a supervised learning problem, X corresponds to the features and Y the target.'
    ],
    'thresolds-help': ['You need to define similarity thresolds for each attribute. They take the form:', 
        html.Br(), 
        'a±(abs+rel*|a|)', 
        html.Br(), 
        'Therefore, two values a and b are considered as equal if:', 
        html.Br(), 
        "|a-b|≤abs+rel*max(|a|,|b|)"
    ]
}