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


def get_lblod_cities():
    sparql_url = environ.get('SPARQL_URL')

    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
    PREFIX ns2: <http://data.vlaanderen.be/ns/besluit#>
    SELECT DISTINCT ?cityName ?cityURI
    WHERE {
        ?list rdf:type ns1:Kandidatenlijst;
        ns1:behoortTot ?election.
        ?election ns1:steltSamen ?bestuursOrgaan.
        ?bestuursOrgaan ns1:isTijdspecialisatieVan ?bestuursOrgaan2.
        ?bestuursOrgaan2 ns2:bestuurt ?bestuursEenheid.
        ?bestuursEenheid ns2:werkingsgebied ?cityURI.
        ?cityURI rdfs:label ?cityName.
    }"""
    res = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )
    results = res.json()['results']['bindings']
    return results


def get_lblod_lists(city_url):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX ns2: <http://data.vlaanderen.be/ns/besluit#>
        PREFIX ns3: <http://www.w3.org/ns/prov#>
        SELECT DISTINCT ?cityURI ?cityName ?list
        WHERE {
            ?bestuursEenheid ns2:werkingsgebied <%s>.
            ?bestuursOrgaan ns2:bestuurt ?bestuursEenheid.
            ?bestuursOrgaan2 ns1:isTijdspecialisatieVan ?besuursOrgaan.
            ?election ns1:steltSamen ?bestuursOrgaan2.
            ?list ns1:behoortTot ?election.
        }""" % city_url
    return None


def get_lblod_candidates(list_url):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX ns1: <http://data.vlaanderen.be/ns/mandaat#>
        PREFIX ns2: <https://data.vlaanderen.be/ns/besluit#>
        SELECT DISTINCT ?personURI ?name
        WHERE {
            <%s> ns1:heeftKandidaat ?personURI.
            ?personURI ns1:gebruikteVoornaam ?name;
            
        }""" % (list_url)
    return None
