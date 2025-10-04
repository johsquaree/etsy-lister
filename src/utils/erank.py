import csv
from typing import Dict, List


def load_erank_keywords(csv_path: str, min_volume: int = 0, limit: int = 200) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for r in reader:
                keyword = r.get("Keyword") or r.get("keyword") or r.get("Term") or r.get("Query")
                if not keyword:
                    continue
                vol_str = r.get("Search Volume") or r.get("search_volume") or r.get("Volume") or "0"
                try:
                    vol = int(str(vol_str).replace(",", "").strip())
                except Exception:
                    vol = 0
                if vol < min_volume:
                    continue
                rows.append({
                    "keyword": keyword.strip(),
                    "volume": str(vol),
                    "competition": str(r.get("Competition") or r.get("competition") or ""),
                })
        rows.sort(key=lambda x: (-int(x["volume"]), x["keyword"]))
        return rows[:limit]
    except FileNotFoundError:
        return []


def top_keywords_only(csv_path: str, min_volume: int = 0, limit: int = 50) -> List[str]:
    return [r["keyword"] for r in load_erank_keywords(csv_path, min_volume=min_volume, limit=limit)]

