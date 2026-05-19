import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

JDIH_SETNEG_URL = "https://jdih.setneg.go.id"


class JDIHSetnegScraper(BaseScraper):
    source_name = "JDIH Setneg"
    source_type = "official"

    def scrape_regulations(self, db) -> dict:
        saved = 0
        found = 0
        skipped = 0
        errors = 0

        urls_to_scrape = [
            f"{JDIH_SETNEG_URL}",
        ]

        for url in urls_to_scrape:
            try:
                resp = httpx.get(url, timeout=30, follow_redirects=True, headers={
                    "User-Agent": "KawalKebijakanBot/1.0 (policy tracker; contact@kawalkebijakan.id)"
                })
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")

                for selector in [".item-regulasi a", ".card-regulasi a", "table tbody tr a", ".card a", "a[href*=peraturan]", "a[href*=uu-]"]:
                    items = soup.select(selector)
                    for item in items:
                        title = item.get_text(strip=True)
                        href = item.get("href", "")
                        if not href or not title:
                            continue

                        full_url = href if href.startswith("http") else f"{JDIH_SETNEG_URL}{href}"
                        found += 1

                        if self.save_raw_document(
                            db=db,
                            source_url=full_url,
                            title=title,
                            content_text=title,
                            snippet=title[:200],
                            metadata={"source_page": url, "scraper": "jdih_setneg"},
                        ):
                            saved += 1
                        else:
                            skipped += 1
                    if items:
                        break

            except Exception as e:
                logger.error(f"JDIH Setneg scrape error: {e}")
                errors += 1

        self.create_scrape_log(db, items_found=found, items_saved=saved, items_skipped=skipped)
        return {"found": found, "saved": saved, "skipped": skipped, "errors": errors}