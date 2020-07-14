from sanic import Sanic, response
from playhouse.shortcuts import model_to_dict
import models
from rdflib import Graph, RDF
from rdflib.namespace import FOAF
import os
import json

app = Sanic('Test API')


@app.route('/store/', methods=['POST'])
async def r_store(req):
	uri = req.json['uri']
	wid = models.WebID(uri=uri)
	wid.save()
	return response.text('WebID succesfully added to the database!')



@app.route('/get')
async def r_get(req):
	return response.json(get_web_ids())



@app.route('/get/<name>')
async def r_get(req, name):
	web_ids = get_web_ids()

	valid_webids = []
	for web_id in web_ids:
		uri = web_id['uri']
		graph = Graph()
		graph.parse(uri)

		web_id_added = False
		# get all Persons in the solid pod and loop over them
		for person in graph.subjects(RDF.type, FOAF.Person):
			# get all names of these Persons and loop over them
			for webid_name in graph.objects(person, FOAF.name):
				# check if the name on the solid pod equals the given name
				if check_equal_names(name, str(webid_name)):
					valid_webids.append(web_id)
					web_id_added = True
					break

			# make sure the web id is only added once to the list
			if web_id_added:
				break

	return response.json(valid_webids)


def get_web_ids():
	webids = models.WebID.select()

	webids = [model_to_dict(wid) for wid in webids]  # Convert list of ModelSelect objects to Python dicts
	for wid in webids:
		wid['date_created'] = wid['date_created'].isoformat()  # Convert Python datetime object to ISO 8601 string

	return webids



def check_equal_names(name1, name2):
	# TODO: check for small typo's?
	return name1 == name2



if __name__ == '__main__':
	models.db.create_tables([models.WebID])  # Connect to database & create tables if necessary
	app.run(host='0.0.0.0', port=8000, debug=os.environ.get('DEBUG'))