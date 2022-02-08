from utils.dash_utils import hr_tooltip

help_infos = {
    'counterexample-help': [
        'You can use this section to display summary indicators on the counterexamples distribution in the dataset.',
        hr_tooltip,
        'Two tuples are considered as counterexamples if they have the same sets of features (in respect to the defined thresolds) and different targets.'
    ],
    'g1-help': [
        '1-g1 : percentage of pairs of tuples that are not counterexamples', 
        hr_tooltip, 
        'Indicator of dataset purity.'
    ],
    'g2-help': [
        '1-g2 : percentage of tuples not involved in a counterexample', 
        hr_tooltip, 
        'Indicator of dataset purity.'
    ],
    'g3-help': [
        '1-g3 : Maximum percentage of tuples keepable while removing every counterexample.', 
        hr_tooltip, 
        'Provides a theoretical upper bound on the best accuracy obtainable with an ideal model.'
    ],
}