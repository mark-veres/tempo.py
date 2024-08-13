# tempo.py
A python library for working with the National Institute of Statistics [Tempo Online Database](http://statistici.insse.ro:8077/tempo-online/#/pages/tables/insse-table). There's also an already existing [R package](https://github.com/RProjectRomania/TEMPO).

**🚧 UNDER CONSTRUCTION 🚧**

## Example usage
```py
from tempo import Node, LeafNode

nodes = Node.get_all()
[print(" " * n.level + n.name) for n in nodes]
# A. STATISTICA SOCIALA
#  A.1 POPULATIE SI STRUCTURA DEMOGRAFICA <a href="...">
#   1. POPULATIA REZIDENTA
#   2. POPULATIA DUPA DOMICILIU
#   3. DATE ISTORICE DE POPULATIE (1968 - 1991)
#  A.2 MISCAREA NATURALA A POPULATIEI
# ...

nodes = Node.get_all('10')
[print(n.name) for n in nodes]
# 1. POPULATIA REZIDENTA
# 2. POPULATIA DUPA DOMICILIU
# 3. DATE ISTORICE DE POPULATIE (1968 - 1991)
```

```py
from tempo import eq_lambda

nodes = Node.by_property('level', 0, eq_lambda)
[print(n.name) for n in nodes]
# A. STATISTICA SOCIALA
# B. STATISTICA ECONOMICA
# C. FINANTE
# D. JUSTITIE
# E. MEDIU INCONJURATOR
# F. UTILITATI PUBLICE SI ADMINISTRAREA TERITORIULUI
# H. DEZVOLTARE DURABILA - Tinte 2030
# G. DEZVOLTARE DURABILA - Orizont 2020
```

```py
leaf = LeafNode.by_code('POP105A')
q = leaf.query(
    ('Varste si grupe de varsta', ['Total']),
    ('Sexe', ['Masculin']),
    ('Medii de rezidenta', ['Rural']),
    ('Macroregiuni, regiuni de dezvoltare si judete', ['Bihor']),
    ('Perioade', ['Anul 2016', 'Anul 2017']),
    ('UM: Numar persoane', ['Numar persoane'])
)
# Varste si grupe de varsta, Sexe, Medii de rezidenta, Macroregiuni  regiuni de dezvoltare si judete, Perioade, UM: Numar persoane, Valoare
# Total, Masculin, Rural, Bihor, Anul 2016, Numar persoane, 144439
# Total, Masculin, Rural, Bihor, Anul 2017, Numar persoane, 145335
```

## Concepts
To better understand the concepts of this library it's useful to look at the [visual interface of Tempo](http://statistici.insse.ro:8077/tempo-online/#/pages/tables/insse-table).

### Data organization
All data is organized hierarchically, with all nodes having a specified level, code, parent code, name and more.

### API and Data extraction
Extrating data from Tempo is done through a JSON API. Take a look at these URLs for better understanding.
```
http://statistici.insse.ro:8077/tempo-ins/context/
http://statistici.insse.ro:8077/tempo-ins/context/1010
http://statistici.insse.ro:8077/tempo-ins/matrix/POP105A
```

### Nodes and Leaf Nodes
The differences between nodes and leaf nodes are:  
- leaf nodes are located at the bottom of the hierarchy
- leaf nodes are accessed through the `tempo-ins/matrix` route instead of the `tempo-ins/context` route
- normal nodes are used just for organization
- leaf nodes actually enable us to query the database

### Querying, Dimensions and Options
Querying for data is done by sending a POST request to the URL of the leaf node and providing the following request body:

```json
{
    "language": "ro",
    "arr": [
        [
            {
                "label": "<option label>",
                "nomItemId": 1,
                "offset": 1,
                "parentId": null
            }
        ],
        "..."
    ],
    "matrixName": "<leaf name>",
    "matrixDetails": {
        "nomJud": 0,
        "nomLoc": 0,
        "...": "..."
    }
}
```

Dimensions are characteristics of the dataset and each dimension has multiple options. Each element of the `arr` JSON element corresponds to a dimension and contains the data for the selected options.