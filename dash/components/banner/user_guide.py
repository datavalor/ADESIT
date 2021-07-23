import dash_core_components as dcc

user_guide_content = [
    dcc.Markdown('''
        Read **Context and Concepts** to understand the main points of ADESIT (or better, the paper presented in the About section). For full computing power, you are invited to launch ADESIT locally.

        The sections below refer to the main parts of the interface which are clearly named.
        Only parts A is availaible when you open ADESIT.
        

        #### A - Data and problem settings
        * Upload a dataset or choose one among the propositions. *In this this online version you are restricted to 100,000 rows and 20 attributes.*
        * Choose the functionnal dependency corresponding to the supervised problem at hand (eg. sepal_length, sepal_width → specie corresponds to specie=f(sepal_length, sepal_width)).
            * For each numerical attribute, uncertainties are null by default: this corresponds to the case of *crisp FDs*.
            * You can modify the uncertainties in regard to your problem: you are now considering *non-crisp FDs*.
        * Finally, your can launch the counterexample analysis. The more counterexamples there are, the longer this process will be. *In this online version, you are restricted to 10 seconds of processing time.*
            * Use *g3 appromixation* to get approximate bounds on the value of g3 (gray zone of the indicator).
            * Use *g3 exact* to get the exact value g3 using the WeGotYouCovered solver => this is NP-Hard and can take a **very** long time.
            * For crisp FDs, this distinction is ignored and the exact value is return in polynomial time.

        #### B - Counterexample performance indicators
        This section presents the g1, g2 and g3 indicators. For more information, your can hover their names.

        #### C - Dataset exploration

        In this part you can observe two miroring versions of the same dataset:

        * Scatter view
            * This view presents a scatter plot of the dataset according to two axes than you can change at any time. Two dimensionnality reduction projection axes are also availaible and depend on the type of the attributes and the number of features considered (PCA, MCA, FAMD).
            * In the scatter view, you can freely zoom and pan. With the box select tool, you can frame a zone of the dataset whose informations are displayed in the *Box Select Infos* section.
        * Table view
            * This table allows to numerically navigate the dataset through a colored grid.
            * It uses online pagination and is therefore not limited by the size of the dataset.

        You can select a tuple in either of those views by clicking on it. A section with a legend and filters is also available and can be used to deselect the tuple.

        #### D - Selection infos

        Once a tuple is selected, you can obtain its data and explore its counterexample neighbordhood in this section. Two main views are available:

        * Graph view
            * This presents an interactive counterexample graph. Nodes correspond to tuples and there is an edge between two tuples if they are a counterexample.
            * You can change the depth of the graph with the slider (if nothing changes, maximum depth has already been reached).
            * By hovering a node, you get the details of its corresponding tuple on the right side.
            * By clicking a node, you can select it and make it the root of the graph (as in section C).
        * Table view
            * This table provides a numerical exploration up to depth 1.
            * You can also select a tuple in this table by clicking on it.

    ''')
]