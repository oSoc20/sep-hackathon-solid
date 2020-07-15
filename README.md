# SolidElections API
Hackathon project for the Simplification Election Procedures team. This API simply stores a WebID and returns a list of stored WebIDs, which can be used to fetch Solid documents.


## Setup
To run this project, you will either need [docker-compose](https://docs.docker.com/compose/install/) or a Docker Swarm instance. You will also need to set some environment variables, the easiest way to do this is to create an `.env` file (format `VARIABLE=value`) in the project root.

- **DEBUG** - Setting this to *any* value (including `0` or `False`) will enable Sanic's debug mode, which gives you hot-reload functionality and more verbose error logging. Please don't enable this in production.
- **PG_HOST** - The host of the Postgres instance. Default: `db`
- **PG_DBNAME** - Name of Postgres database. Default: `postgres`
- **PG_USER** - Name of Postgres user. Default: `postgres`
- **PG_PASS** - Password to use for this user. Run `pwgen 30 1` to generate a random password.

To start the development server using docker-compose, just run `docker-compose up` in the project root.

To deploy this to a Docker Swarm instance, copy the `docker-compose-prod.yml` file from this repository to your instance and run `docker stack deploy -c docker-compose-prod.yml solid-elections-api` with the above environment variables set manually (`docker stack deploy` does not support `.env` files) or prepend the command with `env $(cat .env | xargs)` to use the `.env` file. You can also set up a webhook that runs `docker service update --image samvdkris/osoc-docker solid-elections-api_api` to deploy new images.