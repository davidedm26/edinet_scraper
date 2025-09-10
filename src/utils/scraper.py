"""Standard imports"""
import os
import time
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

"""Local imports"""
from workers.csv_worker import download_csv_worker
from workers.pdf_worker import download_pdf_worker

"""Portable paths"""
from utils.paths import DATA_DIR, PROJECT_ROOT
output_csv_path = os.path.join(DATA_DIR, "Edinet_codeList.csv")
    
def search_files_by_company(edinet_code, session=None):
    """
    Searches for files for a specific company (edinet_code).
    Returns the list of found results and the tokens.
    """
    # If no session is provided, create one and get tokens
    if session is None:
        session, tokens = get_session_tokens()
    else:
        _, tokens = get_session_tokens()

    search_page_url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"

    # Set request headers with required tokens and user agent
    headers = {
        "ajax_security_token": tokens["ajax_token"],
        "x-gxauth-token": tokens["gx_auth_token"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://disclosure2.edinet-fsa.go.jp",
        "Referer": search_page_url,
        "X-Requested-With" : "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "gxajaxrequest": "1"
    }

    # Main POST request payload for searching documents
    payload = {
        "MPage": False,
        "cmpCtx": "",
        "parms": [
            [],
            {
                "SEARCH_KEY_WORD": edinet_code,
                "CONTAIN_FUND": False,
                "SYORUI_SYUBETU": (
                    "120,130,140,150,160,170,350,360,010,020,030,040,050,060,070,080,090,100,"
                    "110,135,136,200,210,220,230,235,236,240,250,260,270,280,290,300,310,320,"
                    "330,340,370,380,180,190,"
                ),
                "KESSAN_NEN": "",
                "KESSAN_TUKI": "",
                "TEISYUTU_FROM": "19000101",
                "TEISYUTU_TO": "20250904",
                "FLS": True,
                "LPR": True,
                "RPR": True,
                "OTH": True,
                "TEISYUTU_KIKAN": 7
            },
            "WEEE0040",
            "Simple document search",
            2,
            1,
            100,
            {
                "SaitoKubun": "",
                "SennimotoId": "WEEE0040"
            },
            "1",
            False,
            "[]",
            0
        ],
        "events": [
            "T(O(14,'WEEE0030_EVENTS'),72).BACKSETPARAMETER"
        ],
        "grids": {},
        "hsh": [
            {"hsh": tokens["gx_hash_name"], "row": ""},
            {"hsh": tokens["gx_hash_desc"], "row": ""},
            {"hsh": tokens["gxhash_vW_PAGEMAX"], "row": ""},
            {"hsh": tokens["gxhash_vW_LANGUAGE"], "row": ""}
        ],
        "objClass": "weee0040",
        "pkgName": "GeneXus.Programs"
    }

    # Send the initial POST request
    response = session.post(search_page_url, headers=headers, json=payload)
    data = response.json()
    total_results = int(data.get("gxValues", [{}])[0].get("AV84W_TotalCount", 0))
    results_per_page = 100
    total_pages = (total_results + results_per_page - 1) // results_per_page

    all_results = []
    # Loop through all pages to collect results
    for page in range(1, total_pages + 1):
        if page == 1:
            prev_results_json = "[]"
        else:
            prev_results_json = json.dumps(all_results)
        # Prepare payload for pagination
        payload_pagination = {
            "MPage": False,
            "cmpCtx": "",
            "parms": [
                "WEEE0040",
                "Simple document search",
                {
                    "SEARCH_KEY_WORD": edinet_code,
                    "CONTAIN_FUND": False,
                    "SYORUI_SYUBETU": "120,130,140,150,160,170,350,360,010,020,030,040,050,060,070,080,090,100,110,135,136,200,210,220,230,235,236,240,250,260,270,280,290,300,310,320,330,340,370,380,180,190,",
                    "KESSAN_NEN": "",
                    "KESSAN_TUKI": "",
                    "TEISYUTU_FROM": "19000101",
                    "TEISYUTU_TO": "20250904",
                    "FLS": True,
                    "LPR": True,
                    "RPR": True,
                    "OTH": True,
                    "TEISYUTU_KIKAN": 7
                },
                page,
                page,
                results_per_page,
                {
                    "SaitoKubun": "",
                    "SennimotoId": "WEEE0040",
                    "SdtYuzaJoho": {
                        "YuzaId": "",
                        "EdinetKodo": "",
                        "Yuzamei": "",
                        "KengenKodo": "",
                        "ZaimukyokuKodo": "",
                        "SaishuRoguinJikan": "0000-00-00T00:00:00",
                        "KoshinJikan": "0000-00-00T00:00:00",
                        "Pasuwadojotai": "",
                        "SaishuPasuwadokoshin": "0000-00-00T00:00:00",
                        "SakujoFuragu": "",
                        "Roguinshippaikaisu": 0,
                        "RoguinFLG": "",
                        "GamUserGUID": ""
                    }
                },
                "1",
                False,
                prev_results_json,
                total_results
            ],
            "hsh": [
                {"hsh": tokens["gx_hash_name"], "row": ""},
                {"hsh": tokens["gx_hash_desc"], "row": ""},
                {"hsh": tokens["gxhash_vW_PAGEMAX"], "row": ""},
                {"hsh": tokens["gxhash_vW_LANGUAGE"], "row": ""}
            ],
            "objClass": "weee0040",
            "pkgName": "GeneXus.Programs",
            "events": ["'DOBTN_PAGER'"],
            "grids": {}
        }
        # Send POST request for each page
        response_page = session.post(search_page_url, headers=headers, json=payload_pagination)
        data_page = response_page.json()
        results_json = data_page.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
        results = json.loads(results_json)
        results = [r for r in results if r.get("EDINET_CD") == edinet_code]
        all_results.extend(results)
    return all_results, tokens


def download_pdfs(results, edinet_code, session, tokens, max_files=300, max_workers=32):
    """
    Downloads PDF files in parallel using multithreading.
    Shows progress bar and prints final statistics.
    """
    total = min(len(results), max_files)
    start_time = time.time()
    pdf_downloaded = 0
    pdf_not_found = 0
    errors = 0
    batch_metadata = []

    from tqdm import tqdm
    with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=total, desc="Download PDF", unit="file", position=0) as pbar:
        futures = []
        for idx, doc in enumerate(results):
            if idx >= max_files:
                break
            futures.append(executor.submit(download_pdf_worker, doc, edinet_code, session, tokens))
            #print(doc) 
        for idx, future in enumerate(as_completed(futures)):
            success, info_and_metadata = future.result()
            if success and isinstance(info_and_metadata, tuple):
                pdf_downloaded += 1
                #import pprint
                #pprint.pprint(info_and_metadata[1])
                batch_metadata.append(info_and_metadata[1])
                
            elif info_and_metadata[0] in ("not_found"):
                pdf_not_found += 1
            else:
                errors += 1
            pbar.set_postfix({"Downloaded": pdf_downloaded, "Not found": pdf_not_found, "Errors": errors})
            pbar.update(1)

    elapsed = time.time() - start_time
    print("\n--- FINAL STATISTICS ---")
    print(f"PDFs downloaded: {pdf_downloaded}")
    print(f"PDFs not found: {pdf_not_found}")
    print(f"Errors: {errors}")
    print(f"Total time: {elapsed:.2f} seconds")
    
    stats = {
        "pdf_downloaded": pdf_downloaded,
        "pdf_not_found": pdf_not_found,
        "pdf_errors": errors,
        "pdf_time": elapsed
    }
    
    return stats, batch_metadata    


