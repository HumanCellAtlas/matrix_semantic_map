import unittest
from OLS_tools import OLSQueryWrapper, results_to_names


class TestOLSQueryWrapper(unittest.TestCase):

    def setUp(self):
        self.ols = OLSQueryWrapper()

    def test_check_ontology(self):
        assert self.ols.check_ontology('cl') is True
        assert self.ols.check_ontology('asdf') is False

    def test_get_ancestors(self):
        a = self.ols.get_cl_ancestor_labels('CL:0000099')
        b = self.ols.get_cl_ancestor_labels('CL:00000999')


    def test_get_term(self):
        t = self.ols.query('CL:0000099', 'terms')
        tl = results_to_names(t)
        assert 'interneuron' in tl
        t2 = self.ols.query('CL:00000999', 'terms')




if __name__ == '__main__':
    unittest.main()
