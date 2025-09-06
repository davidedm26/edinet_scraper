def search_files_by_company(edinet_code, session=None):
    """
    Esegue la ricerca dei file per una specifica azienda (edinet_code).
    Restituisce la lista dei risultati trovati e i token.
    """
    import json

    # Se la sessione non è passata, la crea
    if session is None:
        session, tokens = get_session_tokens()
    else:
        _, tokens = get_session_tokens()

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"

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

    # Richiesta principale POST
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

    response = session.post(url, headers=headers, json=payload)
    data = response.json()
    total_results = int(data.get("gxValues", [{}])[0].get("AV84W_TotalCount", 0))
    results_per_page = 100
    total_pages = (total_results + results_per_page - 1) // results_per_page

    all_results = []
    for page in range(1, total_pages + 1):
        if page == 1:
            prev_results_json = "[]"
        else:
            prev_results_json = json.dumps(all_results)
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
        response_page = session.post(url, headers=headers, json=payload_pagination)
        data_page = response_page.json()
        results_json = data_page.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
        results = json.loads(results_json)
        all_results.extend(results)
    return all_results, tokens

import os
from tqdm import tqdm
import time

def get_files(results, edinet_code, session, tokens, max_files=300):
    import os
    import time
    from tqdm import tqdm

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    save_dir = os.path.join(".", "data", edinet_code, "pdf")
    os.makedirs(save_dir, exist_ok=True)

    hsh_list = [
        tokens.get("gx_hash_name"),
        tokens.get("gx_hash_desc")
    ]

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

    pdf_found = 0
    pdf_downloaded = 0
    errors = 0
    total = min(len(results), max_files)

    start_time = time.time()

    with tqdm(total=total, desc="Download PDF", unit="file") as pbar:
        for idx, doc in enumerate(results):
            if idx >= max_files:
                break
            kanri_no_encrypt = doc.get("SYORUI_KANRI_NO_ENCRYPT")
            tipo_documento = doc.get("SYORUI_SB_CD_ID", "unknown")
            # Usa solo il codice tipo documento come sottocartella
            save_dir = os.path.join(".", "data", edinet_code, "pdf", tipo_documento)
            os.makedirs(save_dir, exist_ok=True)

            if not kanri_no_encrypt:
                errors += 1
                pbar.set_postfix({"Scaricati": pdf_downloaded, "Errori": errors})
                pbar.update(1)
                continue

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

            response_pdf = session.post(url, headers=headers, json=payload_pdf)
            if response_pdf.status_code == 200:
                try:
                    data_pdf = response_pdf.json()
                    pdf_url = data_pdf.get("gxProps", [{}])[0].get("PDFDISP", {}).get("Target")
                    if not pdf_url:
                        errors += 1
                        pbar.set_postfix({"Scaricati": pdf_downloaded, "Errori": errors})
                        pbar.update(1)
                        continue
                except Exception:
                    errors += 1
                    pbar.set_postfix({"Scaricati": pdf_downloaded, "Errori": errors})
                    pbar.update(1)
                    continue

                pdf_response = session.get(pdf_url)
                pdf_url_real = extract_pdf_url_from_html(pdf_response.text)
                if pdf_url_real:
                    pdf_found += 1 
                    pdf_file_response = session.get(pdf_url_real)
                    if pdf_file_response.status_code == 200 and pdf_file_response.content: 
                        # Usa SYORUI_KANRI_NO come nome file
                        codice_file = doc.get("SHORUI_KANRI_NO", f"{idx+1:05d}")
                        filename = os.path.join(save_dir, f"{codice_file}.pdf")
                        with open(filename, "wb") as f:
                            f.write(pdf_file_response.content)
                        pdf_downloaded += 1
                    else:
                        errors += 1
                else:
                    errors += 1
            else:
                errors += 1

            pbar.set_postfix({"Scaricati": pdf_downloaded, "Errori": errors})
            pbar.update(1)

    elapsed = time.time() - start_time
    print("\n--- STATISTICHE FINALI ---")
    print(f"PDF trovati: {pdf_found}")
    print(f"PDF scaricati: {pdf_downloaded}")
    print(f"Errori: {errors}")
    print(f"Tempo totale: {elapsed:.2f} secondi")

def get_session_tokens():
    """
    Effettua la prima GET e restituisce:
    - sessione requests con i cookie
    - dizionario con tutti i token necessari (estratti da GXState)
    """
    import requests
    import json
    from bs4 import BeautifulSoup

    url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"
    session = requests.Session()
    resp = session.get(url)
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    gxstate_input = soup.find("input", {"name": "GXState"})
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

from bs4 import BeautifulSoup
import re

def extract_pdf_url_from_html(html):
    """
    Estrae l'URL diretto del PDF dall'HTML, cercando la chiamata pdfView('...').
    Restituisce l'URL come stringa o None se non trovato.
    """
    match = re.search(r"pdfView\('([^']+\.pdf[^\']*)'\)", html)
    if match:
        return match.group(1)
    return None

# Esempio di utilizzo:
if __name__ == "__main__":
    edinet_code = "7203"
    session, _ = get_session_tokens()
    risultati, tokens = search_files_by_company(edinet_code, session=session)
    print(f"Totale risultati trovati per azienda {edinet_code}: {len(risultati)}")
    get_files(risultati, edinet_code, session, tokens)