import requests
import json
from bs4 import BeautifulSoup

url = "https://disclosure2.edinet-fsa.go.jp/WEEE0040.aspx"

session = requests.Session()
resp = session.get(url)
cookies = (session.cookies.get_dict())
print(cookies)

response = requests.get(url)
print(response)

soup = BeautifulSoup(response.text, "html.parser")

# trova l'input GXState
gxstate_input = soup.find("input", {"name": "GXState"})
if gxstate_input:
    gxstate_raw = gxstate_input["value"]
    
    # parse come JSON
    gxstate = json.loads(gxstate_raw)
    
    # Estrai GX_AUTH_TOKEN
    gx_auth_token = gxstate.get("GX_AUTH_WEEE0040")
    print("GX_AUTH_WEEE0040 =", gx_auth_token)
    # Estrai AJAX_SECURITY_TOKEN
    ajax_token = gxstate.get("AJAX_SECURITY_TOKEN")
    # Estrai GX_AJAX_KEY
    gx_key = gxstate.get("GX_AJAX_KEY")
    # Estrai GX_AJAX_IV
    gx_iv = gxstate.get("GX_AJAX_IV")
    
    # Estrai gxhash_vPGMNAME
    gx_hash_name = gxstate.get("gxhash_vPGMNAME")
    
    # Estrai gxhash_vPGMDESC
    gx_hash_desc = gxstate.get("gxhash_vPGMDESC")
    
    # Estrai gxhash_vW_PAGEMAX
    gxhash_vW_PAGEMAX = gxstate.get("gxhash_vW_PAGEMAX")
    # Estrai gxhash_vW_LANGUAGE
    gxhash_vW_LANGUAGE = gxstate.get("gxhash_vW_LANGUAGE")
    
    # Estrai GX_AUTH_W0018WEEE0040_CONDITION
    gx_auth_condition_token = gxstate.get("GX_AUTH_W0018WEEE0040_CONDITION")
    print("GX_AUTH_W0018WEEE0040_CONDITION =", gx_auth_condition_token)

    # Estrai W0018gxhash_vPGMNAME
    W0018gxhash_vPGMNAME = gxstate.get("W0018gxhash_vPGMNAME")
    print("W0018gxhash_vPGMNAME:", W0018gxhash_vPGMNAME)
    # Estrai W0018gxhash_vPGMDESC
    W0018gxhash_vPGMDESC = gxstate.get("W0018gxhash_vPGMDESC")
    print("W0018gxhash_vPGMDESC:", W0018gxhash_vPGMDESC)

    print("gxhash_vW_PAGEMAX:", gxhash_vW_PAGEMAX)
    print("gxhash_vW_LANGUAGE:", gxhash_vW_LANGUAGE)  
    print("AJAX_SECURITY_TOKEN:", ajax_token)
    print("GX_AJAX_KEY:", gx_key)
    print("GX_AJAX_IV:", gx_iv)
    print("gxhash_vPGMNAME:",gx_hash_name)
    print("gxhash_vPGMDESC:",gx_hash_desc)

headers_cond_req = {
    "ajax_security_token": ajax_token,
    "x-gxauth-token": gx_auth_condition_token ,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Origin": "https://disclosure2.edinet-fsa.go.jp",
    "Referer": "https://disclosure2.edinet-fsa.go.jp/WEEE0040",
    "X-Requested-With" : "XMLHttpRequest",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "gxajaxrequest": "1"
}

headers3 = {
    "ajax_security_token": ajax_token,
    "x-gxauth-token": gx_auth_token,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Origin": "https://disclosure2.edinet-fsa.go.jp",
    "Referer": "https://disclosure2.edinet-fsa.go.jp/WEEE0040",
    "X-Requested-With" : "XMLHttpRequest",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6",
    "gxajaxrequest": "1"
}


payload1 = {
    "MPage":False,
    "cmpCtx":"W0018",
    "parms":["WEEE0040_Condition", "WEEE0040_Condition", False, True, True, True, True],
    "events":["'DOBTN_SERACH'"],
    "grids":{},
    "hsh":[
        {"hsh": W0018gxhash_vPGMNAME , "row": ""},
        {"hsh": W0018gxhash_vPGMDESC , "row": ""}
    ],
    "objClass":"weee0040_condition",
    "pkgName":"GeneXus.Programs"}


