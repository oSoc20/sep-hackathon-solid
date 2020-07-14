from peewee import Model, PostgresqlDatabase, CharField, DateTimeField
import datetime

import secret

# TODO: peewee's docs mention a middleware thing for sanic, but it seems to want to reconnect to the database for every request? Maybe check it out
# http://docs.peewee-orm.com/en/latest/peewee/database.html#sanic
db = PostgresqlDatabase(
	host=secret.PG_HOST,
	database=secret.PG_DBNAME,
	user=secret.PG_USER,
	password=secret.PG_PASS
)

# NOTE: peewee unfortunately does not support automatic schema migrations, so we have to handle this manually if we change a model.
# Fortunately the data we're storing is pretty simple, so this shouldn't happen a lot.
# If this does become an issue there are modules to handle this automatically, but I haven't been able to find one that is actively developed.


class BaseModel(Model):
	"""A base model that will use our Postgresql database"""
	class Meta:
		database = db


class WebID(BaseModel):
	uri = CharField()
	date_created = DateTimeField(default=datetime.datetime.now)