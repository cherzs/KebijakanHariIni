from datetime import datetime, date
from uuid import UUID


class CategoryOut:
    def __init__(self, id: UUID, slug: str, name: str, description: str | None = None):
        self.id = id
        self.slug = slug
        self.name = name
        self.description = description


class SourceOut:
    def __init__(self, id: UUID, source_type: str, title: str, url: str,
                 snippet: str | None = None, published_date: date | None = None,
                 site_name: str | None = None):
        self.id = id
        self.source_type = source_type
        self.title = title
        self.url = url
        self.snippet = snippet
        self.published_date = published_date
        self.site_name = site_name


class TimelineOut:
    def __init__(self, id: UUID, date: date, title: str, description: str | None = None,
                 sort_order: int = 0):
        self.id = id
        self.date = date
        self.title = title
        self.description = description
        self.sort_order = sort_order


class PolicyListOut:
    def __init__(self, id: UUID, title: str, slug: str, status: str,
                 summary_30sec: str | None, primary_category: CategoryOut | None,
                 published_at: datetime | None, created_at: datetime, updated_at: datetime):
        self.id = id
        self.title = title
        self.slug = slug
        self.status = status
        self.summary_30sec = summary_30sec
        self.primary_category = primary_category
        self.published_at = published_at
        self.created_at = created_at
        self.updated_at = updated_at