import pandas as pd
import os
import requests
import base64
from utils.paths import DATA_DIR

def clean_CodeList(input_path=None, output_path=None):
    """
    Removes the first row, selects columns by position (edit indices if needed),
    and filters only rows with type Listed Company.
    Handles input/output paths robustly relative to the project root.
    """
    if input_path is None:
        input_path = os.path.join(DATA_DIR, 'EdinetcodeDlInfo.csv')
    if output_path is None:
        output_path = os.path.join(DATA_DIR, 'Edinet_codeList.csv')
    df = pd.read_csv(input_path, skiprows=1, encoding="cp932")
    # Select columns by position: e.g. 0, 1, 2
    df = df.iloc[:, [0, 2, 7]]
    # Filter only rows where the third column (index 2) is "Listed company"
    df = df[df.iloc[:, 1] == "Listed company"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Transformed file saved at: {output_path}")
    os.remove(input_path)

def get_codeList():
    """
    Retrieves hashes and tokens via an initial GET request.
    All paths are handled relative to the project root.
    """
    import json
    url = "https://disclosure2.edinet-fsa.go.jp/weee0020.aspx"
    session = requests.Session()
    resp = session.get(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    gxstate_input = soup.find("input", {"name": "GXState"})
    if gxstate_input is None:
        print("[get_codeList] ERROR: GXState not found in initial page")
        raise Exception("GXState not found in initial page")
    gxstate_raw = gxstate_input["value"]
    gxstate = json.loads(gxstate_raw)
    gx_auth_token = gxstate.get("GX_AUTH_WEEE0020")
    ajax_token = gxstate.get("AJAX_SECURITY_TOKEN")
    gx_hash_name = gxstate.get("gxhash_vPGMNAME")
    gx_hash_desc = gxstate.get("gxhash_vPGMDESC")
    payload = {
        "MPage": False,
        "cmpCtx": "",
        "parms": [
            "WEEE0020",
            "EDINET TAXONOMY&CODE LIST"
        ],
        "hsh": [
            {"hsh": gx_hash_name, "row": ""},
            {"hsh": gx_hash_desc, "row": ""}
        ],
        "objClass": "weee0020",
        "pkgName": "GeneXus.Programs",
        "events": ["'DODOWNLOADEDINET'"],
        "grids": {}
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": url,
        "Origin": "https://disclosure2.edinet-fsa.go.jp",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9,ja;q=0.8",
        "X-Requested-With": "XMLHttpRequest",
        "gxajaxrequest": "1",
        "ajax_security_token": ajax_token,
        "x-gxauth-token": gx_auth_token,
    }
    print("[get_codeList] Sending POST request to download ZIP...")
    response = session.post(url, headers=headers, json=payload)
    print(f"[get_codeList] POST completed, status: {response.status_code}")
    data = response.json()
    dl_script = data.get("gxProps", [{}])[0].get("TXTSCRIPT", {}).get("Caption", "")
    import re
    match = re.search(r'data:;base64,([A-Za-z0-9+/=]+)', dl_script)
    if not match:
        print("[get_codeList] ERROR: Base64 ZIP not found in response!")
        raise Exception("Base64 ZIP not found in response")
    base64_data = match.group(1)
    file_data = base64.b64decode(base64_data)
    import zipfile, io
    print("[get_codeList] Extracting ZIP...")
    with zipfile.ZipFile(io.BytesIO(file_data)) as z:
        for name in z.namelist():
            print(f"[get_codeList] File found in ZIP: {name}")
            if name.endswith(".csv"):
                os.makedirs(DATA_DIR, exist_ok=True)
                out_path = os.path.join(DATA_DIR, name)
                with open(out_path, "wb") as f:
                    f.write(z.read(name))
                print(f"[get_codeList] CSV saved at: {out_path}")
                return out_path
    print("[get_codeList] ERROR: No CSV file found in ZIP!")
    raise Exception("No CSV file found in ZIP")

def build_codeList_file():
    get_codeList()
    clean_CodeList() 

if __name__ == "__main__":
    get_codeList()
    clean_CodeList() 
    #updateCodeList()
