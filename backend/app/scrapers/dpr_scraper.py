import httpx
import logging
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

DPR_PROLEGNAS_URL = "https://www.dpr.go.id/prolegnas"


class DPRProlegnasScraper(BaseScraper):
    source_name = "DPR Prolegnas"
    source_type = "document"

    def scrape_prolegnas(self, db) -> dict:
        saved = 0
        found = 0
        skipped = 0
        errors = 0

        try:
            resp = httpx.get(DPR_PROLEGNAS_URL, timeout=30, follow_redirects=True, headers={
                "User-Agent": "KawalKebijakanBot/1.0 (policy tracker; contact@kawalkebijakan.id)"
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            for selector in ["table tbody tr a", ".prolegnas-item a", "a[href*=prolegnas]", ".card a"]:
                items = soup.select(selector)
                for item in items:
                    title = item.get_text(strip=True)
                    href = item.get("href", "")
                    if not title or not href:
                        continue

                    full_url = href if href.startswith("http") else f"https://www.dpr.go.id{href}"
                    found += 1

                    if self.save_raw_document(
                        db=db,
                        source_url=full_url,
                        title=title[:500],
                        content_text=title,
                        snippet=title[:200],
                        metadata={"source": "dpr_prolegnas", "scraper": "dpr_prolegnas"},
                    ):
                        saved += 1
                    else:
                        skipped += 1
                if items:
                    break

        except Exception as e:
            logger.error(f"DPR Prolegnas scrape error: {e}")
            errors += 1

        self.create_scrape_log(db, items_found=found, items_saved=saved, items_skipped=skipped)
        return {"found": found, "saved": saved, "skipped": skipped, "errors": errors}