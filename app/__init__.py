import flask
from flask_jwt_extended import JWTManager
from controllers import connect
from bson import ObjectId
from controllers import api
from config import config

db, lf, users = connect.db()

def create_app(name):

    app = flask.Flask(name)

    app.config['JSON_SORT_KEYS'] = False
    # app.json.sort_keys = False
    app.config['JWT_SECRET_KEY'] = 'rahasia'

    app.config.update(**config)

    app.register_blueprint(api)
    jwt = JWTManager(app)
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return users.find_one({"_id": ObjectId(identity)})

    return app
