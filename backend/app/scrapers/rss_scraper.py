import feedparser
from datetime import datetime
from .base_scraper import BaseScraper

RSS_FEEDS = [
    {"name": "Kompas", "url": "https://rss.kompas.com/news", "category_hint": "hukum"},
    {"name": "DetikNews", "url": "https://rss.detik.com/index.php/detik", "category_hint": "hukum"},
    {"name": "Tempo Nasional", "url": "https://rss.tempo.co/nasional", "category_hint": "hukum"},
    {"name": "CNN Indonesia", "url": "https://rss.cnnindonesia.com/nasional", "category_hint": "hukum"},
    {"name": "Bisnis.com", "url": "https://rss.bisnis.com/news", "category_hint": "ekonomi"},
]


class RSSScraper(BaseScraper):
    source_name = "rss_media"
    source_type = "news"

    def scrape_feed(self, db, feed_url: str, site_name: str) -> int:
        feed = feedparser.parse(feed_url)
        saved = 0

        for entry in feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            snippet = entry.get("summary", "")[:200]
            published = None

            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(*entry.published_parsed[:6])
                except Exception:
                    pass

            if link and title and self.save_raw_document(
                db=db,
                source_url=link,
                title=title,
                content_text=snippet,
                published_date=published,
                snippet=snippet,
                metadata={"feed_name": site_name, "feed_url": feed_url},
            ):
                saved += 1

        return saved

    def scrape_all(self, db) -> dict:
        results = {}
        for feed in RSS_FEEDS:
            try:
                saved = self.scrape_feed(db, feed["url"], feed["name"])
                results[feed["name"]] = saved
            except Exception as e:
                results[feed["name"]] = f"error: {str(e)}"
        return results