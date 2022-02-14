from dash import dcc

overview_content = [
    dcc.Markdown('''
    Before training the last top-notch learning algorithm, why not starting by questionning the very existence of a model in your data and maybe spare some precious time?
    ADESIT proposes exactly that: given a dataset and a supervised learning problem, we propose a counterexample analysis of your data to help you understand what could go wrong or maybe just confirm that you are ready to go!

    *This is only a preview so bear in mind that you may be limited in computation resources. 10 minutes of inactivity deletes your stored data.*
    ''')
]