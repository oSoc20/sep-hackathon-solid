# SolidElections API
Hackathon project for the Simplification Election Procedures team. This API simply stores a WebID and returns a list of stored WebIDs, which can be used to fetch Solid documents.


## Setup (development)
To run this project as a development server, you will need [docker-compose](https://docs.docker.com/compose/install/). You will also need to set some environment variables, the easiest way to do this is to create an `.env` file (format `VARIABLE=value`) in the project root.

[![asciicast](https://asciinema.org/a/7U61VYBxH6xwjn6CUsb1X7byW.svg)](https://asciinema.org/a/7U61VYBxH6xwjn6CUsb1X7byW)

- **DEBUG** - Setting this to *any* value (including `0` or `False`) will enable Sanic's debug mode, which gives you hot-reload functionality and more verbose error logging. Please don't enable this in production.
- **PG_HOST** - The host of the Postgres instance. Default: `db`
- **PG_DBNAME** - Name of Postgres database. Default: `postgres`
- **PG_USER** - Name of Postgres user. Default: `postgres`
- **PG_PASS** - Password to use for this user. Run `pwgen 30 1` to generate a random password.
- **SPARQL_URL** - URL for the Virtuoso SPARQL endpoint. Default: `http://api.sep.osoc.be:8890/sparql`


## Setup (production)
To deploy this to a Docker Swarm instance, first copy the `docker-compose-prod.yml` file from this repository to your instance. Then create a `pgdata` folder for persistent database storage, a `virtuoso-data` folder for Virtuoso's triple storage and a `letsencrypt` to store the TLS certificates generated for Traefik.  
Now set the environment variables in an `.env` file as described above, plus a `HOST` variable with the domain name and `LETSENCRYPT_EMAIL` for the e-mail address you want to use for Let's Encrypt (for expiration warnings).

```bash
# To deploy the stack
env $(cat .env | xargs) docker stack deploy -c docker-compose-prod.yml solid-elections-api

# To update the API container (you can set this up as a webhook)
docker service update --image solidelections/api solid-elections-api_api
```