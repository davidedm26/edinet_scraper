from pymongo import MongoClient
from pymongo.errors import BulkWriteError

def connect_mongo(uri="mongodb://localhost:27017/", db_name="edinet"):
    client = MongoClient(uri)
    db = client[db_name]
    # Crea indice unico su document_name+company_name se non esiste
    try:
        db["files"].create_index(
            [("document_name", 1), ("file_type", 1), ("edinet_code", 1)],
            unique=True
        )
    except Exception as e:
        print(f"Errore creazione indice: {e}")
    return db


# Usa un dizionario per gestire i file e inserisci i metadati con insert_many per efficienza.
def save_company_files_from_dict(file_dict):
    db = connect_mongo()
    if file_dict:
        collection = db["files"]
        try:
            collection.insert_many(file_dict, ordered=False)
            print(f"Saved {len(file_dict)} documents in 'files'.")
        except BulkWriteError as bwe:
            # Ignora solo i duplicati, mostra altri errori
            for error in bwe.details.get("writeErrors", []):
                if error.get("code") == 11000:
                    op = error.get('op', {})
                    print(f"Duplicato: document_name={op.get('document_name')}, file_type={op.get('file_type')}, edinet_code={op.get('edinet_code')}")
                else:
                    print(f"Errore inserimento: {error}")
        except Exception as e:
            print(f"Errore inserimento batch: {e}")

def find_company_files(edinet_code):
    db = connect_mongo()
    return list(db["files"].find({"edinet_code": edinet_code}))


if __name__ == "__main__":
    sample_files = find_company_files("E02166")
    for f in sample_files:
        print(f)