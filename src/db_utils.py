from pymongo import MongoClient
import os
import time

def connect_mongo(uri="mongodb://localhost:27017/", db_name="edinet"):
	client = MongoClient(uri)
	return client[db_name]

def insert_file_metadata(db, edinet_code, file_type, file_path, extra_info=None):
	collection = db["files"]
	doc = {
		"edinet_code": edinet_code,
		"file_type": file_type,  # "pdf" o "csv"
		"file_path": file_path,
		"extra_info": extra_info or {}
	}
	collection.insert_one(doc)

def save_company_files(edinet_code, base_dir="../data"):
    db = connect_mongo()
    # Usa un dizionario per gestire i file e inserisci i metadati con insert_many per efficienza.
    def save_company_files_from_dict(edinet_code, file_dict):
        docs = []
        for file_type, files in file_dict.items():
            for file_path in files:
                docs.append({
                    "edinet_code": edinet_code,
                    "file_type": file_type,
                    "file_path": file_path,
                    "extra_info": {}
                })
        if docs:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    db["files"].insert_many(docs)
                    break
                except Exception as e:
                    print(f"Errore durante l'inserimento dei file (tentativo {attempt+1}): {e}")
                    time.sleep(2)
            else:
                print("Impossibile inserire i file dopo vari tentativi.")

def find_company_files(edinet_code):
	db = connect_mongo()
	return list(db["files"].find({"edinet_code": edinet_code}))
