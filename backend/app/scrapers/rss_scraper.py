import feedparser
import logging
from datetime import datetime
from typing import Optional
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    {"name": "Kompas Nasional", "url": "https://rss.kompas.com/news", "category_hint": "hukum"},
    {"name": "Kompas Ekonomi", "url": "https://rss.kompas.com/ekonomi", "category_hint": "ekonomi"},
    {"name": "DetikNews", "url": "https://rss.detik.com/index.php/detik", "category_hint": "hukum"},
    {"name": "DetikFinance", "url": "https://rss.detik.com/index.php/finance", "category_hint": "ekonomi"},
    {"name": "Tempo Nasional", "url": "https://rss.tempo.co/nasional", "category_hint": "hukum"},
    {"name": "Tempo Bisnis", "url": "https://rss.tempo.co/bisnis", "category_hint": "ekonomi"},
    {"name": "CNN Indonesia", "url": "https://rss.cnnindonesia.com/nasional", "category_hint": "hukum"},
    {"name": "CNN Ekonomi", "url": "https://rss.cnnindonesia.com/ekonomi", "category_hint": "ekonomi"},
    {"name": "Bisnis.com", "url": "https://rss.bisnis.com/news", "category_hint": "ekonomi"},
    {"name": "Bisnis Ekonomi", "url": "https://rss.bisnis.com/economy", "category_hint": "ekonomi"},
    {"name": "Republika", "url": "https://www.republika.co.id/rss", "category_hint": "hukum"},
    {"name": "Suaracom", "url": "https://rss.suara.com/suara", "category_hint": "hukum"},
    {"name": "Antara Ekonomi", "url": "https://rss.antaranews.com/ekonomi", "category_hint": "ekonomi"},
    {"name": "Antara Nasional", "url": "https://rss.antaranews.com/nasional", "category_hint": "hukum"},
    {"name": "Kontan", "url": "https://rss.kontan.co.id/news", "category_hint": "ekonomi"},
]

POLICY_KEYWORDS = [
    "kebijakan", "peraturan", "undang-undang", "uu ", "pp ", "perpres",
    "permen", "kepmen", "inpres", "regulasi", "regulasi", "pajak",
    "ump", "umk", "upah minimum", "subsidi", "bansos", "kesehatan",
    "pendidikan", "tenaga kerja", "umkm", "pangan", "transportasi",
    "perumahan", "digital", "data pribadi", "bpjs", "prakerja",
]


class RSSScraper(BaseScraper):
    source_name = "rss_media"
    source_type = "news"

    def _is_policy_relevant(self, title: str, snippet: str = "") -> bool:
        text = f"{title} {snippet}".lower()
        return any(kw in text for kw in POLICY_KEYWORDS)

    def scrape_feed(self, db, feed_url: str, site_name: str, category_hint: str = "") -> dict:
        found = 0
        saved = 0
        skipped = 0
        errors = 0

        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logger.error(f"RSS fetch error [{site_name}]: {e}")
            return {"found": 0, "saved": 0, "skipped": 0, "errors": 1, "error": str(e)}

        for entry in feed.entries:
            found += 1
            title = entry.get("title", "")
            link = entry.get("link", "")
            snippet = entry.get("summary", "")[:300]
            published = None

            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            if not link or not title:
                skipped += 1
                continue

            if not self._is_policy_relevant(title, snippet):
                skipped += 1
                continue

            if self.save_raw_document(
                db=db,
                source_url=link,
                title=title,
                content_text=snippet,
                published_date=published,
                snippet=snippet[:200],
                metadata={
                    "feed_name": site_name,
                    "feed_url": feed_url,
                    "category_hint": category_hint,
                    "relevant": True,
                },
            ):
                saved += 1
            else:
                skipped += 1

        return {"found": found, "saved": saved, "skipped": skipped, "errors": 0}

    def scrape_all(self, db) -> dict:
        results = {}
        total_found = 0
        total_saved = 0
        total_skipped = 0
        total_errors = 0

        for feed in RSS_FEEDS:
            try:
                result = self.scrape_feed(db, feed["url"], feed["name"], feed.get("category_hint", ""))
                results[feed["name"]] = result
                total_found += result["found"]
                total_saved += result["saved"]
                total_skipped += result["skipped"]
                total_errors += result["errors"]
            except Exception as e:
                results[feed["name"]] = {"found": 0, "saved": 0, "skipped": 0, "errors": 1, "error": str(e)}
                total_errors += 1

        self.create_scrape_log(
            db,
            items_found=total_found,
            items_saved=total_saved,
            items_skipped=total_skipped,
        )

        logger.info(f"RSS scrape complete: found={total_found}, saved={total_saved}, skipped={total_skipped}")
        return {
            "feeds": results,
            "total_found": total_found,
            "total_saved": total_saved,
            "total_skipped": total_skipped,
        }