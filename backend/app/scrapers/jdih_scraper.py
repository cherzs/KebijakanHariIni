import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from .base_scraper import BaseScraper

JDIH_SETNEG_URL = "https://jdih.setneg.go.id"


class JDIHSetnegScraper(BaseScraper):
    source_name = "JDIH Setneg"
    source_type = "official"

    def scrape_regulations(self, db) -> int:
        saved = 0
        urls = [
            f"{JDIH_SETNEG_URL}/Regulasi%20TERBARU",
            f"{JDIH_SETNEG_URL}/Peraturan",
        ]

        for url in urls:
            try:
                resp = httpx.get(url, timeout=30, follow_redirects=True)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "lxml")
                selectors = [".item-regulasi", ".card-regulasi", "table tbody tr a", ".card a"]
                for selector in selectors:
                    items = soup.select(selector)
                    for item in items:
                        link_tag = item if item.name == "a" else item.select_one("a[href]")
                        if not link_tag:
                            continue
                        title = link_tag.get_text(strip=True)
                        href = link_tag.get("href", "")
                        full_url = href if href.startswith("http") else f"{JDIH_SETNEG_URL}{href}"
                        snippet = item.get_text(strip=True)[:200]

                        if full_url and title and self.save_raw_document(
                            db=db,
                            source_url=full_url,
                            title=title,
                            content_text=snippet,
                            snippet=snippet,
                            metadata={"source_page": url},
                        ):
                            saved += 1
                break
            except Exception:
                continue

        return saved