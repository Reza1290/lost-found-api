from pymongo import MongoClient


def db():
	uri = MongoClient("mongodb+srv://reza:reza1290@cluster0.snqx5vy.mongodb.net/?retryWrites=true&w=majority")

	db = uri["db_lost_found"]
	lf = db.lost_and_found
	
	return db, lf, db.users
	