payload2 = {
    "MPage":False,
    "cmpCtx":"W0018",
    "parms":["",[],{"SEARCH_KEY_WORD":"","CONTAIN_FUND":False,"SYORUI_SYUBETU":"","KESSAN_NEN":"","KESSAN_TUKI":"","TEISYUTU_FROM":"","TEISYUTU_TO":"","FLS":False,"LPR":False,"RPR":False,"OTH":False,"TEISYUTU_KIKAN":0},"WEEE0040_Condition","WEEE0040_Condition","7205",{"s":"7","v":[["1","On the day"],["2","In last three days"],["3","In last week"],["4","In last month"],["5","In the past six months"],["6","In the past year"],["7","In the entire period"]]},7,False,True,True,True,True],
    "events": ["T(O(14,'WEEE0030_EVENTS'),72).SETPARAMETER"],
    "grids":{},
    "hsh":[
        {"hsh": W0018gxhash_vPGMNAME , "row": ""},
        {"hsh": W0018gxhash_vPGMDESC , "row": ""}
    ],
    "objClass":"weee0040_condition",
    "pkgName":"GeneXus.Programs"}

payload3 = {
    "MPage":False,
    "cmpCtx":"",
    "parms":[[],{"SEARCH_KEY_WORD":"7203","CONTAIN_FUND":False,"SYORUI_SYUBETU":"120,130,140,150,160,170,350,360,010,020,030,040,050,060,070,080,090,100,110,135,136,200,210,220,230,235,236,240,250,260,270,280,290,300,310,320,330,340,370,380,180,190,","KESSAN_NEN":"","KESSAN_TUKI":"","TEISYUTU_FROM":"19000101","TEISYUTU_TO":"20250904","FLS":True,"LPR":True,"RPR":True,"OTH":True,"TEISYUTU_KIKAN":7},"WEEE0040","Simple document search",2,1,100,{"SaitoKubun":"","SennimotoId":"WEEE0040"},"1",False,"[]",0],
    "events":["T(O(14,'WEEE0030_EVENTS'),72).BACKSETPARAMETER"],
    "grids":{},
    "hsh":[
        {"hsh": gx_hash_name, "row": ""},
        {"hsh": gx_hash_desc, "row": ""},
        {"hsh": gxhash_vW_PAGEMAX, "row": ""},
        {"hsh": gxhash_vW_LANGUAGE, "row": ""}
    ],
    "objClass":"weee0040",
    "pkgName":"GeneXus.Programs"}

# Prima richiesta POST preventiva
response1 = session.post(url, headers=headers_cond_req, json=payload1)
print("Response 1 status:", response1.status_code)
#print("Response 1 text:", response1.text)

# Sec richiesta POST preventiva
response2 = session.post(url, headers=headers_cond_req, json=payload2)
print("Response 2 status:", response2.status_code)
#print("Response 2 text:", response2.text)

