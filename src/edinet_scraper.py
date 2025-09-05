import sys
sys.path.append("../src")
import codeList_utils
import pandas as pd


def schedule_tasks_from_csv(csv_path="../data/Edinet_codeList.csv", batch_size=10):
    """
    Legge i codici dal CSV e processa i task in batch da batch_size.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "Edinet_codeList.csv")
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    codes = df.iloc[:, 0].tolist()  # Prima colonna: Edinet Code
    total = len(codes)
    print(f"Totale aziende da processare: {total}")
    for start in range(0, total, batch_size):
        batch = codes[start:start+batch_size]
        print(f"\nBatch {start//batch_size + 1}: {batch}")
        for edinet_code in batch:
            try:
                extract_all_for_company(edinet_code)
            except Exception as e:
                print(f"Errore per {edinet_code}: {e}")
                
# Funzione per processare i task dal file tasks.json
def process_tasks_from_file(tasks_file="../tasks.json", max_files=300, max_workers_pdf=32, max_workers_csv=16):
    import json
    import os
    tasks_path = os.path.join(os.path.dirname(__file__), tasks_file)
    with open(tasks_path, "r", encoding="utf-8") as f:
        tasks = json.load(f)
    for task in tasks:
        if task.get("status") == "pending":
            edinet_code = task["edinet_code"]
            print(f"\n--- Processing {edinet_code} ---")
            try:
                stats = extract_all_for_company(edinet_code, max_files=max_files, max_workers=max_workers_pdf)
                task["status"] = "done"
                task["stats"] = stats
            except Exception as e:
                print(f"Errore per {edinet_code}: {e}")
                task["status"] = "error"
                task["stats"] = {"error": str(e)}
            # Salva lo stato aggiornato dopo ogni task
            with open(tasks_path, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=2)
    print("\n--- Tutti i task sono stati processati ---")
def search_files_by_company(edinet_code, session=None):
    """
    Searches for files for a specific company (edinet_code).
    Returns the list of found results and the tokens.
    """
    import json

    # If no session is provided, create one and get tokens
    if session is None:
        session, tokens = get_session_tokens()
    else:
        _, tokens = get_session_tokens()

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"

    # Set request headers with required tokens and user agent
    headers = {
        "ajax_security_token": tokens["ajax_token"],
        "x-gxauth-token": tokens["gx_auth_token"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://disclosure2.edinet-fsa.go.jp",
        "Referer": url,
        "X-Requested-With" : "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "gxajaxrequest": "1"
    }

    # Main POST request payload for searching documents
    payload = {
        "MPage":False,
        "cmpCtx":"",
        "parms":[[],{"SEARCH_KEY_WORD": edinet_code,"CONTAIN_FUND":False,"SYORUI_SYUBETU":"120,130,140,150,160,170,350,360,010,020,030,040,050,060,070,080,090,100,110,135,136,200,210,220,230,235,236,240,250,260,270,280,290,300,310,320,330,340,370,380,180,190,","KESSAN_NEN":"","KESSAN_TUKI":"","TEISYUTU_FROM":"19000101","TEISYUTU_TO":"20250904","FLS":True,"LPR":True,"RPR":True,"OTH":True,"TEISYUTU_KIKAN":7},"WEEE0040","Simple document search",2,1,100,{"SaitoKubun":"","SennimotoId":"WEEE0040"},"1",False,"[]",0],
        "events":["T(O(14,'WEEE0030_EVENTS'),72).BACKSETPARAMETER"],
        "grids":{},
        "hsh":[
            {"hsh": tokens["gx_hash_name"], "row": ""},
            {"hsh": tokens["gx_hash_desc"], "row": ""},
            {"hsh": tokens["gxhash_vW_PAGEMAX"], "row": ""},
            {"hsh": tokens["gxhash_vW_LANGUAGE"], "row": ""}
        ],
        "objClass":"weee0040",
        "pkgName":"GeneXus.Programs"
    }

    # Send the initial POST request
    response = session.post(url, headers=headers, json=payload)
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
        response_page = session.post(url, headers=headers, json=payload_pagination)
        data_page = response_page.json()
        results_json = data_page.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
        results = json.loads(results_json)
        all_results.extend(results)
    return all_results, tokens

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from tqdm import tqdm
import time

def download_pdf_worker(doc, edinet_code, session, tokens, max_retries=3):
    """
    Worker function for downloading a single PDF document.
    Skips if SYORUI_KANRI_NO_ENCRYPT is missing.
    """
    import os
    import time

    if not doc.get("SYORUI_KANRI_NO_ENCRYPT"):
        # Documento senza PDF
        return False, "No PDF for this document"

    tipo_documento = doc.get("SYORUI_SB_CD_ID", "unknown")
    save_dir = os.path.join(".", "data", edinet_code, "pdf", tipo_documento)
    os.makedirs(save_dir, exist_ok=True)
    kanri_no_encrypt = doc.get("SYORUI_KANRI_NO_ENCRYPT")
    if not kanri_no_encrypt:
        return False, "Missing SYORUI_KANRI_NO_ENCRYPT"

    hsh_list = [
        tokens.get("gx_hash_name"),
        tokens.get("gx_hash_desc")
    ]
    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    headers = {
        "ajax_security_token": tokens["ajax_token"],
        "x-gxauth-token": tokens["gx_auth_token"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://disclosure2.edinet-fsa.go.jp",
        "Referer": url,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "gxajaxrequest": "1"
    }
    payload_pdf = {
        "MPage": False,
        "cmpCtx": "",
        "parms": [
            "WEEE0040",
            "Simple document search",
            kanri_no_encrypt,
            "",
            "",
            "",
            "",
            [],
        ],
        "hsh": [
            {"hsh": hsh_list[0], "row": ""},
            {"hsh": hsh_list[1], "row": ""}
        ],
        "objClass": "weee0040",
        "pkgName": "GeneXus.Programs",
        "events": ["'DOBTN_PDF'"],
        "grids": {}
    }

    for attempt in range(1, max_retries + 1):
        try:
            response_pdf = session.post(url, headers=headers, json=payload_pdf)
            if response_pdf.status_code != 200:
                raise Exception("Error POST PDF")
            data_pdf = response_pdf.json()
            pdf_url = data_pdf.get("gxProps", [{}])[0].get("PDFDISP", {}).get("Target")
            if not pdf_url:
                raise Exception("PDF URL not found")
            pdf_response = session.get(pdf_url)
            import re
            def extract_pdf_url_from_html(html):
                match = re.search(r"pdfView\('([^']+\.pdf[^\']*)'\)", html)
                if match:
                    return match.group(1)
                return None
            pdf_url_real = extract_pdf_url_from_html(pdf_response.text)
            if not pdf_url_real:
                raise Exception("Real PDF URL not found")
            pdf_file_response = session.get(pdf_url_real)
            if pdf_file_response.status_code == 200 and pdf_file_response.content:
                codice_file = doc.get("SHORUI_KANRI_NO", "unknown")
                filename = os.path.join(save_dir, f"{codice_file}.pdf")
                with open(filename, "wb") as f:
                    f.write(pdf_file_response.content)
                return True, filename
            else:
                raise Exception("PDF download failed")
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)  # Wait before retrying
            else:
                return False, f"Attempt {attempt}: {str(e)}"

def download_pdfs(results, edinet_code, session, tokens, max_files=300, max_workers=32):
    """
    Downloads PDF files in parallel using multithreading.
    Shows progress bar and prints final statistics.
    """
    from tqdm import tqdm
    import time

    total = min(len(results), max_files)
    start_time = time.time()
    pdf_downloaded = 0
    pdf_not_found = 0
    errors = 0

    # Use ThreadPoolExecutor for parallel downloads
    with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=total, desc="Download PDF", unit="file") as pbar:
        futures = []
        for idx, doc in enumerate(results):
            if idx >= max_files:
                break
            futures.append(executor.submit(download_pdf_worker, doc, edinet_code, session, tokens))
        for future in as_completed(futures):
            success, info = future.result()
            if success:
                pdf_downloaded += 1
            elif info in ("No PDF for this document", "Missing SYORUI_KANRI_NO_ENCRYPT"):
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
    
    return {
        "pdf_downloaded": pdf_downloaded,
        "pdf_not_found": pdf_not_found,
        "pdf_errors": errors,
        "pdf_time": elapsed
    }

import re
import base64

def download_csv_worker(doc, edinet_code, session, tokens, max_retries=3):
    import os
    import time

    if not doc.get("SYORUI_KANRI_NO_ENCRYPT"):
        # Documento senza CSV
        return True, "not_found"

    tipo_documento = doc.get("SYORUI_SB_CD_ID", "unknown")
    save_dir = os.path.join(".", "data", edinet_code, "csv", tipo_documento)
    os.makedirs(save_dir, exist_ok=True)
    kanri_no_encrypt = doc.get("SYORUI_KANRI_NO_ENCRYPT")
    if not kanri_no_encrypt:
        return True, "not_found"

    hsh_list = [
        tokens.get("gx_hash_name"),
        tokens.get("gx_hash_desc")
    ]
    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    headers = {
        "ajax_security_token": tokens["ajax_token"],
        "x-gxauth-token": tokens["gx_auth_token"],
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Origin": "https://disclosure2.edinet-fsa.go.jp",
        "Referer": url,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "gxajaxrequest": "1"
    }
    payload_csv = {
        "MPage": False,
        "cmpCtx": "",
        "parms": [
            "WEEE0040",
            "Simple document search",
            kanri_no_encrypt,
            "",
            "",
            "",
            "",
            [],
        ],
        "hsh": [
            {"hsh": hsh_list[0], "row": ""},
            {"hsh": hsh_list[1], "row": ""}
        ],
        "objClass": "weee0040",
        "pkgName": "GeneXus.Programs",
        "events": ["'DOBTN_CSV'"],
        "grids": {}
    }

    for attempt in range(1, max_retries + 1):
        try:
            response_csv = session.post(url, headers=headers, json=payload_csv)
            if response_csv.status_code != 200:
                raise Exception("Error POST CSV")
            data_csv = response_csv.json()
            dl_script = data_csv.get("gxProps", [{}])[0].get("DLSCRIPT", {}).get("Caption", "")
            import re
            match = re.search(r'data:;base64,([A-Za-z0-9+/=]+)', dl_script)
            if not match:
                # CSV non trovato, ma non è errore: non fare retry
                return True, "not_found"
            import base64
            base64_data = match.group(1)
            file_data = base64.b64decode(base64_data)
            codice_file = doc.get("SHORUI_KANRI_NO", "unknown")
            filename = os.path.join(save_dir, f"{codice_file}.zip")
            with open(filename, "wb") as f:
                f.write(file_data)
            return True, filename
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
            else:
                return False, f"Attempt {attempt}: {str(e)}"

def download_csvs(results, edinet_code, session, tokens, max_files=300, max_workers=16):
    """
    Downloads CSV files in parallel using multithreading.
    """
    from tqdm import tqdm
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    total = min(len(results), max_files)
    start_time = time.time()
    csv_downloaded = 0
    csv_not_found = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor, tqdm(total=total, desc="Download CSV", unit="file") as pbar:
        futures = []
        for idx, doc in enumerate(results):
            if idx >= max_files:
                break
            futures.append(executor.submit(download_csv_worker, doc, edinet_code, session, tokens))
        for future in as_completed(futures):
            success, info = future.result()
            if success and info == "not_found":
                csv_not_found += 1
            elif success:
                csv_downloaded += 1
            elif info in ("not_found", "Missing SYORUI_KANRI_NO_ENCRYPT"):
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
    
    return {
        "csv_downloaded": csv_downloaded,
        "csv_not_found": csv_not_found,
        "csv_errors": errors,
        "csv_time": elapsed
    }

def get_session_tokens():
    """
    Performs the initial GET and returns:
    - requests session with cookies
    - dictionary with all required tokens (extracted from GXState)
    """
    import requests
    import json
    from bs4 import BeautifulSoup

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    session = requests.Session()
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        resp = session.get(url)
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
            print(f"[get_session_tokens] Tentativo {attempt}: GXState non trovato. Ritento...")
            if attempt < max_retries:
                import time
                time.sleep(2)
            else:
                print("[get_session_tokens] Errore: GXState non trovato dopo vari tentativi.")
                print(response.text[:1000])  # Stampa i primi 1000 caratteri per debug
                raise RuntimeError("GXState non trovato nella pagina iniziale")

from bs4 import BeautifulSoup
import re

def extract_pdf_url_from_html(html):
    """
    Extracts the direct PDF URL from HTML, searching for the pdfView('...') call.
    Returns the URL as a string or None if not found.
    """
    match = re.search(r"pdfView\('([^']+\.pdf[^\']*)'\)", html)
    if match:
        return match.group(1)
    return None

# Example usage:
import threading

def extract_all_for_company(edinet_code, max_files=300, max_workers=16):
    """
    Esegue ricerca e download PDF/CSV per una singola azienda.
    """
    session, tokens = get_session_tokens()
    risultati, tokens = search_files_by_company(edinet_code, session=session)
    print(f"Totale risultati per {edinet_code}: {len(risultati)}")

    # Scarica PDF e CSV in parallelo
    import threading
    
    pdf_stats = {}
    csv_stats = {}
    def pdf_job():
        nonlocal pdf_stats
        pdf_stats = download_pdfs(risultati, edinet_code, session, tokens, max_files, max_workers)
    def csv_job():
        nonlocal csv_stats
        csv_stats = download_csvs(risultati, edinet_code, session, tokens, max_files, 16)
    t_pdf = threading.Thread(target=pdf_job)
    t_csv = threading.Thread(target=csv_job)
    t_pdf.start()
    t_csv.start()
    t_pdf.join()
    t_csv.join()
    stats = {**pdf_stats, **csv_stats}
    return stats
    
if __name__ == "__main__":
    # Esegui la pulizia del CSV e schedula i task a batch
    codeList_utils.clean_CodeList()
    schedule_tasks_from_csv(csv_path="../data/EdinetcodeDlInfo_listed.csv", batch_size=10)