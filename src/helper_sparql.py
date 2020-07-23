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


def get_person_info(lblod_id):
    sparql_url = environ.get('SPARQL_URL')

    query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX adms: <http://www.w3.org/ns/adms#>
        PREFIX person: <http://www.w3.org/ns/person#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
        PREFIX mandaat:<http://data.vlaanderen.be/ns/mandaat#>
            SELECT DISTINCT ?name ?familyName ?listName
            WHERE {
                ?person rdf:type person:Person;
                adms:identifier <%s>;
                persoon:gebruikteVoornaam ?name;
                foaf:familyName ?familyName.
                ?list rdf:type mandaat:Kandidatenlijst;
                mandaat:heeftKandidaat ?person;
                skos:prefLabel ?listName.
        }""" % lblod_id

    res = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )

    result = res.json()['results']['bindings'][0]
    return result
