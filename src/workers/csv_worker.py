import os
import time
import re
import base64
from utils.paths import PROJECT_ROOT, DATA_DIR
from utils.metadata import generate_metadata

def download_csv_worker(doc, edinet_code, session, tokens, max_retries=3):
    """
    Worker function for downloading a single CSV document.
    Returns: (filename, document_type, company_name) tuple
    """
    kanri_no_encrypt = doc.get("SYORUI_KANRI_NO_ENCRYPT") 
    if not kanri_no_encrypt: #Crypted Document Number
        return False, "No CSV for this document"

    document_type = doc.get("SYORUI_SB_CD_ID", "unknown") # Document Type Code
    
    #save_dir = os.path.join(project_root, "data", edinet_code, "csv", document_type)
    
    save_dir = os.path.join(DATA_DIR, edinet_code, "csv", document_type)
    relative_path = os.path.relpath(save_dir, PROJECT_ROOT).replace("\\", "/")
    #print(f"CSV save_dir: {save_dir}")
    
    hsh_list = [tokens.get("gx_hash_name"), tokens.get("gx_hash_desc")]
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
            data= response_csv.json()
            dl_script = data.get("gxProps", [{}])[0].get("DLSCRIPT", {}).get("Caption", "")
            match = re.search(r'data:;base64,([A-Za-z0-9+/=]+)', dl_script)
            if not match:
                return False, "not_found"
            
            base64_data = match.group(1)
            file_data = base64.b64decode(base64_data)
            document_name = doc.get("SHORUI_KANRI_NO", "unknown") #Document Name
            filename = os.path.join(save_dir, f"{document_name}.zip")
            try:
                # Create directory lazily only when writing the file
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir, exist_ok=True)
                with open(filename, "wb") as f:
                    f.write(file_data)
                    
                metadata = generate_metadata(doc, relative_path, "csv")
                return True, (None, metadata)
            
            except Exception as file_exc:
                return False, (f"File write error: {str(file_exc)}", None)

        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
            else:
                return False, (f"Attempt {attempt}: {str(e)}",None)
