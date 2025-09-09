import pandas as pd
# Funzione per popolare la collection 'companies' da Edinet_codeList.csv

from pymongo import MongoClient
from pymongo.errors import BulkWriteError

def connect_mongo(uri="mongodb://localhost:27017/", db_name="edinet"):
    client = MongoClient(uri)
    db = client[db_name]
    # Crea indice unico su document_name+company_name se non esiste
    from pymongo.errors import PyMongoError
    try:
        db["files"].create_index(
            [("document_name", 1), ("file_type", 1), ("edinet_code", 1)],
            unique=True
        )
    except PyMongoError as e:
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


def populate_companies_collection(csv_path):
    """
    Updates the 'companies' collection from the CSV file codeList
    Prints the companies that were added.
    """
    import os
    if not os.path.exists(csv_path):
        print(f"Errore: il file '{csv_path}' non esiste.")
        return

    db = connect_mongo()
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    companies = []
    for _, row in df.iterrows():
        edinet_code = row.get("EDINET_CD", row.iloc[0])
        company_name = row.get("COMPANY_NAME", row.iloc[2] if len(row) > 2 else "")
        companies.append({
            "edinet_code": edinet_code,
            "company_name": company_name,
            "status": "pending"
        })
    # Crea indice unico se non esiste
    db["companies"].create_index([
        ("edinet_code", 1)
    ], unique=True)
    if companies:
        from pymongo.errors import BulkWriteError
        try:
            result = db["companies"].insert_many(companies, ordered=False)
            print(f"Aziende aggiunte: {len(result.inserted_ids)}")
        except BulkWriteError as bwe:
            duplicate_count = sum(1 for error in bwe.details.get("writeErrors", []) if error.get("code") == 11000)
            added_count = len(companies) - duplicate_count
            if added_count >= 0:
                print(f"Added companies: {added_count}")
            if duplicate_count:
                print(f"Already stored companies: {duplicate_count}")
        except Exception as e:
            print(f"Error updating companies: {e}")




if __name__ == "__main__":
    sample_files = find_company_files("E02166")
    populate_companies_collection("./data/Edinet_codeList.csv")
    #for f in sample_files:
    #    print(f)