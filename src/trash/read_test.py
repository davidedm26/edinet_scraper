import os
from pymongo import MongoClient

# Leggi la variabile d'ambiente
mongo_uri = os.environ.get("MONGO_URI")

# Connetti a MongoDB
client = MongoClient(mongo_uri)
db = client.test

for doc in db.test_collection.find():
    print(doc)
