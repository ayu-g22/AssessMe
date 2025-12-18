import os
import json
import re
import time
from firecrawl import Firecrawl

# ---------------- CONFIG ----------------
BASE_URL = "https://www.shl.com"
CATALOG_BASE = "https://www.shl.com/solutions/products/product-catalog/"
OUTPUT_FILE = "assessments.json"

PAGE_SIZE = 12
MAX_PAGES = 50          # safe upper bound
SLEEP_SECONDS = 0.3
# ---------------- INIT ----------------
firecrawl = Firecrawl(api_key="fc-0bb61fde1cc04757990a828197d94ad6")

# ---------------- HELPERS ----------------
def extract_assessment_urls(markdown: str):
    """
    Extract assessment URLs like:
    /products/product-catalog/view/account-manager-solution/
    """
    pattern = r"/products/product-catalog/view/[a-zA-Z0-9\-]+/"
    return set(re.findall(pattern, markdown))


# ---------------- MAIN ----------------
def scrape_catalog():
    print("Scraping SHL catalog using start-based pagination")

    assessment_urls = set()

    for page in range(1, MAX_PAGES + 1):
        start = PAGE_SIZE * (page - 1) 
        url = f"{CATALOG_BASE}?start={start}&type=1"

        print(f"Scraping page {page} → start={start}")

        try:
            result = firecrawl.scrape(
                url,
                formats=["markdown"]
            )
        except Exception as e:
            print("Failed to scrape catalog page:", e)
            break

        markdown = result.markdown or ""
        urls = extract_assessment_urls(markdown)

        if not urls:
            print("No assessments found — stopping pagination.")
            break

        before = len(assessment_urls)
        for u in urls:
            assessment_urls.add(BASE_URL + u)

        added = len(assessment_urls) - before
        print(f"➕ Added {added} new assessments")

        if added == 0:
            print("No new assessments added — stopping.")
            break

        time.sleep(SLEEP_SECONDS)

    print(f"\nTotal unique assessment URLs found: {len(assessment_urls)}")

    # 2. Scrape each assessment page
    assessments = []

    for i, url in enumerate(sorted(assessment_urls), start=1):
        print(f"[{i}/{len(assessment_urls)}] Scraping assessment")

        try:
            page = firecrawl.scrape(
                url,
                formats=["markdown"]
            )

            assessments.append({
                "name": url.split("/")[-2].replace("-", " ").title(),
                "url": url,
                "content": page.markdown or ""
            })

            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            print("Failed:", e)

    print(f"\nTotal scraped assessments: {len(assessments)}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUTPUT_FILE}")


# ---------------- RUN ----------------
if __name__ == "__main__":
    scrape_catalog()