# Richiesta principale POST
response3 = session.post(url, headers=headers3, json=payload3)
print("Response 3 status:", response3.status_code)
#print("Response 3 text:", response3.text)
"""
with open("response3.html", "w", encoding="utf-8") as f:
    f.write(response3.text)
print("Risposta salvata in response3.html. Apri il file con il browser per visualizzarla.")

# Visualizza i risultati della ricerca dalla risposta JSON
results_list_json = "[]"  # default vuoto
try:
    data = response3.json()
    # Cerca la chiave dei risultati (può variare, ad esempio AV113W_RESULT_LIST_JSON)
    results_json = data.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
    results = json.loads(results_json)
    results_list_json = results_json  # salva la lista risultati come stringa JSON
    print(f"Numero risultati trovati: {len(results)}")
    for doc in results:
        print(f"{doc.get('TEISHUTSU_NICHIJI', '')} | {doc.get('SHORUI_NAME', '')} | {doc.get('TEISYUTUSYA_NAME', '')}")
except Exception as e:
    print("Impossibile estrarre i risultati:", e)

# token della prima e della seocnda post per ricerca GX_AUTH_W0018WEEE0040_CONDITION
# token della post principale GX_AUTH_WEEE0040

payload4 = {
    "MPage": False,
    "cmpCtx": "",
    "parms": [
        "WEEE0040",
        "Simple document search",
        {
            "SEARCH_KEY_WORD": "7203",
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
        2,
        2,
        100,
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
        results_list_json,  # <-- qui passa la lista risultati estratta
        135
    ],
    "hsh": [
        {"hsh": gx_hash_name, "row": ""},
        {"hsh": gx_hash_desc, "row": ""},
        {"hsh": gxhash_vW_PAGEMAX, "row": ""},
        {"hsh": gxhash_vW_LANGUAGE, "row": ""}
    ],
    "objClass": "weee0040",
    "pkgName": "GeneXus.Programs",
    "events": ["'DOBTN_PAGER'"],
    "grids": {}
}

# Richiesta principale POST
response4 = session.post(url, headers=headers3, json=payload4)
print("Response 4 status:", response4.status_code)
#print("Response 4 text:", response3.text)

with open("response4.html", "w", encoding="utf-8") as f:
    f.write(response4.text)
print("Risposta salvata in response4.html. Apri il file con il browser per visualizzarla.")

# Visualizza i risultati della ricerca dalla risposta JSON
try:
    data = response4.json()
    # Cerca la chiave dei risultati (può variare, ad esempio AV113W_RESULT_LIST_JSON)
    results_json = data.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
    results = json.loads(results_json)
    print(f"Numero risultati trovati: {len(results)}")
    for doc in results:
        print(f"{doc.get('TEISHUTSU_NICHIJI', '')} | {doc.get('SHORUI_NAME', '')} | {doc.get('TEISYUTUSYA_NAME', '')}")
except Exception as e:
    print("Impossibile estrarre i risultati:", e)
"""
# Estrai il numero totale di risultati e calcola il numero di pagine
try:
    data = response3.json()
    # Usa la chiave corretta per il totale
    total_results = int(data.get("gxValues", [{}])[0].get("AV84W_TotalCount", 0))
    results_per_page = 100
    total_pages = (total_results + results_per_page - 1) // results_per_page
    print(f"Totale risultati: {total_results}, pagine: {total_pages}")
except Exception as e:
    print("Impossibile estrarre il numero di pagine:", e)
    total_pages = 1

# Ciclo su tutte le pagine
all_results = []
for page in range(1, total_pages + 1):
    # Aggiorna la lista risultati per la paginazione (serve per il server)
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
                "SEARCH_KEY_WORD": "7203",
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
            page,  # <-- numero pagina
            page,  # <-- offset (spesso coincide col numero pagina)
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
            prev_results_json,  # <-- passa la lista risultati delle pagine precedenti
            total_results
        ],
        "hsh": [
            {"hsh": gx_hash_name, "row": ""},
            {"hsh": gx_hash_desc, "row": ""},
            {"hsh": gxhash_vW_PAGEMAX, "row": ""},
            {"hsh": gxhash_vW_LANGUAGE, "row": ""}
        ],
        "objClass": "weee0040",
        "pkgName": "GeneXus.Programs",
        "events": ["'DOBTN_PAGER'"],
        "grids": {}
    }
    response_page = session.post(url, headers=headers3, json=payload_pagination)
    print(f"Pagina {page}: status {response_page.status_code}")
    try:
        data_page = response_page.json()
        results_json = data_page.get("gxValues", [{}])[0].get("AV113W_RESULT_LIST_JSON", "[]")
        results = json.loads(results_json)
        print(f"Risultati pagina {page}: {len(results)}")
        for doc in results:
            print(f"{doc.get('TEISHUTSU_NICHIJI', '')} | {doc.get('SHORUI_NAME', '')} | {doc.get('TEISYUTUSYA_NAME', '')}")
        all_results.extend(results)
    except Exception as e:
        print(f"Impossibile estrarre i risultati dalla pagina {page}:", e)

print(f"Totale risultati raccolti: {len(all_results)}")