from pymongo import MongoClient
import os

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")  # legge la variabile d'ambiente
client = MongoClient(mongo_uri)

db = client.test
result = db.test_collection.insert_one({"nome": "pippo"})
print("Documento inserito con id:", result.inserted_id)
