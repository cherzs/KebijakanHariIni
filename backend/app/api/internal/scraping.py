from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...api.deps import require_admin
from ...models.models import RawDocument
from ...tasks.celery_app import run_rss_scraper, run_jdih_scraper, run_all_scrapers

router = APIRouter(prefix="/internal/scrape", tags=["internal-scraping"])


@router.post("/rss")
def trigger_rss_scrape(user=Depends(require_admin)):
    task = run_rss_scraper.delay()
    return {"status": "dispatched", "task_id": task.id}


@router.post("/jdih-setneg")
def trigger_jdih_scrape(user=Depends(require_admin)):
    task = run_jdih_scraper.delay()
    return {"status": "dispatched", "task_id": task.id}


@router.post("/all")
def trigger_all_scrapers(user=Depends(require_admin)):
    task = run_all_scrapers.delay()
    return {"status": "dispatched", "task_id": task.id}


@router.get("/raw-documents")
def list_raw_documents(
    page: int = 1,
    limit: int = 50,
    processed: bool | None = None,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    query = db.query(RawDocument)
    if processed is not None:
        query = query.filter(RawDocument.processed == processed)
    total = query.count()
    items = query.order_by(RawDocument.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": [
            {
                "id": str(item.id),
                "source_url": item.source_url,
                "source_type": item.source_type,
                "title": item.title,
                "site_name": item.site_name,
                "published_date": item.published_date.isoformat() if item.published_date else None,
                "processed": item.processed,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ],
    }