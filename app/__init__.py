import flask

from controllers import api
from config import config

def create_app(name):

    app = flask.Flask(name)

    app.config['JSON_SORT_KEYS'] = False
    app.json.sort_keys = False

    app.config.update(**config)

    app.register_blueprint(api)
    

    return app