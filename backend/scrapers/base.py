import hashlib
from datetime import datetime
from typing import Optional


class BaseScraper:
    source_name: str = ""
    source_type: str = ""

    def __init__(self, db_session=None):
        self.db = db_session

    def _hash_url(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def is_url_processed(self, url: str) -> bool:
        from ..models.models import RawDocument
        from sqlalchemy import select
        result = self.db.execute(
            select(RawDocument.id).where(RawDocument.source_url == url)
        ).scalar_one_or_none()
        return result is not None

    def save_raw_document(self, source_url: str, title: str, content_text: str,
                          published_date: Optional[datetime] = None) -> bool:
        from ..models.models import RawDocument

        if self.is_url_processed(source_url):
            return False

        doc = RawDocument(
            source_url=source_url,
            source_type=self.source_type,
            site_name=self.source_name,
            title=title,
            content_text=content_text[:5000],
            published_date=published_date,
            processed=False,
        )
        self.db.add(doc)
        self.db.commit()
        return True