def download_csvs(results, edinet_code, session, tokens, max_files=300, max_workers=16):
    """
    Downloads CSV files in parallel using multithreading.
    """
    total = min(len(results), max_files)
    start_time = time.time()
    csv_downloaded = 0
    csv_not_found = 0
    errors = 0
    batch_metadata = []

    from tqdm import tqdm
    with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=total, desc="Download CSV", unit="file", position=1) as pbar:
        futures = []
        for idx, doc in enumerate(results):
            if idx >= max_files:
                break
            futures.append(executor.submit(download_csv_worker, doc, edinet_code, session, tokens))
        for idx, future in enumerate(as_completed(futures)):
            success, info_and_metadata = future.result()
            if success and isinstance(info_and_metadata, tuple):
                csv_downloaded += 1
                batch_metadata.append(info_and_metadata[1])            
            elif info_and_metadata[0] in ( "not_found") :
                csv_not_found += 1
            else:
                errors += 1
            pbar.set_postfix({"Downloaded": csv_downloaded, "Not found": csv_not_found, "Errors": errors})
            pbar.update(1)

    elapsed = time.time() - start_time
    print("\n--- FINAL STATISTICS (CSV) ---")
    print(f"CSVs downloaded: {csv_downloaded}")
    print(f"CSVs not found: {csv_not_found}")
    print(f"Errors: {errors}")
    print(f"Total time: {elapsed:.2f} seconds")

    stats = {
        "csv_downloaded": csv_downloaded,
        "csv_not_found": csv_not_found,
        "csv_errors": errors,
        "csv_time": elapsed
    }

    return stats, batch_metadata

