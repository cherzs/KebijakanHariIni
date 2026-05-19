import feedparser
from datetime import datetime
from .base import BaseScraper

RSS_FEEDS = [
    {"name": "Kompas", "url": "https://rss.kompas.com/news", "category_hint": "hukum"},
    {"name": "Detik", "url": "https://rss.detik.com/index.php/detik", "category_hint": "hukum"},
    {"name": "Tempo", "url": "https://rss.tempo.co/nasional", "category_hint": "hukum"},
    {"name": "CNN Indonesia", "url": "https://rss.cnnindonesia.com/nasional", "category_hint": "hukum"},
]


class RSSScraper(BaseScraper):
    source_name = "rss_media"
    source_type = "news"

    def scrape_feed(self, feed_url: str, site_name: str):
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
                source_url=link,
                title=title,
                content_text=snippet,
                published_date=published,
            ):
                saved += 1

        return saved

    def scrape_all(self):
        total = 0
        for feed in RSS_FEEDS:
            try:
                saved = self.scrape_feed(feed["url"], feed["name"])
                total += saved
            except Exception as e:
                print(f"Error scraping {feed['name']}: {e}")
        return total