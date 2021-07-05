import dash_core_components as dcc

concepts_content = [
    dcc.Markdown('''
        #### Context
        Suppose you are facing a new supervised learning (SL) challenge: a domain expert asks you if it is possible to predict a **target C** from a set of **features X** by learning on a **dataset r**. 
        To answer this question, it is common for a data scientist to directly jump into the learning step by training a model and  then evaluate it against a testing set to obtain an accuracy.
        If this approach might work, the interpretability of the result is generally rather low: *Why such accuracy, where the errors come from? Could you obtain a better one with a different model or settings?*
        Moreover, it can also be very costly as answering such questions might require many trainings.

        With ADESIT, we propose a tool to better understand your data beforehand in view of that SL problem, allowing to avoid many costly training and to obtain a deeper insight on your data. We target questions such as:
        * What areas of my data might present a problem?
            * How the domain expert could explain those issues and provide potential solutions?
            * How incorporating domain knowledge such as accuracies changes my results?
        * What maximum accuracy should I excpect from my trainings?
        * What features are the most discriminant?


        #### What is a counterexample?
        ADESIT proposes a **counterexample analysis** of your dataset. Imagine a researcher R who needs to predict the specie of an *iris* (pure coincidence...) in function of multiple characteristics of the flower. 
        Notably, R knows that the *sepal length* and the *sepal width* of irises are very disctinctive features. 
        Therefore, R measures those two characteristics for 3 species of 150 flowers and takes a look at the results to evaluate the feasability of the prediction task.
        R notably observes the following pair of tuples:

        | id   | sepal_length | sepal_width | specie |
        |---:|:---:|:---:|:---:|
        | t50 | 5.1 | 3.5 | setosa |
        | t80 | 5.1 | 3.5 | versicolor |

        It appears very clear that something is missing as no model can predict t50 and t80 at the same time!
        
        More formally, R is trying to assess the veracity of the following function: *specie=f(sepal_length, sepal_width)*. It is possible to express this function as a functionnal dependency (FD) in the form:

        φ: sepal_length, sepal_width → specie

        We say that the pair (t50, t80) violates φ: **(t50, t80) forms a counterexample.**. From there, R might go talk with specialist biologist researchers who might indicate to her why such counterexample might be happening. 
        Should R also measure the *petal length* and the *petal width* of the flower, who knows?

        #### About counterexample indicators
        In 1995, Kivinen introduces 3 counterexample indicators to measure the veracity of a FD in a relation:
        * g1 measures the proportion of counterexamples
        * g2 measures the proportion of tuples of involved in a counterexample
        * g3 gives the minimum proportion of tuples to remove from the relation such that no counterexample remains

        In addition to the close inspection of the counterexamples in the dataset, those 3 indicators also bring valuable informations on the problem at hand. 
        Notably, g3 provides an upper bound on the accuracy reachable with any model. 
        Intuitively, this makes sense as a model, being nothing other than a function, cannot predict both tuples of a counterexample correctly (eg. t50 and t80).
    ''')
]