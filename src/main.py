from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint
from sanic_cors import CORS
from playhouse.shortcuts import model_to_dict
from peewee import IntegrityError, DoesNotExist
import models
from rdflib import Graph, RDF
from rdflib.namespace import FOAF
from os import environ

import helper_sparql

app = Sanic('Test API')
app.blueprint(swagger_blueprint)
app.config["API_TITLE"] = "Solid Elections API"
app.config["API_DESCRIPTION"] = "API documentation of the Solid Elections API"
CORS(app)


# Middleware to automatically open/close a database connection for every request
@app.middleware('request')
async def handle_request(request):
    """Open database connection before each request is handled."""
    models.db.connect()


@app.middleware('response')
async def handle_response(request, response):
    """Close database connection after each request is handled."""
    if not models.db.is_closed():
        models.db.close()


@app.route('/store/', methods=['POST'])
@doc.summary("store a new web id")
async def r_store(req):
    """
    Store a new webID in the database given a valid webID uri and a lblod uri.

    Keyword arguments:
    The request should contain valid json parameters for 'uri' and 'lblod'.
        Example:
            {
                "uri": "https://jonasvervloet.inrupt.net/profile/card#me",
                "lblod_id": "http://data.lblod.info/id/personen/41e449eafddf2c0c2365a294376780293d92fb401241589a1f403cdff8d2ce5a"
            }

    Returns:
    The response contains json name/value pairs 'success', 'updated' and 'message'.
        'success' denotes if the right query parameters are available and if they are valid.
        'updated' denotes if the webID uri and lblod uri pair is stored in the database.
            This is set to False when the webID uri is already used in the database.
        'message' clarifies the response.

        Example:
            {
                'success': True
                'updated': True
                'message': "WebID successfully added tot the database!"
            }
    """

    # Get 'uri' and 'lblod_id' from JSON body and throw HTTP/400 if one of them is missing
    uri = req.json.get('uri')
    lblod_id = req.json.get('lblod_id')
    if not uri or not lblod_id:
        return response.json({'success': False, 'updated': False, 'message': 'Please set the "uri" and "lblod_id" fields in your JSON body'}, status=400)

    if not helper_sparql.lblod_id_exists(lblod_id):
        return response.json({'success': False, 'updated': False, 'message': 'This lblod ID does not exist in our dataset'}, status=400)

    # Try to add the data to the database, throw HTTP/400 if user tries to add an existing value
    web_id = models.WebID(uri=uri, lblod_id=lblod_id)
    try:
        web_id.save()
    except IntegrityError:
        return response.json({'success': True, 'updated': False, 'message': 'WebID or lblod ID already exists in database'}, status=400)

    return response.json({'success': True, 'updated': True, 'message': 'WebID succesfully added to the database!'})


@app.route('/get')
@doc.summary("get all the web id's")
@doc.description("This endpoints can be used to retrieve all the web id's that are stored in the database")
async def r_get(req):
    """
    Get all stored webIDs in the database.

    :return:
    """
    return response.json(get_web_ids())


@app.route('/cities', methods=['GET'])
async def get_handler(req):
    cities = helper_sparql.get_lblod_cities()
    return response.json(
        {
            'success': True,
            'result': cities
        }
    )


@app.route('/lists', methods=['GET'])
async def get_handler(req):
    try:
        city_uri = req.args['cityURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False
            },
            status=400
        )
    lists = helper_sparql.get_lblod_lists(city_uri)
    return response.json(
        {
            'success': True,
            'result': lists
        }
    )


@app.route('/candidates', methods=['GET'])
async def get_handler(req):
    try:
        list_uri = req.args['listURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False,
            },
            status=400
        )
    candidates = helper_sparql.get_lblod_candidates(list_uri)
    for candidate in candidates:
        try:
            web_id_uri = get_web_id(candidate['personURI']['value'])
            candidate['webID'] = {
                'type': 'literal',
                'value': web_id_uri
            }
        except DoesNotExist:
            continue
    return response.json(
        {
            'success': True,
            'result': candidates
        }
    )


@app.route('/person', methods=['GET'])
async def get_handler(req):
    try:
        person_uri = req.args['personURI'][0]
    except KeyError:
        return response.json(
            {
                'message': 'Wrong query parameters',
                'succes': False,
            },
            status=400
        )
    info = helper_sparql.get_lblod_person_info(person_uri)
    return response.json(
        {
            'success': True,
            'result': info
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


def get_web_id(lblod_id):
    web_id = models.WebID.get(models.WebID.lblod_id == lblod_id)
    return web_id.uri


def check_equal_names(name1, name2):
    # TODO: check for small typo's?
    return name1 == name2


if __name__ == '__main__':
    # Connect to database & create tables if necessary
    models.db.create_tables([models.WebID])
    models.db.close()
    app.run(host='0.0.0.0', port=8000, debug=environ.get('DEBUG'))
