import dash_core_components as dcc

about_content = [
    dcc.Markdown('''
        The demonstration paper associated with ADESIT is named *"ADESIT: Visualize the Limits of your Data in a Machine Learning Process"* and is in proceeding of VLDB 21 (International Conference on Very Large Data Bases). 
        Full version of this paper is available [here](https://pastel.archives-ouvertes.fr/LIRIS/hal-03242380v1).

        Authors and developpers:
        * Pierre Faure--Giovagnoli (pierre.faure--giovagnoli@insa-lyon.fr)
        * Marie Le Guilly
        * Jean-Marc Petit
        * Vasile-Marian Scuturici

        We thank Matteo Dumont and Antoine Mandin for their help on the initial development of ADESIT. We also thank Benjamin Bertin and Vincent Barellon for testing the application and their help for its deployment. Finally, we thank the Datavalor initiative at INSA Lyon for funding a part of this work.

        ADESIT is coded in Python (>=3.7) based on the Dash framework. Counterexample analysis is powered by the [fastg3](https://github.com/datavalor/fastg3) python library.
        Sources are available on [GitHub](https://github.com/datavalor/adesit).

        Copyright (c) 2021, DataValor. All rights reserved.
    ''')
]