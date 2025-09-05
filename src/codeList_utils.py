import pandas as pd
import os
import requests
import base64


def clean_CodeList(input_path=None, output_path=None):
    """
    Rimuove la prima riga, prende solo le colonne per posizione (modifica gli indici se necessario)
    e filtra solo le righe con tipo Listed Company.
    Gestisce i path di input/output in modo robusto rispetto alla directory di esecuzione.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    if input_path is None:
        input_path = os.path.join(base_dir, 'EdinetcodeDlInfo.csv')
    if output_path is None:
        output_path = os.path.join(base_dir, 'Edinet_codeList.csv')
    df = pd.read_csv(input_path, skiprows=1, encoding="cp932")
    print(df.iloc[:, 2].unique())
    #print("Colonne disponibili:", df.columns.tolist())
    # Seleziona le colonne per posizione: ad esempio 0, 1, 2
    df = df.iloc[:, [0, 2, 7]]
    # Filtra solo le righe dove la terza colonna (indice 2) è "Listed company"
    df = df[df.iloc[:, 1] == "Listed company"]
    #print(df.head(10))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"File trasformato salvato in: {output_path}")


def get_codeList():
    """
    Gli hash e i token vengono recuperati tramite una GET iniziale.
    """
    import json
    url = "https://disclosure2.edinet-fsa.go.jp/weee0020.aspx"
    session = requests.Session()
    # GET iniziale per recuperare i token
    resp = session.get(url)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")
    gxstate_input = soup.find("input", {"name": "GXState"})
    if gxstate_input is None:
        raise Exception("GXState non trovato nella pagina iniziale")
    gxstate_raw = gxstate_input["value"]
    gxstate = json.loads(gxstate_raw)
    gx_auth_token = gxstate.get("GX_AUTH_WEEE0020")
    ajax_token = gxstate.get("AJAX_SECURITY_TOKEN")
    gx_hash_name = gxstate.get("gxhash_vPGMNAME")
    gx_hash_desc = gxstate.get("gxhash_vPGMDESC")
    # Costruisci il payload dinamicamente
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
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
        "X-Requested-With": "XMLHttpRequest",
        "gxajaxrequest": "1",
        "ajax_security_token": ajax_token,
        "x-gxauth-token": gx_auth_token,
    }
    # Esegui la richiesta POST
    response = session.post(url, headers=headers, json=payload)
    data = response.json()
    # Salva la risposta JSON per analisi
    import json
    with open("data/edinet_codeList_response.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))
    dl_script = data.get("gxProps", [{}])[0].get("TXTSCRIPT", {}).get("Caption", "")
    import re
    match = re.search(r'data:;base64,([A-Za-z0-9+/=]+)', dl_script)
    if not match:
        raise Exception("Base64 ZIP non trovato nella risposta")
    base64_data = match.group(1)
    file_data = base64.b64decode(base64_data)
    import zipfile, io, os
    with zipfile.ZipFile(io.BytesIO(file_data)) as z:
        for name in z.namelist():
            if name.endswith(".csv"):
                os.makedirs("data", exist_ok=True)
                out_path = os.path.join("data", name)
                with open(out_path, "wb") as f:
                    f.write(z.read(name))
                print(f"Salvato: {out_path}")
                return out_path
    raise Exception("Nessun file CSV trovato nello ZIP")

if __name__ == "__main__":
    get_codeList()
    clean_CodeList()