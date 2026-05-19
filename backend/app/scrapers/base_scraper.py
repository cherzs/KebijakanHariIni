import json
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from ..core.database import SessionLocal
from ..models.models import RawDocument, ScrapeLog

logger = logging.getLogger(__name__)


class BaseScraper:
    source_name: str = ""
    source_type: str = ""

    def _normalize_url(self, url: str) -> str:
        url = url.strip()
        url = url.rstrip("/")
        url = re.sub(r"^https?://(www\.)?", "https://", url)
        url = re.sub(r"\?.*$", "", url)
        url = re.sub(r"#.*$", "", url)
        return url

    def _normalize_title(self, title: str) -> str:
        t = title.lower().strip()
        t = re.sub(r"[^\w\s]", "", t)
        t = re.sub(r"\s+", " ", t)
        t = t[:200]
        return t

    def _title_hash(self, title: str) -> str:
        normalized = self._normalize_title(title)
        return str(hash(normalized))

    def is_url_duplicate(self, db, url: str) -> bool:
        normalized = self._normalize_url(url)
        return db.execute(
            select(RawDocument.id).where(RawDocument.source_url == normalized)
        ).scalar_one_or_none() is not None

    def is_title_duplicate(self, db, title: str) -> bool:
        normalized = self._normalize_title(title)
        return db.execute(
            select(RawDocument.id).where(
                func.lower(RawDocument.title).contains(normalized[:80])
            )
        ).scalar_one_or_none() is not None

    def save_raw_document(
        self,
        db,
        source_url: str,
        title: str,
        content_text: str,
        published_date: Optional[datetime] = None,
        snippet: str = "",
        metadata: dict = None,
    ) -> bool:
        normalized_url = self._normalize_url(source_url)
        if self.is_url_duplicate(db, normalized_url):
            return False

        doc = RawDocument(
            source_url=normalized_url,
            source_type=self.source_type,
            site_name=self.source_name,
            title=title[:500] if title else None,
            content_text=content_text[:5000] if content_text else None,
            snippet=snippet[:500] if snippet else None,
            published_date=published_date.date() if isinstance(published_date, datetime) else published_date,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
            processed=False,
        )
        db.add(doc)
        db.commit()
        return True

    def create_scrape_log(self, db, items_found: int, items_saved: int, items_skipped: int, error: str = None) -> ScrapeLog:
        log = ScrapeLog(
            scraper_name=self.source_name,
            status="completed" if not error else "error",
            items_found=items_found,
            items_saved=items_saved,
            items_skipped=items_skipped,
            error_message=error,
            started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        db.add(log)
        db.commit()
        return log