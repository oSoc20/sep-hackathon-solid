from sanic import Sanic, response
from sanic_openapi import doc, swagger_blueprint
from sanic_cors import CORS
from playhouse.shortcuts import model_to_dict
from peewee import IntegrityError
import models
from rdflib import Graph, RDF
from rdflib.namespace import FOAF
from os import environ

app = Sanic('Test API')
app.blueprint(swagger_blueprint)
app.config["API_TITLE"] = "Solid Elections API"
app.config["API_DESCRIPTION"] = "API documentation of the Solid Elections API"
CORS(app)


@app.route('/store/', methods=['POST'])
@doc.summary("store a new web id")
async def r_store(req):
    uri = req.json['uri']
    web_id = models.WebID(uri=uri)

    try:
        web_id.save()
    except IntegrityError:  # Thrown when you try to add an existing unique value
        return response.json({'success': False, 'message': 'WebID already exists in database'}, status=400)

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


def get_web_ids():
    web_ids = models.WebID.select()

    web_ids = [model_to_dict(web_id) for web_id in web_ids]  # Convert list of ModelSelect objects to Python dicts
    for web_id in web_ids:
        web_id['date_created'] = web_id['date_created'].isoformat()  # Convert Python datetime object to ISO 8601 string

    return web_ids


def check_equal_names(name1, name2):
    # TODO: check for small typo's?
    return name1 == name2


if __name__ == '__main__':
    models.db.create_tables([models.WebID])  # Connect to database & create tables if necessary
    app.run(host='0.0.0.0', port=8000, debug=environ.get('DEBUG'))