def get_session_tokens():
    """
    Performs the initial GET and returns:
    - requests session with cookies
    - dictionary with all required tokens (extracted from GXState)
    """
    import requests
    from bs4 import BeautifulSoup

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    session = requests.Session()
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        gxstate_input = soup.find("input", {"name": "GXState"})
        if gxstate_input is not None:
            gxstate_raw = gxstate_input["value"]
            gxstate = json.loads(gxstate_raw)
            tokens = {
                "gx_auth_token": gxstate.get("GX_AUTH_WEEE0040"),
                "ajax_token": gxstate.get("AJAX_SECURITY_TOKEN"),
                "gx_hash_name": gxstate.get("gxhash_vPGMNAME"),
                "gx_hash_desc": gxstate.get("gxhash_vPGMDESC"),
                "gxhash_vW_PAGEMAX": gxstate.get("gxhash_vW_PAGEMAX"),
                "gxhash_vW_LANGUAGE": gxstate.get("gxhash_vW_LANGUAGE"),
                "session_cookies": session.cookies.get_dict()
            }
            return session, tokens
        else:
            print(f"[get_session_tokens] Attempt {attempt}: GXState not found. Retrying...")
            if attempt < max_retries:
                import time
                time.sleep(2)
            else:
                print("[get_session_tokens] Error: GXState not found after several attempts.")
                print(response.text[:1000])  # Print first 1000 characters for debug
                raise RuntimeError("GXState not found in initial page")

def extract_pdf_url_from_html(html):
    """
    Extracts the direct PDF URL from HTML, searching for the pdfView('...') call.
    Returns the URL as a string or None if not found.
    """
    match = re.search(r"pdfView\('([^']+\.pdf[^\']*)'\)", html)
    if match:
        return match.group(1)
    return None

def extract_all_for_company(edinet_code, max_files=300, max_workers=16):
    """
    Sequential version: downloads first PDFs, then CSVs, and saves metadata to the database.
    """
    session, tokens = get_session_tokens()
    results, _ = search_files_by_company(edinet_code, session=session)
    print(f"Total results for {edinet_code}: {len(results)}")

    import utils.db_utils as db_utils
    # Download PDFs
    pdf_stats, pdf_metadata = download_pdfs(results, edinet_code, session, tokens, max_files, max_workers)
    # Download CSVs
    csv_stats, csv_metadata = download_csvs(results, edinet_code, session, tokens, max_files, max_workers)
    # Save metadata to MongoDB
    # Prepare dictionary for batch insert
    all_metadata = pdf_metadata + csv_metadata

    #from pprint import pprint
    #pprint(all_metadata)

    db_utils.save_company_files(all_metadata)
    # Merge statistics and metadata
    stats_per_company = {
        "pdf_downloaded": pdf_stats.get("pdf_downloaded", 0),
        "pdf_not_found": pdf_stats.get("pdf_not_found", 0),
        "pdf_errors": pdf_stats.get("pdf_errors", 0),
        "pdf_time": pdf_stats.get("pdf_time", 0),
        "csv_downloaded": csv_stats.get("csv_downloaded", 0),
        "csv_not_found": csv_stats.get("csv_not_found", 0),
        "csv_errors": csv_stats.get("csv_errors", 0),
        "csv_time": csv_stats.get("csv_time", 0)
    }
    return stats_per_company


if __name__ == "__main__":
    try:
        # Run CSV cleaning and schedule batch tasks
        #codeList_utils.get_codeList()
        #codeList_utils.clean_CodeList()
        #schedule_tasks_from_codeList(batch_size=10)
        #from utils.db_utils import clear_db
        #clear_db()
        extract_all_for_company("E02166", max_files=5, max_workers=16)
    except KeyboardInterrupt:
        print("Exit....")