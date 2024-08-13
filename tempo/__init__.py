from typing import TypedDict, Final, Callable, Tuple, Dict
from json import loads
import requests_cache
import itertools
import requests
import base64

BASE_URL: Final[str] = 'http://statistici.insse.ro:8077/tempo-ins/'

SESSION_DB_PATH: str = 'cache'
requests_cache.install_cache(SESSION_DB_PATH)

eq_lambda = lambda a, b: a == b
in_lambda = lambda a, b: b in a
gt_lambda = lambda a, b: a > b
gte_lambda = lambda a, b: a >= b
st_lambda = lambda a, b: a < b
ste_lambda = lambda a, b: a <= b

class Option:
    label: str
    code: int
    offset: int
    parent_id: int

    @classmethod
    def from_json(cls, data):
        o = Option()
        o.label = data['label'] # .strip()
        o.code = data['nomItemId']
        o.offset = data['offset']
        o.parent_id = data['parentId']
        return o
    
    def to_json(self):
        return {
            'label': self.label,
            'nomItemId': self.code,
            'offset': self.offset,
            'parentId': self.parent_id
        }

class Dimension:
    label: str
    code: int
    options: list[Option]

    @classmethod
    def from_json(cls, data):
        d = Dimension()
        d.label = data['label']
        d.code = data['dimCode']
        d.options = list(map(Option.from_json, data['options']))
        return d
    
    def to_json(self):
        return {
            'dimCode': self.code,
            'label': self.label,
            'options': [o.to_json() for o in self.options]
        }
    
    def options_by_label(self, label: str) -> list[Option]:
        return [o for o in self.options if label in o.label]
    
    def option_by_code(self, code: int) -> Option|None:
        return next(filter(lambda o: o.code == code, self.options), None)

class Node:
    code: str
    url: str
    name: str
    comment: str
    _level: int = None
    _parent_code: str = None
    _children: list[any] = None

    @classmethod
    def from_json(cls, data: dict):
        ctx = data.get('context', data)
        if ctx['childrenUrl'] == 'matrix':
            new_data = requests.get(BASE_URL+'matrix/'+data['code']).json()
            return LeafNode.from_json(new_data, data['code'])

        n = Node()
        n.code = ctx['code']
        n.name = ctx['name']
        n.comment = ctx['comment']
        n.url = BASE_URL + ctx['url'] + '/' + n.code
        n._level = data.get('level', None)
        n._parent_code = data.get('parentCode', None)
        return n

    @classmethod
    def get_all(cls, code: str = '') -> list[any]:
        data = requests.get(BASE_URL+'context/'+code).json()
        if code != '':
            data = data['children']
        return list(map(cls.from_json, data))
    
    @classmethod
    def by_property(cls, prop: str, value: any, cb: Callable = eq_lambda, code: str = '', arr: list[any] = None) -> list[any]:
        if arr is None:
            arr = cls.get_all(code)

        props = prop.split(".")
        def valid(e):
            temp = e
            for p in props:
                temp = getattr(temp, p)
            return cb(temp, value)
        return [e for e in arr if valid(e)]

    @classmethod
    def by_name(cls, value: str):
        return first_element(cls.by_property('name', value, in_lambda))
    
    @classmethod
    def by_code(cls, value: str):
        return first_element(cls.by_property('code', value))
    
    @property
    def parent_code(self):
        if self._parent_code is None:
            n = self.from_json(requests.get(url).json())
            self._parent_code = n.parent_code
        return self._parent_code
    
    @property
    def level(self):
        if self._level is None:
            n = self.from_json(requests.get(url).json())
            self._level = n.level
        return self._level

    @property
    def children(self):
        if self._children is None:
            self._children = self.by_property('parent_code', self.code, eq_lambda, self.code)
        return self._children

class LeafNode(Node):
    periodicity: list[str]
    data_sources: list[object]
    definition: str
    metodology: str
    observations: str
    last_updated: str
    dimensions: list[Dimension]
    details: Dict[str, int]

    @classmethod
    def from_json(cls, data, code):
        n = LeafNode()
        n.name = data['matrixName']
        n.code = code
        n.url = BASE_URL + 'matrix/' + n.code
        n._level = len(data['ancestors'])
        n._parent_code = data['ancestors'][-1]['code']
        n.periodicity = data['periodicitati']
        n.data_sources = data['surseDeDate']
        n.definition = data['definitie']
        n.metodology = data['metodologie']
        n.last_updated = data['ultimaActualizare']
        n.observations = data['observatii']
        n.dimensions = list(map(Dimension.from_json, data['dimensionsMap']))
        n.details = data['details']
        return n
    
    @classmethod
    def by_code(cls, code: str):
        data = requests.get(BASE_URL+'matrix/matrices').json()
        match = first_element([n for n in data if n['code'] == code])
        if match:
            data = requests.get(BASE_URL+'matrix/'+match['code']).json()
            return cls.from_json(data, match['code'])
        return match
    
    @classmethod
    def by_name(cls, name: str):
        data = requests.get(BASE_URL+'matrix/matrices').json()
        match = first_element([n for n in data if name in n['name']])
        if match:
            data = requests.get(BASE_URL+'matrix/'+match['code']).json()
            return cls.from_json(data, match['code'])
        return match
    
    def dimensions_by_label(self, label: str) -> list[Dimension]:
        return [d for d in self.dimensions if label in d.label]
    
    def dimension_by_code(self, code: int) -> Dimension|None:
        return next(filter(lambda d: d.code == code, self.dimensions), None)
    
    def query(self, *args):
        query_str = []

        for arg in args:
            d: Dimension = first_element(self.dimensions_by_label(arg[0]))
            options: list[Option] = itertools.chain.from_iterable(
                [d.options_by_label(o) for o in arg[1]])
            codes = [str(o.code) for o in options]
            query_str.append(','.join(codes))
        
        response = requests.post(BASE_URL+'pivot', json={
            'encQuery': ':'.join(query_str),
            'language': 'ro',
            'matCode': self.code,
            'matMaxDim': self.details['matMaxDim'],
            'matRegJ': self.details['matRegJ'],
            'matUMSpec': self.details['matUMSpec']
        })

        return response.text

def first_element(arr: list[any]) -> any:
    try:
        return arr[0]
    except IndexError:
        return None