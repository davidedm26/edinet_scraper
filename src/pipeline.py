import argparse
from utils.db_utils import populate_companies_collection, connect_mongo, clear_db
from utils.scraper import extract_all_for_company
from utils.codeList_utils import build_codeList_file
from utils.reset_environment import reset_data_folder
from utils.paths import DATA_DIR
import os

def process_pending_companies():
    db = connect_mongo()
    for company in db["companies"].find({"status": "pending"}):
        edinet_code = company["edinet_code"]
        print(f"Processo azienda: {edinet_code}")
        try:
            stats = extract_all_for_company(edinet_code, max_files=10000, max_workers=32)
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "done", "stats": stats}}
            )
        except Exception as e:
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "error", "error": str(e)}}
            )

def run_pipeline(START_FROM_ZERO=False):
    try:
        if START_FROM_ZERO:
            clear_db()
            reset_data_folder()
        build_codeList_file()
        populate_companies_collection(os.path.join(DATA_DIR, "Edinet_codeList.csv"))
        process_pending_companies()
    except KeyboardInterrupt:
        print("Keyboard interruption detected. Exiting the program.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EDINET pipeline.")
    parser.add_argument(
        "--start-from-zero",
        action="store_true",
        help="Clear DB and reset data folder before running pipeline"
    )
    args = parser.parse_args()
    run_pipeline(args.start_from_zero)