import httpx
import logging
from bs4 import BeautifulSoup
from datetime import datetime
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

JDIH_BPK_URL = "https://peraturan.bpk.go.id"


class JDIHBPKScraper(BaseScraper):
    source_name = "JDIH BPK"
    source_type = "official"

    def scrape_regulations(self, db) -> dict:
        saved = 0
        found = 0
        skipped = 0
        errors = 0

        api_urls = [
            f"{JDIH_BPK_URL}/api/peraturan/terbaru",
        ]

        for url in api_urls:
            try:
                resp = httpx.get(url, timeout=30, follow_redirects=True, headers={
                    "User-Agent": "KawalKebijakanBot/1.0 (policy tracker; contact@kawalkebijakan.id)",
                    "Accept": "application/json",
                })
                resp.raise_for_status()
                data = resp.json()

                items = data if isinstance(data, list) else data.get("data", data.get("results", []))
                if not isinstance(items, list):
                    items = []

                for item in items:
                    title = item.get("judul_peraturan", item.get("title", item.get("nama", "")))
                    url_doc = item.get("url_peraturan", item.get("url", item.get("link", "")))
                    if not title or not url_doc:
                        continue

                    found += 1
                    snippet = item.get("keterangan", item.get("deskripsi", item.get("abstrak", ""))) or ""

                    if self.save_raw_document(
                        db=db,
                        source_url=url_doc,
                        title=title[:500],
                        content_text=snippet[:5000],
                        published_date=None,
                        snippet=snippet[:200],
                        metadata={
                            "source": "jdih_bpk",
                            "jenis": item.get("jenis_peraturan", ""),
                            "nomor": item.get("no_peraturan", ""),
                            "tahun": item.get("tahun", ""),
                        },
                    ):
                        saved += 1
                    else:
                        skipped += 1

            except Exception as e:
                logger.error(f"JDIH BPK scrape error: {e}")
                errors += 1

        self.create_scrape_log(db, items_found=found, items_saved=saved, items_skipped=skipped)
        return {"found": found, "saved": saved, "skipped": skipped, "errors": errors}