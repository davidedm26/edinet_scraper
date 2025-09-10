import os
import time
import re
from utils.paths import PROJECT_ROOT, DATA_DIR
from utils.metadata import generate_metadata

def download_pdf_worker(doc, edinet_code, session, tokens, max_retries=3):
    """
    Worker function for downloading a single PDF document.
    Skips if SYORUI_KANRI_NO_ENCRYPT is missing.
    Returns: (filename, document_type, company_name) tuple
    """
    document_type = doc.get("SYORUI_SB_CD_ID", "unknown") # Document Type Code
    
    #import pprint
    #pprint.pprint(doc)
    
    if not doc.get("SYORUI_KANRI_NO_ENCRYPT"):
        return False, "No PDF for this document"

    # Use DATA_DIR for base data path
    save_dir = os.path.join(DATA_DIR, edinet_code, "pdf", document_type)
    relative_path = os.path.relpath(save_dir, PROJECT_ROOT).replace("\\", "/")

    #print(f"PDF save_dir: {save_dir}")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    kanri_no_encrypt = doc.get("SYORUI_KANRI_NO_ENCRYPT")
    if not kanri_no_encrypt:
        return False, "Missing SYORUI_KANRI_NO_ENCRYPT"
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
            data = response_pdf.json()
            pdf_page_url = data.get("gxProps", [{}])[0].get("PDFDISP", {}).get("Target")
            if not pdf_page_url:
                raise Exception("PDF URL not found")

            pdf_file = session.get(pdf_page_url)
            if pdf_file.status_code != 200:
                raise Exception("Error downloading PDF file")
            
            def extract_pdf_url_from_html(html):
                match = re.search(r"pdfView\('([^']+\.pdf[^']*)'\)", html)
                if match:
                    return match.group(1)
                return None
            
            pdf_url = extract_pdf_url_from_html(pdf_file.text)
            if not pdf_url:
                raise Exception("Real PDF URL not found")
            pdf_file_response = session.get(pdf_url)
            
            if pdf_file_response.status_code == 200 and pdf_file_response.content:
                try:
                    document_name = doc.get("SHORUI_KANRI_NO", "unknown") # Document Name
                except Exception as e:
                    return False, ("not_found",None)
                
                
                filename = os.path.join(save_dir, f"{document_name}.pdf")
                with open(filename, "wb") as f:
                    f.write(pdf_file_response.content)
                metadata = generate_metadata(doc, relative_path, "pdf")
                return True, (None, metadata)
            else:
                raise Exception("PDF download failed")
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
            else:
                return False, (f"Attempt {attempt}: {str(e)}",None)


## Legacy generate_MetaData removed (migrated to utils.metadata.generate_metadata)

