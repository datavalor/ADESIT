ADESIT is a web application allowing to explore

It is coded in Python (>=3.7) based on the Dash framework.
The computation of g3 is powered by the [fastg3 python library](https://github.com/datavalor/fastg3).

# Starting guide

On it is launched, ADESIT is available on port 8050.

## Regular

```
pip install -r deploy/requirements.txt
cd dash/
python app.py -d -t -b
```

* -d: debut logs
* -b: no banner
* -t: no time limit

## Docker

```
cd deploy/
docker-compose up
```

# Authors and developers

The demonstration paper associated with ADESIT is named *"ADESIT: Visualize the Limits of your Data in a Machine Learning Process"* and is in proceeding of VLDB 21 (International Conference on Very Large Data Bases). 
Full version of this paper is available [here](https://pastel.archives-ouvertes.fr/LIRIS/hal-03242380v1).

* Pierre Faure--Giovagnoli (pierre.faure--giovagnoli@insa-lyon.fr)
* Marie Le Guilly
* Jean-Marc Petit
* Vasile-Marian Scuturici

We thank Matteo Dumont and Antoine Mandin for their help on the initial development of ADESIT. We also thank Benjamin Bertin and Vincent Barellon for testing the application and their help for its deployment. Finally, we thank the Datavalor initiative at INSA Lyon for funding a part of this work.