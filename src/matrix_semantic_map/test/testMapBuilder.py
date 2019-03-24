import unittest
from matrix_semantic_map.matrix_map_tools import MapBuilder
import os
import requests


def _get_resource_file(file_path, url):
    if not os.path.isfile('/'.join(file_path)):
        req = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(req.raw.read())


class TestMapBuilder(unittest.TestCase):
    def setUp(self):
        print(os.getcwd())
        self.schema_path = "json_schema/expression_matrix_semantic_map.json"
        self.resources_dir = "matrix_semantic_map/test/resources/"
        # Get  resource files if not already present
        _get_resource_file(self.resources_dir + "Cortex.loom",
                           "http://loom.linnarssonlab.org/clone/Previously%20Published/Cortex.loom")
        _get_resource_file(self.resources_dir + "Desplan_Fly_AdultOpticLobe_57k.loom",
                           "http://scope.aertslab.org/#/695988e2-61c5-4625-a6a4-e937d9854824/Desplan_Fly_AdultOpticLobe_57k.loom")


    def test_map_builder_construction(self):
        mb = MapBuilder(
            loom=self.resources_dir + "Cortex.loom",
            schema=self.schema_path,
            cell_type_fields=['ca.Class'])
        print(mb.commit())

    def test_add_map(self):
        mb = MapBuilder(
            loom=self.resources_dir + "Cortex.loom",
            schema=self.schema_path,
            cell_type_fields=['ca.Class'])
        mb.add_map(name='interneurons',
                   applicable_to=['ca.Class'],
                   maps_to=[{
                         "name": "interneuron",
                         "id": "CL:0000099"}])
        print(mb.commit())

    def test_csv_loader(self):
        mb = MapBuilder(
            loom=self.resources_dir + "Cortex.loom",
            schema=self.schema_path,
            cell_type_fields=['ca.Class'])
        mb.load_csv_map(self.resources_dir + "cortex_map.tsv", sep='\t')
        print(mb.commit())

    def test_csv_loader_header_json(self):
        mb = MapBuilder(
            loom=self.resources_dir + "Desplan_Fly_AdultOpticLobe_57k.loom",
            schema=self.schema_path,
            cell_type_fields=['attrs.MetaData.clusterings[*].clusters[*].description'])
        mb.load_csv_map(self.resources_dir + "Desplan_Fly_AdultOpticLobe_map.tsv", sep='\t')
        print(mb.commit())

    def test_add_ancestor_map(self):
        mb = MapBuilder(
            loom=self.resources_dir + "Desplan_Fly_AdultOpticLobe_57k.loom",
            schema=self.schema_path,
            cell_type_fields=['attrs.MetaData.clusterings[*].clusters[*].description'])
        mb.load_csv_map(self.resources_dir + "Desplan_Fly_AdultOpticLobe_map.tsv", sep='\t')
        mb.add_ancestor_lookup()
        print(mb.commit())


if __name__ == '__main__':
    unittest.main()
