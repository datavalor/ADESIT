import dash_core_components as dcc

user_guide_content = [
    dcc.Markdown('''
        Read **Context and Concepts** to understand the main points of ADESIT (or better, the paper presented in the About section).

        The sections below refer to the main parts of the interface which are clearly named.
        Only parts A is availaible when you open ADESIT.

        #### A - Supervised learning problem settings
        * Upload a dataset or choose one among the propositions.
        * Choose the functionnal dependency corresponding to the supervised problem at hand (eg. sepal_length, sepal_width → specie corresponds to specie=f(sepal_length, sepal_width)).
            * For each numerical attribute, uncertainties are null by default: this corresponds to the case of crisp FDs.
            * You can modify the uncertainties in regard to your problem: you are now considering non-crisp FDs.
        * Finally, your can launch the counterexample analysis. The more counterexamples there are, the longer this process will be.
            * Use *g3 appromixation* to get approximate bounds on the value of g3 (gray zone of the indicator).
            * Use *g3 exact* to get the exact value g3 using the WeGotYouCovered solver => this is NP-Hard and can take a **very** long time.
            * For crisp FDs, this distinction is ignored and the exact value is return in polynomial time.

        #### B - Counterexample performance indicators
        This section presents the g1, g2 and g3 indicators. For more information, your can hover their names.

        #### C - Interactive counterexample visualization and selection
    ''')
]