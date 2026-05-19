import re
import logging
from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models.models import RawDocument, Policy, Source, PolicyCategory

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "pajak": ["pajak", "pajak penghasilan", "pph", "ppn", "pbb", "bea", "fiskal", "tarif pajak", "tax"],
    "ekonomi": ["ekonomi", "makro", "gdp", "inflasi", "bunga", "moneter", "fiskal", "subsidi bbm", "impor", "ekspor"],
    "umkm": ["umkm", "usaha mikro", "usaha kecil", "kur", "kredit usaha", "umkm", "mse", "warung"],
    "tenaga-kerja": ["tenaga kerja", "tki", "pekerja", "buruh", "upah minimum", "ump", "umk", "phk", "outsourcing", "serikat buruh", "gig"],
    "pendidikan": ["pendidikan", "sekolah", "kurikulum", "guru", "universitas", "beasiswa", "pip", "kuliah"],
    "kesehatan": ["kesehatan", "bpjs kesehatan", "rumah sakit", "vaksin", "obat", "jkn", "stunting", "puskesmas"],
    "digital-teknologi": ["digital", "teknologi", "data pribadi", "pse", "kominfo", "internet", "ai", "startup", "e-commerce", "fintech"],
    "infrastruktur": ["infrastruktur", "jalan tol", "pelabuhan", "bandara", "irigasi", "ikn", "pembangunan"],
    "hukum": ["hukum", "undang-undang", "uu ", "Peraturan", "legislasi", "dpr", "mahkamah", "kuhp", "regulasi"],
    "bansos": ["bansos", "bantuan sosial", "pkh", "blt", "kartu prakerja", " subsidi energi", "program keluarga"],
    "pangan": ["pangan", "beras", "bulog", "pupuk", "pertanian", "harga pangan", "stunting", "keamanan pangan"],
    "transportasi": ["transportasi", "mrt", "lrt", "kereta", "tol", "angkutan", "bus", "ojol", "ride hailing"],
    "perumahan": ["perumahan", "flpp", "rumah", "kpr", "rusunawa", "tapera", "dpr"],
}

STATUS_KEYWORDS = {
    "wacana": ["diwacanakan", "wacana", "direncanakan", "diusulkan", "akan dibahas", "akan diprioritaskan"],
    "draf": ["draf", "rancangan", "ruu", "draft", "belum disahkan", "tahap penyusunan"],
    "dibahas": ["dibahas", "pembahasan", "rapat dpr", "panitia kerja", "fraksi", "dipolemikan", "debate"],
    "disahkan": ["disahkan", "ditetapkan", "diundangkan", "diputuskan", "disetujui", "resmi", "diumumkan"],
    "berlaku": ["berlaku", "efektif", "diberlakukan", "mulai berlaku", "implementasi"],
    "ditunda": ["ditunda", "ditangguhkan", "dibatalkan sementara", "postponed", "delayed"],
    "dibatalkan": ["dibatalkan", "dicabut", "ditarik", "withdrawn", "repealed", "dihapus"],
}


def classify_category(title: str, snippet: str = "") -> str:
    text = f"{title} {snippet}".lower()
    best_category = "hukum"
    best_score = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def detect_status_from_text(title: str, snippet: str = "") -> str:
    text = f"{title} {snippet}".lower()

    for status, keywords in STATUS_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return status

    return "wacana"


def cluster_documents(db: Session) -> list[dict]:
    unprocessed = db.execute(
        select(RawDocument).where(RawDocument.processed == False).order_by(RawDocument.published_date.desc())
    ).scalars().all()

    clusters: dict[str, list] = {}

    for doc in unprocessed:
        normalized_title = re.sub(r"[^\w\s]", "", doc.title.lower() if doc.title else "")
        normalized_title = re.sub(r"\s+", " ", normalized_title).strip()

        matched = False
        for cluster_key in clusters:
            key_words = set(cluster_key.split())
            title_words = set(normalized_title.split()[:5])
            overlap = len(key_words & title_words)

            if overlap >= 2 and (overlap / max(len(key_words), 1)) >= 0.4:
                clusters[cluster_key].append(doc)
                matched = True
                break

        if not matched:
            key = " ".join(normalized_title.split()[:6])
            clusters[key] = [doc]

    result = []
    for key, docs in clusters.items():
        if len(docs) >= 1:
            result.append({
                "cluster_key": key,
                "documents": docs,
                "count": len(docs),
            })

    result.sort(key=lambda x: x["count"], reverse=True)
    return result


def create_draft_from_cluster(db: Session, cluster: dict, admin_user_id=None) -> Policy | None:
    docs = cluster["documents"]
    if not docs:
        return None

    primary_doc = docs[0]

    title = primary_doc.title
    if not title:
        return None

    slug = re.sub(r"[^\w\s-]", "", title.lower().strip())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")[:200]

    existing = db.execute(select(Policy).where(Policy.slug == slug)).scalar_one_or_none()
    if existing:
        return existing

    category_slug = classify_category(
        primary_doc.title or "",
        primary_doc.snippet or "",
    )
    category = db.execute(
        select(PolicyCategory).where(PolicyCategory.slug == category_slug)
    ).scalar_one_or_none()
    if category:
        category_id = category.id
    else:
        hukum = db.execute(
            select(PolicyCategory).where(PolicyCategory.slug == "hukum")
        ).scalar_one_or_none()
        category_id = hukum.id if hukum else None

    detected_status = detect_status_from_text(
        primary_doc.title or "",
        primary_doc.snippet or "",
    )

    sources_text = "\n".join([
        f"- {d.title} ({d.source_url})" for d in docs[:5]
    ])

    policy = Policy(
        title=title,
        slug=slug,
        status=detected_status,
        primary_category_id=category_id,
        published_status="draft",
        source_confidence="low",
        verification_status="needs_verification",
        summary_30sec=f"[DRAFT] Kebijakan terkait: {title}. Memerlukan review editor.",
        created_by=admin_user_id,
    )
    db.add(policy)
    db.flush()

    if category_id:
        db.add(PolicyCategory(policy_id=policy.id, category_id=category_id))

    for doc in docs[:10]:
        source = Source(
            policy_id=policy.id,
            source_type="official" if doc.source_type == "official" else "news",
            title=doc.title or "Untitled",
            url=doc.source_url,
            snippet=doc.snippet[:200] if doc.snippet else None,
            published_date=doc.published_date,
            site_name=doc.site_name,
            verification_status="needs_verification",
        )
        db.add(source)

    for doc in docs:
        doc.processed = True
        doc.policy_id = policy.id

    db.commit()
    return policy


def process_unprocessed_documents(db: Session, admin_user_id=None) -> list[Policy]:
    clusters = cluster_documents(db)

    created = []
    for cluster in clusters:
        if cluster["count"] >= 1:
            policy = create_draft_from_cluster(db, cluster, admin_user_id)
            if policy:
                created.append(policy)
                logger.info(f"Created draft policy: {policy.title}")

    return created