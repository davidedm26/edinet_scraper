import os
import sys
import json

# Ensure project src root is on sys.path when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.db_utils import connect_mongo


NUMERIC_KEYS = [
    "pdf_downloaded", "pdf_not_found", "pdf_errors", "pdf_time",
    "csv_downloaded", "csv_not_found", "csv_errors", "csv_time",
]


def get_scraping_stats():
    """Return a list of per-company stats dicts (only for companies with status='done')."""
    db = connect_mongo()
    docs = db["companies"].find({"status": "done"}, {"_id": 0, "stats": 1})
    return [d.get("stats", {}) for d in docs]


def aggregate_totals(include_averages: bool = True):
    """Aggregate totals (and optionally averages) across all companies' stats."""
    stats_list = get_scraping_stats()
    totals = {k: 0 for k in NUMERIC_KEYS}
    count = 0
    for s in stats_list:
        if not isinstance(s, dict):
            continue
        if any(k in s for k in NUMERIC_KEYS):
            count += 1
        for k in NUMERIC_KEYS:
            v = s.get(k)
            if isinstance(v, (int, float)):
                totals[k] += v
                

    # Time conversions
    pdf_t = totals.get("pdf_time", 0.0)
    csv_t = totals.get("csv_time", 0.0)
    tot_t = pdf_t + csv_t
    
    
    # Helper for human readable time
    def format_time(seconds):
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            min_part, sec_part = divmod(int(seconds), 60)
            return f"{min_part} minutes and {sec_part}s"
        else:
            hrs_part, rem = divmod(int(seconds), 3600)
            min_part, sec_part = divmod(rem, 60)
            if min_part > 0:
                return f"{hrs_part} hours and {min_part} min"
            else:
                return f"{hrs_part} hours"

    summary = {
        "companies_with_stats": count,
        "totals": totals,
        "time": {
            "pdf_time": format_time(pdf_t),
            "csv_time": format_time(csv_t),
            "total_time": format_time(tot_t),
        },
    }
    if include_averages:
        advanced_stats = {}
        advanced_stats["pdf_rate"] = f"{(totals['pdf_downloaded'] / pdf_t):.2f} files/s" if pdf_t else "0 files/s"

        advanced_stats["csv_rate"] = f"{(totals['csv_downloaded'] / csv_t):.2f} files/s" if csv_t else "0 files/s"
        summary["advanced_stats"] = advanced_stats

    # Remove pdf_t and csv_t from totals as they are not counts
    totals.pop("pdf_time", None)
    totals.pop("csv_time", None)

    
    return summary


if __name__ == "__main__":
    print(json.dumps(aggregate_totals(), indent=2))

