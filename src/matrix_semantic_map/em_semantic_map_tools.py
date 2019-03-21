import warnings
import json
from jsonpath_rw import parse
import numpy
import pandas as pd
import loompy
from schema_test_suite import get_validator, validate
import numpy as np
from OLS_tools import OLSQueryWrapper

def check_string(x):
    if isinstance(x, numpy.str):
        return True
    else:
        warnings.warn("Specified path does not point to list of strings.") # ??
        return False


def is_json(myjson):
    try:
        json.loads(myjson)
    except:
        return False
    return True


def dot_path2jpath(dot_path, json_string):
    j = json.loads(json_string)
    path = parse(dot_path)
    return path.find(j)


def resolve_dot_path(loom, path, value):
    """Convert dot path into loom lookup.
    If column or row, return uniq'd list of contents.
    If attr, return contents, test if JSON, if so, continue path in JSON
    -> return contents"""

    elements = path.split('.')
    if elements[0] == "ca":
        if len(elements) == 1:
            if not value in loom.ca.keys():
                raise Exception("%s not in columns keys" % elements[1])
        if len(elements) == 2:
            if not elements[1] in loom.ca.keys():
                raise Exception("%s not in columns keys" % elements[1])
            column_values = set(loom.ca[elements[1]])
            if check_string(list(column_values)[0]):
                if value in column_values:
                    return True
                else:
                    raise Exception("Mapped value %s not in %s" % (value, path))

    elif elements[0] == "ra":
        row = loom.ra[elements[1]]
        if check_string(row[0]):
            return list(set(row))
    elif elements[0] == "attrs":
        attr = loom.attrs[elements[1]]
        if is_json(attr):
            return dot_path2jpath('.'.join(elements[2:]), attr)
        else:
            return [attr]
    else:
        warnings.warn("unrecognised path %s", path)


class MapBuilder:

    def __init__(self, loom, schema, cell_type_fields=None):

        """
        loom: path to loom file
        schema: path to a schema.
        cell_type_fields: optionally specify one or more fields used to record cell type"""

        self.semantic_map = {"semantic_map": []}
        self.loom = loom  # Connect and close when used.
        self.validator = get_validator(schema)
        if cell_type_fields:
            for f in cell_type_fields:
                self.map_cell_type_field(f)
        self.ols = OLSQueryWrapper()

    def _append_to_map(self, map):
        self.semantic_map['semantic_map'].append(map)

    def map_cell_type_field(self, path):
        components = path.split('.')
        base = '.'.join(components[0:-1])
        name = components[-1]
        self._append_to_map({'name': name,
                             'applicable_to': [base],
                             'maps_to': [{
                                 "name": "is_a",
                                 "id": "rdfs:Type"}
                             ]})

    def add_map(self, name, applicable_to,
                maps_to, relation='', object=''):
        fu = locals().copy()
        fu.pop('self')
        out = {k: v for k, v in fu.items() if v}
        validate(self.validator, {"semantic_map": [out]})

    def enhance_indexes(self):
        # Use OLS to add enhanced indexes to Loom file
        return

    def commit(self):
        """Validate map and, if valid, add to loom"""

        if not validate(self.validator, self.semantic_map):
            raise Exception("Semantic map doesn't validate against schema.")
        with loompy.connect(self.loom) as lc:
            for m in self.semantic_map["semantic_map"]:
                for p in m['applicable_to']:
                    resolve_dot_path(lc, p, m['name'])
                for mt in m['maps_to']:
                    self.ols.get_term(mt['id'])
            lc.attrs['semantic_map'] = json.dumps(self.semantic_map)



        # validate references in loom (applicable_to + name)
        # validate map
        # Add map to loom file
        return json.dumps(self.semantic_map)

    def load_csv_map(self, csv, sep=','):
        table = pd.read_csv(csv, sep=sep)
        table.replace(np.nan, '', inplace=True)
        required_headers = {'name', 'applicable_to',
                            'maps_to_name', 'maps_to_id'}

        optional_headers = {'relation_name', 'relation_id', 'object'}
        headers = set(table.columns)
        missing = required_headers - headers
        extra = headers - (required_headers.union(optional_headers))
        if missing:
            raise Exception(
                'Required columns missing: {}.'
                ''.format(str(missing)))
        elif extra:
            warnings.warn("Additional columns present ({}). "
                          "Ignoring these".format(extra))

        def maps_to_split(maps_to_name, maps_to_id):
            names = maps_to_name.split('|')
            ids = maps_to_id.split('|')
            if not len(names) == len(ids):
                raise Exception("Name and ID numbers don't match up: {} {}"
                                "".format(maps_to_name, maps_to_id))
            maps_to = []
            while names:
                maps_to.append({"name": names.pop(), "id": ids.pop()})
            return maps_to

        for i, r in table.iterrows():
            out = {
                'name': r['name'],
                'applicable_to': r['applicable_to'].split('|'),
                'maps_to': maps_to_split(r['maps_to_name'], r['maps_to_id'])
            }
            if not {'relation_name', 'relation_id', 'object'} - headers:
                if r['relation_name'] and r['relation_id'] and r['object']:
                    out['subject_of'] = {"relation": {'name': r['relation_name'],
                                                      'id': r['relation_id']},
                                         "object": r['object']}
            # Add validation step here?
            self._append_to_map(out)