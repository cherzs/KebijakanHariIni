import hashlib
import json
import re
from datetime import datetime
from typing import Optional
from sqlalchemy import select
from ..core.database import SessionLocal
from ..models.models import RawDocument


class BaseScraper:
    source_name: str = ""
    source_type: str = ""

    def _normalize_url(self, url: str) -> str:
        return url.strip().rstrip("/")

    def is_url_processed(self, db, url: str) -> bool:
        normalized = self._normalize_url(url)
        return db.execute(
            select(RawDocument.id).where(RawDocument.source_url == normalized)
        ).scalar_one_or_none() is not None

    def save_raw_document(self, db, source_url: str, title: str, content_text: str,
                          published_date: Optional[datetime] = None, snippet: str = "",
                          metadata: dict = None) -> bool:
        normalized = self._normalize_url(source_url)
        if self.is_url_processed(db, normalized):
            return False

        doc = RawDocument(
            source_url=normalized,
            source_type=self.source_type,
            site_name=self.source_name,
            title=title[:500] if title else None,
            content_text=content_text[:5000] if content_text else None,
            snippet=snippet[:500] if snippet else None,
            published_date=published_date,
            metadata_json=json.dumps(metadata, ensure_ascii=False) if metadata else None,
            processed=False,
        )
        db.add(doc)
        db.commit()
        return True