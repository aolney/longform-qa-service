# longform-qa-service

A flask-based Docker image providing a deep-learning long-form question answering service (question in, answer out).

## Installation

A conda env is provided. Simply execute:

```
conda env create -f environment.yml
```
followed by:

```
conda activate longform-qa
```
The `models` model folder is not distributed and must be created.
See **TODO** for steps to create your own model.

## Server

The server is contained in `app.py` with helper functions in `lfqa_utils.py` so all modifications should be made there.

### Development

#### Terminal 1: Start Elasticsearch:

E.g. using a [command line installation](https://www.elastic.co/guide/en/elasticsearch/reference/current/targz.html):

```
./elasticsearch-7.7.1/bin/elasticsearch & 
```

#### Terminal 2: Start Flask:

```
export ENV_TORCH_HOME=./models
export TRANSFORMERS_CACHE=./models
export HF_HOME=./models
conda activate longform-qa
export FLASK_APP=app.py
flask run
```

### Deployment

The Dockerfile in specifies a build using [Gunicorn](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/) for production.
You can build a docker image with e.g.:

```
docker build --tag longform-qa-service:1.0 .
```

Because the docker image depends on Elasticsearch, you need to use Docker Compose to connect an Elasticsearch container to the QA container:

```
docker-compose up
```

Note that you may need to change the ports, etc., in `docker-compose.yml` to match your needs and/or pull the docker image from docker hub instead of building your own. In particular, port 9200 on the Elasticsearch node is left open to allow for flexible access outside the current API (e.g. custom document loading). **Obviously nothing will happen if you don't load documents into Elasticsearch first.**

[Postman](https://learning.postman.com/) tests are in `longform-qa.postman_collection.json`, with different ports for flask and gunicorn (5000 for flask, 8000 for gunicorn).
These tests document how to call the server, but essentially it is POSTing JSON like this:

```json
{
    "question":"What is the difference between the cerebrum and the cerebellum?"
}
```
