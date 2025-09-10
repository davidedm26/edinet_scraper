"""Shared metadata generation utilities for downloaded EDINET documents."""
import re

_PERIOD_PATTERN = re.compile(r"(\d{4}\.\d{2}\.\d{2})-(\d{4}\.\d{2}\.\d{2})")

def _extract_period(text):
    if not text:
        return None, None
    m = _PERIOD_PATTERN.search(text)
    if m:
        return m.group(1), m.group(2)
    return None, None

def generate_metadata(doc, relative_path, file_type):
    """Generate a normalized metadata dictionary for a downloaded file."""
    try:
        metadata = {
            "file_path": relative_path,
            "file_type": file_type.lower(),
            "document_name": doc.get("SHORUI_KANRI_NO", "unknown"),
            "document_type_code": doc.get("SYORUI_SB_CD_ID", "unknown"),
            "document_type_name": doc.get("SHORUI_NAME", "unknown"),
            "document_category": doc.get("YOUSIKI_NAME", "unknown"),
            "publication_date": doc.get("TEISHUTSU_NICHIJI", "unknown"),
            "company_name": doc.get("TEISYUTUSYA_NAME", "unknown"),
            "target_company": doc.get("IGAITEISYUTUSYANAME", "unknown"),
            "edinet_code": doc.get("EDINET_CD", "unknown"),
        }
        period_start, period_end = _extract_period(metadata["document_type_name"])
        metadata["period_start"] = period_start
        metadata["period_end"] = period_end
        return metadata
    except Exception as exc:
        return {"error": str(exc), "file_path": relative_path, "file_type": file_type.lower()}

__all__ = ["generate_metadata"]
