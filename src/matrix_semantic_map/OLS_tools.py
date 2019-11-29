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


def curie_2_obo_ontology(curie):
    cp = curie.split(':')
    if not len(cp) == 2:
        raise Exception("{} is not a curie".format(curie))
    db = cp[0]
    # acc = cp[1]
    ontology = db.lower()
    return ontology


class OLSQueryWrapper:

    # Should probably (re)-consider using pip install ols-client.

    def __init__(self):
        self.api_base = "https://www.ebi.ac.uk/ols/api/ontologies"
        self.upper_ont_filters = {}

    def set_upper_ont_filter(self, ont, upper_bound_term):
        if not (ont in self.upper_ont_filters.keys()):
            self.upper_ont_filters[ont] = set()

        self.upper_ont_filters[ont].update(set(
            results_to_names(
                self.query(upper_bound_term, 'ancestors'))))

    def set_upper_ont_filter_cl_cell(self):
        self.set_upper_ont_filter('cl', 'CL:0000548')

    def set_upper_ont_filter_fbbt_cell(self):
        self.set_upper_ont_filter('fbbt', 'FBbt:00007002')

    def _gen_query_url(self, curie, query, id_field='id'):
        """Use curie to generate OBO-style ontology identifier
          Check whether ontology exists
          return query URL
        query may be: terms, descendants, parents, children, ancestors.
        terms query requires id_field='obo_id'"""
        cp = curie.split(':')
        if not len(cp) == 2:
            raise Exception("{} is not a curie".format(curie))
        db = cp[0]
        # acc = cp[1]
        ontology = db.lower()
        if ontology == 'bfo' and query == 'properties':
            ontology = 'ro'
        if self.check_ontology(ontology):
            return '/'.join([self.api_base, ontology,
                             query + '?' + id_field + '=' + curie])  # Yuk - can id be passed as data?
        else:
            return False

    def check_ontology(self, o):
        """Check whether ontology 'o' is known to OLS.  Returns boolean."""
        r = requests.get('/'.join([self.api_base, o]))
        # Exception handling is a bit crude.
        if r.status_code == 200:
            j = r.json()
            if "ontologyId" in j.keys() and j['ontologyId'] == o:
                return True
        warnings.warn("The ontology %s is not known to OLS" % o)
        return False

    def query(self, curie, query):
        """curie must be a valid OBO curie e.g. CL:0000017
        query may be: terms, descendants, parents, children, ancestors
        returns JSON or False."""

        # TODO: Extend to work for non OBO Library ontologies (pass a curie map)
        # TODO: Add paging
        # TODO: For terms query - add backup query for properties.

        ### For terms query, treating curie as OBO ID:

        id_field = 'id'
        if query == 'terms':
            id_field = 'obo_id'

        url = self._gen_query_url(curie, query, id_field=id_field)
        # print(url)
        if not url:
            return False
        response = requests.get(url)
        if response.status_code == 404:
            if query == "terms":
                query = "properties"
                url = self._gen_query_url(curie, query, id_field=id_field)
                if not url:
                    return False
                # print(url)
                response = requests.get(url)
                if response.status_code == 404:
                    warnings.warn("Content not found: %s" % curie)
            else:
                warnings.warn("Content not found: %s" % curie)
        elif response.status_code == 200:
            results = response.json()

            if not ('_embedded' in results.keys()) or not ('terms' in results['_embedded'].keys()):
                warnings.warn("No term returned.")
            # TODO: Improve warnings error handling.

            # This is very unsatisfactory - but this has to cover both empty results lists
            # and unrecognised query word

            return results

        else:
            raise ConnectionError(" %s (%s) on query for %s. "
                                  "" % (response.status_code,
                                        response.reason,
                                        curie))

    def get_ancestor_labels(self, curie):
        al = self.query(curie, 'ancestors')
        if al:
            obo = curie_2_obo_ontology(curie)

            if obo == 'cl':
                if not 'cl' in self.upper_ont_filters.keys():
                    self.set_upper_ont_filter_cl_cell()

            if obo == 'fbbt':
                if not 'fbbt' in self.upper_ont_filters.keys():
                    self.set_upper_ont_filter_cl_cell()

            if obo in self.upper_ont_filters.keys():
                return set(results_to_names(al)) - set(self.upper_ont_filters[obo])
            else:
                return results_to_names(al)
        else:
            return []

    def get_term(self, curie):
        # url = self.gen_query_url(curie, 'terms', id_field='obo_id')
        # r = requests.get(url)
        return self.query(curie, query='terms')
