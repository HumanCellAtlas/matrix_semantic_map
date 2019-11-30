import warnings
import json
from jsonpath_rw import parse
import pandas as pd
import loompy
from matrix_semantic_map.schema_test_suite import get_validator, validate
import numpy as np
from matrix_semantic_map.OLS_tools import OLSQueryWrapper
import pkg_resources
import os

def check_string(x):
    if isinstance(x, np.str):
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
        attrs = loom.attrs
        #print(type(attrs))
        #print(path)
        attrs_metadata = attrs[elements[1]]
        if is_json(attrs_metadata):
            return dot_path2jpath('.'.join(elements[2:]), attrs_metadata)
        else:
            return False
    else:
        warnings.warn("unrecognised path %s", path)


class MapBuilder:

    def __init__(self, loom, schema=None, cell_type_fields=None, validate_loom=True):

        """
        loom: path to loom file
        schema: path to JSON schema file.  If schema not specified, attempts to use package
         or repo version.
        cell_type_fields: optionally specify one or more fields used to record cell type"""
        if not schema:
            try:
                schema = pkg_resources.resource_filename(
                            "matrix_semantic_map",
                            "json_schema/expression_matrix_semantic_map.json")
                assert os.path.isfile(schema) is True
            except:
                try:
                    schema = pkg_resources.resource_filename(
                        "matrix_semantic_map",
                        "../json_schema/expression_matrix_semantic_map.json")
                    assert os.path.isfile(schema) is True
                except FileNotFoundError:
                    warnings.warn("Schema file (expression_matrix_semantic_map.json) "
                                  "not found in expected default location for package"
                                  " installation or running from repo. Please specify"
                                  " location via schema argument.")
                else:
                    pass
            else:
                pass

        self.loom = loom  # Connect and close when used.
        self.validate_loom = validate_loom
        self.semantic_map = {"semantic_map": []}
        with loompy.connect(loom, validate=self.validate_loom) as lc:
            if 'semantic_map' in lc.attrs.keys():
                self.semantic_map = json.loads(lc.attrs.semantic_map)
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


    def uniq(self):
        """Remove duplicates from semantic map."""
        ### Probably safer to refactor to make dict here the working representation
        smd = {}
        for sm in self.semantic_map['semantic_map']:
            for app_to in sm['applicable_to']:
                smd[app_to + '.' + sm['name']] = sm
        self.semantic_map = { 'semantic_map': list(smd.values())}

    def add_ancestor_lookup(self):
        for m in self.semantic_map["semantic_map"]:
            al = set()
            for mt in m['maps_to']:
                al.update(self.ols.get_ancestor_labels(mt['id']))
            m['ancestor_name_lookup'] = list(al)

    def query_by_ancestor(self, term):
            return [(x['name'], x['maps_to'])
                   for x in self.semantic_map['semantic_map']
                   if term in x['ancestor_name_lookup']]

    def get_query_terms(self):
        out = set()
        for m in self.semantic_map['semantic_map']:
            if m['ancestor_name_lookup']:
                out.update(set(m['ancestor_name_lookup']))
                for mt in m['maps_to']:
                    out.add(mt['name'])
        return out

    def validate_map(self, offline=False):
        if not validate(self.validator, self.semantic_map):
            raise Exception("Semantic map doesn't validate against schema.")
        with loompy.connect(self.loom, validate=self.validate_loom) as lc:
            for m in self.semantic_map["semantic_map"]:
                for p in m['applicable_to']:
                    resolve_dot_path(lc, p, m['name'])
                if not offline:
                    for mt in m['maps_to']:
                        self.ols.get_term(mt['id'])


    def commit(self, offline = False, validate_loom=True):
        """Validate map and, if valid, add to loom"""

        # TODO: Split out validation into a separate method.
        # TODO: Add option to update, vs stomp (current behavior)
        self.uniq()
        self.validate_map(offline=offline)
        with loompy.connect(self.loom, validate=validate_loom) as lc:
            lc.attrs['semantic_map'] = json.dumps(self.semantic_map)

        # validate references in loom (applicable_to + name)
        # validate map
        # Add map to loom file
        return json.dumps(self.semantic_map)  # better to return oython data structure?

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
