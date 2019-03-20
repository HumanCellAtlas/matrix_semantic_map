import requests
import warnings


def results_to_names(results, include_synonyms=True):
    """Takes OLS term query returns list of all labels and synonyms"""
    out = []
    for t in results['_embedded']['terms']:
        out.append(t['label'])
        if include_synonyms and t['synonyms']:
            out.extend(t['synonyms'])  # Consider being more conservative
                                       # and only selecting synonyms
                                       # of a certain type
    return out


class OLSQueryWrapper:

    def __init__(self):
        self.api_base = "https://www.ebi.ac.uk/ols/api/ontologies"
        self.cl_upper = set(
            results_to_names(
                self.query('CL:0000548', 'ancestors')))
        self.cl_upper.add('animal cell')

    def _gen_query_url(self, curie, query, id_field='id'):
        cp = curie.split(':')
        if not len(cp) == 2:
            raise Exception("{} is not a curie".format(curie))
        db = cp[0]
        # acc = cp[1]
        ontology = db.lower()
        if ontology =='bfo':
            ontology = 'ro'
        if self.check_ontology(ontology):
            return '/'.join([self.api_base, ontology,
                         query + '?' + id_field + '=' + curie])  # Yuk - can id be passed as data?
        else:
            return False

    def check_ontology(self, o):
        r = requests.get('/'.join([self.api_base, o]))
        if r.status_code == 200:
            j = r.json()
            if "ontologyId" in j.keys() and j['ontologyId'] == o:
                return True
        warnings.warn("The ontology %s is not known to OLS" % o)
        return False

    def query(self, curie, query):
        # First check if ontology exists, warn if not.

        id_field = 'id'
        if query == 'terms':
            id_field = 'obo_id'

        # Not building paging for now.
        """CURIE must be a valid OBO curie e.g. CL:0000017
        query may be: descendants, parents, children, ancestors
        """

        # TODO: Extend to work for non OBO Library ontologies (pass a curie map)
        # TODO: Add paging
        url = self._gen_query_url(curie, query, id_field=id_field)
        if not url:
            return False
        response = requests.get(url)
        if not response.status_code == 200:
            raise ConnectionError("Connection error: %s (%s). "
                                  "Possibly due to %s not being a valid term"
                                  "" % (response.status_code,
                                        response.reason,
                                        curie))
        results = response.json()

        if not ('_embedded' in results.keys()) or not ('terms' in results['_embedded'].keys()):
            warnings.warn("No term returned.")
            # This is rather unsatisfactory - but this has to cover both empty results lists
            # and unrecognised query word
        return results

    def get_ancestors(self, curie):
        return self.query(curie, 'ancestors')

    def get_cl_ancestor_labels(self, curie):
        all_ancestors = self.get_ancestors(curie)
        return set(all_ancestors) - self.cl_upper


    def get_term(self, curie):
        #url = self.gen_query_url(curie, 'terms', id_field='obo_id')
        #r = requests.get(url)
        return self.query(curie, query='terms')

