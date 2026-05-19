import httpx
from bs4 import BeautifulSoup
from datetime import datetime
from .base import BaseScraper

JDIH_SETNEG_URL = "https://jdih.setneg.go.id"


class JDIHSetnegScraper(BaseScraper):
    source_name = "JDIH Setneg"
    source_type = "official"

    def scrape_new_regulations(self):
        saved = 0
        try:
            resp = httpx.get(f"{JDIH_SETNEG_URL}/Regulasi TERBARU", timeout=30, follow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select(".item-regulasi, .card-regulasi, table tbody tr")

            for item in items:
                link_tag = item.select_one("a[href]")
                if not link_tag:
                    continue

                title = link_tag.get_text(strip=True)
                url = link_tag.get("href", "")
                if url and not url.startswith("http"):
                    url = f"{JDIH_SETNEG_URL}{url}"

                snippet = item.get_text(strip=True)[:200]

                if url and title and self.save_raw_document(
                    source_url=url,
                    title=title,
                    content_text=snippet,
                ):
                    saved += 1

        except Exception as e:
            print(f"Error scraping JDIH Setneg: {e}")

        return saved