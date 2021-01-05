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

To run the server using flask, do:

# TODO: update for docker elasticsearch and ENV and conda

### Terminal 1: Start Elasticsearch, e.g.:
```
./elasticsearch-7.7.1/bin/elasticsearch & 
```

### Terminal 2: Start Flask:

```
export ENV_TORCH_HOME=./models
export TRANSFORMERS_CACHE=./models
export HF_HOME=./models
conda activate longform-qa
export FLASK_APP=app.py
flask run
```

The Dockerfile in specifies a build using [Gunicorn](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/) for production.
You can build a docker image with e.g.:

```
docker build --tag longform-qa-service:1.0 .
```

and run with, e.g.:

```
docker run -p 8000:8000 longform-qa-service:1.0
```

[Postman](https://learning.postman.com/) tests are in `longform-qa.postman_collection.json`, with different ports for flask and gunicorn (5000 for flask, 8000 for gunicorn).
These tests document how to call the server, but essentially it is POSTing JSON like this:

```json
{
    "question":"What is the difference between the cerebrum and the cerebellum?"
}
```
