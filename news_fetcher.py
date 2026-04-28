"""
=============================================================
  news_fetcher.py  —  Fetch live 2026 news from NewsAPI
  Get your FREE API key at: https://newsapi.org/register
=============================================================
  Fetches headlines across 7 categories and saves to CSV.
  Run this FIRST before running classifier.py
=============================================================
"""

import os
import csv
import time
import requests
from dotenv import load_dotenv

load_dotenv()

# ── CONFIG ────────────────────────────────────────────────
# Ensure you have a .env file with NEWSAPI_KEY=your_key
API_KEY       = os.getenv("NEWSAPI_KEY", "")
OUTPUT_FILE   = "news_2026.csv"
BASE_URL      = "https://newsapi.org/v2/top-headlines"

# NewsAPI free-tier supports these 7 categories
CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology",
]

# Pages to fetch per category (100 articles per page, max 5 pages free)
PAGES_PER_CAT = 5

# ─────────────────────────────────────────────────────────
def fetch_category(category: str, page: int) -> list[dict]:
    """Fetch one page of top headlines for a category."""
    params = {
        "apiKey"   : API_KEY,
        "category" : category,
        "language" : "en",
        "pageSize" : 100,
        "page"     : page,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()

        if data.get("status") != "ok":
            print(f"  ⚠️  API error [{category} p{page}]: {data.get('message','unknown')}")
            return []

        articles = data.get("articles", [])
        rows = []
        for art in articles:
            headline = (art.get("title") or "").strip()
            # Skip removed / empty headlines
            if not headline or "[Removed]" in headline or len(headline) < 10:
                continue
            rows.append({
                "headline" : headline.lower(),
                "category" : category.upper(),
                "source"   : (art.get("source") or {}).get("name", ""),
                "published": (art.get("publishedAt") or "")[:10],  # YYYY-MM-DD
            })
        return rows

    except Exception as e:
        print(f"  ⚠️  Request failed [{category} p{page}]: {e}")
        return []


def fetch_all() -> list[dict]:
    """Fetch headlines for all categories across multiple pages."""
    all_rows = []

    for cat in CATEGORIES:
        cat_rows = []
        print(f"\n📡  Fetching category: {cat.upper()}")

        for page in range(1, PAGES_PER_CAT + 1):
            rows = fetch_category(cat, page)
            cat_rows.extend(rows)
            print(f"    Page {page}: {len(rows)} articles", end="")

            if len(rows) < 100:          # last page reached early
                print(" (end of results)")
                break
            else:
                print()

            time.sleep(0.5)              # be polite to the API

        print(f"  ✅  {cat.upper()}: {len(cat_rows)} total articles")
        all_rows.extend(cat_rows)

    return all_rows


def remove_duplicates(rows: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for r in rows:
        key = r["headline"]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def save_to_csv(rows: list[dict], path: str):
    fieldnames = ["headline", "category", "source", "published"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n💾  Saved {len(rows):,} rows → {path}")


# ─────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  NEWS FETCHER — Live 2026 Data via NewsAPI")
    print("=" * 55)

    if API_KEY == "YOUR_NEWSAPI_KEY_HERE":
        print("\n❌  Please set your API key in news_fetcher.py")
        print("    Get a free key at: https://newsapi.org/register")
        return

    rows    = fetch_all()
    rows    = remove_duplicates(rows)
    save_to_csv(rows, OUTPUT_FILE)

    print("\n📊  Category breakdown:")
    from collections import Counter
    counts = Counter(r["category"] for r in rows)
    for cat, cnt in counts.most_common():
        bar = "█" * (cnt // 10)
        print(f"  {cat:<15} {bar} {cnt}")

    print("\n✅  Done! Now run:  python classifier.py")


if __name__ == "__main__":
    main()
