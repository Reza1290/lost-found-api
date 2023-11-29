from flask import request,Blueprint, jsonify, json
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
from flask_bcrypt import bcrypt


from datetime import datetime
from .connect import db
from bson import ObjectId


api = Blueprint('api', __name__)

db , lf , users = db()



def check_document_owner(func):
    def wrapper(*args, **kwargs):
        try: 
            current_user = get_jwt_identity()
            entry_id = kwargs.get('entry_id')

            document = lf.find_one({'_id': ObjectId(entry_id)})

            if document and 'user_id' in document:

                document_user_id = str(document['user_id'])
                if current_user and str(current_user) == document_user_id:
                    return func(*args, **kwargs)
                else:
                    return jsonify({"error": "Unauthorized. You are not the owner of the document"}), 403
            else:
                return jsonify({"error": "Document not found or missing 'user_id'"}), 404
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            return jsonify(response), 500

    return wrapper

@api.route('/')
def hello_world():
	return "Kamu Siapa Kenyal Seperti Jelly"



@api.route('/dump',methods=['GET'])
def post():
    try:
        # Sample data
        data = {
            'item_name': 'Laptop',
            'description': 'A silver MacBook Pro',
            'location': 'Coffee Shop XYZ',
            'date': datetime.strptime("2023-11-29T12:30:00Z", "%Y-%m-%dT%H:%M:%SZ"),
            'status': 'lost',
            'createdAt' : datetime.utcnow(),
            'user_id': ObjectId("655ea3b53f12c3eea2822699")
        }
		
        result = lf.insert_one(data)

        response = {
            'status': 'success',
            'message': 'Document inserted successfully',
            'inserted_id': str(result.inserted_id)
        }
		
        return jsonify(response), 201  
    except Exception as e:
        response = {
            'status': 'error',
            'message': str(e)
        }
        return jsonify(response), 500
    
@api.route('/lostfound', methods=['GET'])
@jwt_required()
def get_all_lostfound():
    entries = []

    for document in lf.find():
        result = users.find_one({'_id': document['user_id']})
        if result:
            user_info = {
                'username': result.get('username', 'N/A')
            }
        else:
            user_info = {}

        entries.append({
            'item_name': document.get('item_name', 'N/A'),
            'description': document.get('description', 'N/A'),
            'location': document.get('location', 'N/A'),
            'date': document.get('date', 'N/A'),
            'status': document.get('status', 'N/A'),
            'createdAt': document.get('createdAt', 'N/A'),
            'user_info': user_info
        })
    
    return jsonify(entries)


@api.route('/lostfound/<string:entry_id>', methods=['GET'])
@jwt_required()
@check_document_owner
def get_lostfound(entry_id):
    try:
        entry_id_obj = ObjectId(str(entry_id))
        
        print(entry_id_obj)
        res = lf.find_one({'_id': entry_id_obj})

        if res:
            result = users.find_one({'_id': res['user_id']})
            if result:
                user_info = {
					'username': result.get('username', 'N/A')
				}
            else:
                user_info = {}
    
            response = {
                'status': 'success',
                'data': {
					'item_name': res.get('item_name', 'N/A'),
					'description': res.get('description', 'N/A'),
					'location': res.get('location', 'N/A'),
					'date': res.get('date', 'N/A'),
					'status': res.get('status', 'N/A'),
					'createdAt': res.get('createdAt', 'N/A'),
					'user_info': user_info
				}
            }
            return jsonify(response), 200
        else:
            return jsonify({"status": "error", "message": "Entry not found"}), 404
        
    except Exception as e:
        
        response = {
			'status': 'failed',
			'message' : str(e)
		}
        
        return jsonify(response), 500
    
@api.route('/lostfound', methods=['POST'])
@jwt_required()
def post_lostfound():
	try:
		data = request.data
  		
		data_dict = json.loads(data.decode('utf-8'))
		data_dict['createdAt'] = datetime.utcnow()
  
		result = lf.insert_one(data_dict)
  
		response = {
            'status': 'success',
            'message': 'Document inserted successfully',
            'inserted_id': str(result.inserted_id)
        }

		return jsonify(response), 201
	except Exception as e:
		response = {
			'status' : 'error',
			'message' : str(e)
		}
		return jsonify(response), 500

@api.route('/lostfound/<string:entry_id>', methods=['PUT'])
@jwt_required()
def update_lostfound(entry_id):
    try:
        data = request.data
        data_dict = json.loads(data.decode('utf-8'))
        data_dict['updatedAt'] = datetime.utcnow()

        result = lf.update_one({'_id': ObjectId(entry_id)}, {'$set': data_dict})

        if result.matched_count == 1:
            response = {
                'status': 'success',
                'message': 'Document updated successfully'
            }
            return jsonify(response), 200
        else:
            return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    except Exception as e:
        response = {
            'status': 'error',
            'message': str(e)
        }
        return jsonify(response), 500


@api.route('/lostfound/<string:entry_id>', methods=['DELETE'])
@jwt_required()
def delete_lostfound(entry_id):
    try:
        result = lf.delete_one({'_id': ObjectId(entry_id)})
        if result.deleted_count == 1:
            response = {
                'status': 'success',
                'message': 'Document deleted successfully'
            }
            return jsonify(response), 200
        else:
            return jsonify({'status': 'error', 'message': 'Document not found'}), 404
    except Exception as e:
        response = {
            'status': 'error',
            'message': str(e)
        }
        return jsonify(response), 500


@api.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if data is None:
            return jsonify({"message": "Invalid request. JSON data is missing"}), 400

        username = data.get('username')
        password = data.get('password')

        user = users.find_one({'username': username})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            
            access_token = create_access_token(identity=str(user["_id"]))

            return jsonify({"message": "Login successful", "access_token": access_token}), 200
        else:
            
            return jsonify({"message": "Login failed. Invalid credentials"}), 401

    except Exception as e:
        response = {
            'status': 'error',
            'message': 'KESALAHAN!'
        }
        return jsonify(response), 500
    
@api.route('/register',methods=['POST'])
def register():
    try:
        data = request.json
        if data is None:
            return jsonify({"message": "Invalid request. JSON data is missing"}), 400
		
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        telephone = data.get('telephone')
        address = data.get('address')
        birthdate = data.get('birthdate')

        if not username or not password:
            return jsonify({"message": "Username and password are required"}), 400


        user_data = {
            'username': username,
            'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'email': email,
            'telephone': telephone,
            'address': address,
            'birthdate': birthdate,
            'created_at': datetime.utcnow()
        }

        result = users.insert_one(user_data)

        response = {
            'status': 'success',
            'message': 'User registered successfully',
            'inserted_id': str(result.inserted_id)
        }

        return jsonify(response), 201

    except Exception as e:
        response = {
            'status': 'error',
            'message': str(e)
        }
        return jsonify(response), 400  
