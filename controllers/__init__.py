from flask import request,Blueprint, jsonify
from datetime import datetime, timedelta
from bson import json_util
from pymongo.errors import DuplicateKeyError
from .connect import db


api = Blueprint('api', __name__)

db , lf , users = db()

def get_all_documents(collection_name):
    cursor = db[collection_name].find({})
    documents = [doc for doc in cursor]
    json_documents = json_util.dumps(documents)
    return json_documents	



@api.route('/')
def hello_world():
	# gg = str(pprint.pprint(siswa.find_one({"nama_depan": "reza"})))	
	# gg = db.list_collection_names()
	# gg = 	get_all_documents("")	
	# return 'This Is API With PYTHON + MONGO PUNYA M REZA MUKTASIB' + gg

	return "a"

@api.route('/lostfound', methods=['GET'])
def get_all_lostfound():
	
	current_time = datetime.utcnow()
	time_limit = current_time - timedelta(days=2)
	entries = list(lf.find({"date": {"$gte": time_limit}}))
	
	return jsonify(entries)

@api.route('/lostfound', methods=['POST'])
def post_lostfound():
	data = request.json
	data['date'] = datetime.utcnow()
	data['expiration_date'] = data['date'] + timedelta(days=30)

	result = lf.insert_one(data)
	return jsonify({"message": "Entry added successfully", "id": str(result.inserted_id)}), 201

@api.route('/login',methods=['POST'])
def login():
	data = request.json
	user = users.find_one(data)
	
	if user:
		return jsonify({"message": "Login successful", "user_id": str(user["_id"])}), 200
	else:
		return jsonify({"message": "Login failed. Invalid credentials"}), 401

@api.route('/register',methods=['POST'])
def register():
	data = request.json
	
	try:
		result = users.insert_one(data)
		return jsonify({"status": True, "message": "Registration successful", "user_id": str(result.inserted_id)}), 201
	except DuplicateKeyError	:
		return jsonify({"status": False, "message": "Registration failed. Username already exists"}), 400
	except Exception as e:
		return jsonify({"status": False, "message": f"Registration failed. Usename or Password not" }), 500


