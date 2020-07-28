from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint
from sanic_cors import CORS
from playhouse.shortcuts import model_to_dict
from peewee import IntegrityError
import models
from rdflib import Graph, RDF
from rdflib.namespace import FOAF
from os import environ
import requests
import json

import helper_sparql

app = Sanic('Test API')
app.blueprint(swagger_blueprint)
app.config["API_TITLE"] = "Solid Elections API"
app.config["API_DESCRIPTION"] = "API documentation of the Solid Elections API"
CORS(app)


# Middleware to automatically open/close a database connection for every request
@app.middleware('request')
async def handle_request(request):
    models.db.connect()

@app.middleware('response')
async def handle_response(request, response):
    if not models.db.is_closed():
        models.db.close()



@app.route('/store/', methods=['POST'])
@doc.summary("store a new web id")
async def r_store(req):\
        # Get 'uri' and 'lblod_id' from JSON body and throw HTTP/400 if one of them is missing
    uri = req.json.get('uri')
    lblod_id = req.json.get('lblod_id')
    if not uri or not lblod_id:
        return response.json({'success': False, 'message': 'Please set the "uri" and "lblod_id" fields in your JSON body'}, status=400)

    if not helper_sparql.lblod_id_exists(lblod_id):
        return response.json({'success': False, 'message': 'This lblod ID does not exist in our dataset'}, status=400)

    # Try to add the data to the database, throw HTTP/400 if user tries to add an existing value
    web_id = models.WebID(uri=uri, lblod_id=lblod_id)
    try:
        web_id.save()
    except IntegrityError:
        return response.json({'success': False, 'message': 'WebID or lblod ID already exists in database'}, status=400)

    return response.json({'success': True, 'message': 'WebID succesfully added to the database!'})


@app.route('/get')
@doc.summary("get all the web id's")
@doc.description("This endpoints can be used to retrieve all the web id's that are stored in the database")
async def r_get(req):
    return response.json(get_web_ids())


@app.route('/get/<name>')
@doc.summary("get web id filtered by name")
@doc.description("This endpoint can be used to filter the web id's based on their name.")
async def r_get(req, name):
    web_ids = get_web_ids()

    valid_web_ids = []
    for web_id in web_ids:
        uri = web_id['uri']
        graph = Graph()
        graph.parse(uri)

        web_id_added = False
        # get all Persons in the solid pod and loop over them
        for person in graph.subjects(RDF.type, FOAF.Person):
            # get all names of these Persons and loop over them
            for web_id_name in graph.objects(person, FOAF.name):
                # check if the name on the solid pod equals the given name
                if check_equal_names(name, str(web_id_name)):
                    valid_web_ids.append(web_id)
                    web_id_added = True
                    break

            # make sure the web id is only added once to the list
            if web_id_added:
                break

    return response.json(valid_web_ids)


@app.route('/candidates', methods=['GET'])
async def get_handler(req):
    sparql_url = environ.get('SPARQL_URL')

    query = """
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
    PREFIX mandaat:<http://data.vlaanderen.be/ns/mandaat#>
        SELECT DISTINCT ?firstName ?familyName ?listName
        WHERE {
            ?list rdf:type mandaat:Kandidatenlijst;
            skos:prefLabel ?listName;
            mandaat:heeftKandidaat ?person.
            ?person persoon:gebruikteVoornaam ?firstName ;
            foaf:familyName ?familyName .
    }"""
    query_response = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )
    json_response = json.loads(
        query_response.content.decode('utf-8')
    )
    return response.json(json_response['results']['bindings'])


@app.route('/list', methods=['GET'])
async def get_handler(req):
    try:
        name = req.args['name'][0]
        lastname = req.args['lastname'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters!',
                'succes': 'false'
             },
            status=400
        )

    sparql_url = environ.get('SPARQL_URL')

    query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX persoon: <http://data.vlaanderen.be/ns/persoon#>
        PREFIX mandaat:<http://data.vlaanderen.be/ns/mandaat#>
            SELECT DISTINCT ?listName ?listNumber
            WHERE {
                ?person persoon:gebruikteVoornaam "%s";
                foaf:familyName "%s".
                ?list rdf:type mandaat:Kandidatenlijst;
                mandaat:heeftKandidaat ?person;
                skos:prefLabel ?listName;
                mandaat:lijstnummer ?listNumber.
        }""" % (name, lastname)
    query_response = requests.get(
        sparql_url,
        params={
            "default-graph-uri": "http://api.sep.osoc.be/mandatendatabank",
            "format": "json",
            "query": query
        }
    )
    result_json = query_response.json()['results']['bindings']
    if len(result_json) == 0:
        return response.json(
            {
                'succes': 'false',
                'message': 'No person with given name and last name found.'
            },
            status=404
        )
    return response.json(
        {
            'succes': 'true',
            'result': result_json
        }
    )


def get_web_ids():
    web_ids = models.WebID.select()

    # Convert list of ModelSelect objects to Python dicts
    web_ids = [model_to_dict(web_id) for web_id in web_ids]
    for web_id in web_ids:
        # Convert Python datetime object to ISO 8601 string
        web_id['date_created'] = web_id['date_created'].isoformat()

    return web_ids


def check_equal_names(name1, name2):
    # TODO: check for small typo's?
    return name1 == name2


if __name__ == '__main__':
    # Connect to database & create tables if necessary
    models.db.create_tables([models.WebID])
    models.db.close()
    app.run(host='0.0.0.0', port=8000, debug=environ.get('DEBUG'))
