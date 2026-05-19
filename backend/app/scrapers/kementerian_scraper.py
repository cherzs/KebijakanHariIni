import httpx
import logging
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

KEMENTERIAN_SOURCES = [
    {
        "name": "Kemenkeu",
        "base_url": "https://www.kemenkeu.go.id",
        "paths": ["/informasi-publik", "/publikasi"],
        "selectors": ["article a", ".news-item a", ".content a[href*=peraturan]", "a[href*=pmk]"],
    },
    {
        "name": "Kemnaker",
        "base_url": "https://www.kemnaker.go.id",
        "paths": ["/publikasi", "/berita"],
        "selectors": ["article a", ".news-item a", "a[href*=kepmen]", "a[href*=permen]"],
    },
    {
        "name": "Kemendikbud",
        "base_url": "https://www.kemdikbud.go.id",
        "paths": ["/publikasi", "/berita"],
        "selectors": ["article a", ".news-list a", "a[href*=permendikbud]"],
    },
    {
        "name": "Kemenkes",
        "base_url": "https://www.kemkes.go.id",
        "paths": ["/id/home", "/informasi"],
        "selectors": ["article a", ".news-item a", "a[href*=permenkes]", "a[href*=kepmenkes]"],
    },
    {
        "name": "Kominfo",
        "base_url": "https://www.kominfo.go.id",
        "paths": ["/content/all", "/regulasi"],
        "selectors": ["article a", ".news-item a", "a[href*=perkominfo]", "a[href*=regulasi]"],
    },
]


class KementerianScraper(BaseScraper):
    source_name = "kementerian"
    source_type = "official"

    def scrape_ministry(self, db, source: dict) -> dict:
        saved = 0
        found = 0
        skipped = 0
        errors = 0

        for path in source.get("paths", []):
            url = f"{source['base_url']}{path}"
            try:
                resp = httpx.get(url, timeout=30, follow_redirects=True, headers={
                    "User-Agent": "KawalKebijakanBot/1.0 (policy tracker; contact@kawalkebijakan.id)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")

                for selector in source.get("selectors", []):
                    items = soup.select(selector)
                    for item in items:
                        title = item.get_text(strip=True)
                        href = item.get("href", "")
                        if not title or not href:
                            continue

                        full_url = href if href.startswith("http") else f"{source['base_url']}{href}"
                        found += 1

                        if self.save_raw_document(
                            db=db,
                            source_url=full_url,
                            title=title[:500],
                            content_text=title,
                            snippet=title[:200],
                            metadata={
                                "source": source["name"],
                                "ministry_url": url,
                                "scraper": "kementerian",
                            },
                        ):
                            saved += 1
                        else:
                            skipped += 1
                    if items:
                        break

            except Exception as e:
                logger.error(f"Kementerian scrape error [{source['name']}]: {e}")
                errors += 1

        return {"found": found, "saved": saved, "skipped": skipped, "errors": errors}

    def scrape_all(self, db) -> dict:
        results = {}
        total_found = 0
        total_saved = 0
        total_skipped = 0
        total_errors = 0

        for source in KEMENTERIAN_SOURCES:
            result = self.scrape_ministry(db, source)
            results[source["name"]] = result
            total_found += result["found"]
            total_saved += result["saved"]
            total_skipped += result["skipped"]
            total_errors += result["errors"]

        self.create_scrape_log(
            db,
            items_found=total_found,
            items_saved=total_saved,
            items_skipped=total_skipped,
        )

        return {
            "ministries": results,
            "total_found": total_found,
            "total_saved": total_saved,
            "total_skipped": total_skipped,
        }