import unittest
from matrix_semantic_map.em_semantic_map_tools import MapBuilder
import os
import requests


class TestMapBuilder(unittest.TestCase):

    def setUp(self):
        print(os.getcwd())
        self.schema_path = "json_schema/expression_matrix_semantic_map.json"
        self.resources_dir = "matrix_semantic_map/test/resources/"
        if not os.path.isfile("matrix_semantic_map/test/resources/Cortex.loom"):
            cortex_request = requests.get("http://loom.linnarssonlab.org/clone/Previously%20Published/Cortex.loom",
                                          stream=True)  # Site down?
            cortex_file = open("matrix_semantic_map/test/resources/cortex.loom", "wb")
            cortex_file.write(cortex_request.raw.read())
            cortex_file.close()


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

if __name__ == '__main__':
    unittest.main()
