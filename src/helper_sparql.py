import requests
from os import environ


def lblod_id_exists(lblod_id):
    sparql_url = environ.get('SPARQL_URL')

    query = """
    PREFIX ams: <http://www.w3.org/ns/adms#>
    SELECT DISTINCT ?id
    WHERE {
        ?id ams:identifier <%s>.
    }""" % (lblod_id)
    res = requests.get(
            sparql_url,
            params={
                "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
                "format": "json",
                "query": query
            }
        )

    results = res.json()['results']['bindings']
    return bool(results)