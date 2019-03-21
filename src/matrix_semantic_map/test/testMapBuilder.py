import unittest
from em_semantic_map_tools import MapBuilder
import os
import requests


class TestMapBuilder(unittest.TestCase):

    def setUp(self):
        if not os.path.isfile("./resources/Cortex.loom"):
            cortex_request = requests.get("http://loom.linnarssonlab.org/clone/Previously%20Published/Cortex.loom",
                                          stream=True)  # Site down?
            cortex_file = open("resources/cortex.loom", "wb")
            cortex_file.write(cortex_request.raw.read())
            cortex_file.close()


    def test_map_builder_construction(self):
        mb = MapBuilder(
            loom="resources/Cortex.loom",
            schema="../json_schema/expression_matrix_semantic_map.json",
            cell_type_fields=['ca.Class'])
        print(mb.commit())

    def test_add_map(self):
        mb = MapBuilder(
            loom="resources/Cortex.loom",
            schema="../json_schema/expression_matrix_semantic_map.json",
            cell_type_fields=['ca.Class'])
        mb.add_map(name='interneurons',
                   applicable_to=['ca.Class'],
                   maps_to=[{
                         "name": "interneuron",
                         "id": "CL:0000099"}])
        print(mb.commit())

    def test_csv_loader(self):
        mb = MapBuilder(
            loom="resources/Cortex.loom",
            schema="../json_schema/expression_matrix_semantic_map.json",
            cell_type_fields=['ca.Class'])
        mb.load_csv_map("resources/cortex_map.tsv", sep='\t')
        print(mb.commit())

if __name__ == '__main__':
    unittest.main()
