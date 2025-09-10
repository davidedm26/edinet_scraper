import argparse
import os
from utils.db_utils import populate_companies_collection, connect_mongo, clear_db
from utils.scraper import extract_all_for_company
from utils.codeList_utils import build_codeList_file
from utils.reset_environment import reset_data_folder
from utils.paths import DATA_DIR

def process_pending_companies():
    db = connect_mongo()
    # Snapshot of pending company codes 
    pending_codes = [c["edinet_code"] for c in db["companies"].find({"status": "pending"}, {"edinet_code": 1, "_id": 0})]
    print(f"Pending companies to process: {len(pending_codes)}")
    for edinet_code in pending_codes:
        # Set to 'running' only if still pending (avoid race conditions)
        res = db["companies"].update_one(
            {"edinet_code": edinet_code, "status": "pending"},
            {"$set": {"status": "running", "started_at": int(__import__('time').time())}}
        )
        if res.modified_count == 0:
            # Already taken by another instance or status changed
            continue
        print(f"Processing company: {edinet_code}")
        try:
            stats = extract_all_for_company(edinet_code, max_files=10000, max_workers=32)
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "done", "stats": stats}}
            )
        except Exception as e:
            db["companies"].update_one(
                {"edinet_code": edinet_code},
                {"$set": {"status": "error"}}
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
        raise


def run_with_retries(start_from_zero: bool, max_retries: int = 3, delay_seconds: int = 10):
    """Run the pipeline with simple retries on any exception (except KeyboardInterrupt).
    - start_from_zero is applied only on the first effective attempt.
    - max_retries includes the first attempt (e.g. 3 = 1 attempt + 2 retries).
    """
    attempt = 0
    already_reset = False
    while attempt < max_retries:
        attempt += 1
        apply_reset = start_from_zero and not already_reset
        print(f"[PIPELINE] Attempt {attempt}/{max_retries} (start_from_zero={apply_reset})")
        try:
            run_pipeline(START_FROM_ZERO=apply_reset)
            print("[PIPELINE] Completed successfully.")
            return
        except KeyboardInterrupt:
            print("[PIPELINE] Stopped by user. No further retries.")
            return
        except Exception as e:
            print(f"[PIPELINE] Failure on attempt {attempt}: {e}")
            already_reset = True  # Prevent additional resets in later attempts
            if attempt >= max_retries:
                print("[PIPELINE] Max retries reached. Giving up.")
                return
            print(f"[PIPELINE] Retrying in {delay_seconds}s...")
            try:
                import time as _t
                _t.sleep(delay_seconds)
            except KeyboardInterrupt:
                print("[PIPELINE] Interrupted during wait. Exiting.")
                return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run EDINET pipeline.")
    parser.add_argument(
        "--start-from-zero",
        action="store_true",
        help="Clear DB and reset data folder before running pipeline"
    )
    args = parser.parse_args()
    # Run with fixed retries (default: 3 attempts, 10s delay)
    run_with_retries(args.start_from_zero, max_retries=3, delay_seconds=10)