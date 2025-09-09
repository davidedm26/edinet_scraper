from db_utils import populate_companies_collection, connect_mongo
from edinet_scraper import extract_all_for_company
import os

DATA_DIR = os.path.join(os.path.dirname(__file__),".." ,"data") 

def process_pending_companies():
    db = connect_mongo()
    for company in db["companies"].find({"status": "pending"}):
        edinet_code = company["edinet_code"]
        print(f"Processo azienda: {edinet_code}")
        try:
            stats = extract_all_for_company(edinet_code)
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "done", "stats": stats}}
            )
        except Exception as e:
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "error", "error": str(e)}}
            )

def run_pipeline():
    # Popola la collection delle aziende (solo se serve)
    populate_companies_collection(os.path.join(DATA_DIR, "Edinet_codeList.csv"))
    process_pending_companies()

if __name__ == "__main__":
    run_pipeline()