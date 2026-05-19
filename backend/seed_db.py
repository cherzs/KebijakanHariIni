import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from app.core.database import engine, SessionLocal, Base
from app.models.models import User, Category
from app.core.security import get_password_hash

CATEGORIES = [
    {"slug": "ekonomi", "name": "Ekonomi", "description": "Kebijakan ekonomi makro dan mikro"},
    {"slug": "pajak", "name": "Pajak", "description": "Kebijakan perpajakan"},
    {"slug": "umkm", "name": "UMKM", "description": "Kebijakan usaha mikro, kecil, dan menengah"},
    {"slug": "tenaga-kerja", "name": "Tenaga Kerja", "description": "Kebijakan ketenagakerjaan"},
    {"slug": "pendidikan", "name": "Pendidikan", "description": "Kebijakan pendidikan"},
    {"slug": "kesehatan", "name": "Kesehatan", "description": "Kebijakan kesehatan"},
    {"slug": "digital-teknologi", "name": "Digital & Teknologi", "description": "Kebijakan digital dan teknologi"},
    {"slug": "infrastruktur", "name": "Infrastruktur", "description": "Kebijakan infrastruktur"},
    {"slug": "hukum", "name": "Hukum", "description": "Kebijakan hukum dan peraturan"},
    {"slug": "bansos", "name": "Bantuan Sosial", "description": "Kebijakan bantuan sosial dan subsidi"},
    {"slug": "pangan", "name": "Pangan", "description": "Kebijakan pangan dan pertanian"},
    {"slug": "transportasi", "name": "Transportasi", "description": "Kebijakan transportasi publik"},
    {"slug": "perumahan", "name": "Perumahan", "description": "Kebijakan perumahan dan permukiman"},
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = "admin@kawalkebijakan.id"
        existing = db.query(User).filter(User.email == admin_email).first()
        if not existing:
            admin = User(
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                full_name="Admin KawalKebijakan",
                role="admin",
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print(f"Admin created: {admin_email}")
        else:
            print(f"Admin already exists: {admin_email}")

        for cat_data in CATEGORIES:
            existing_cat = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
            if not existing_cat:
                cat = Category(**cat_data)
                db.add(cat)
                print(f"Category created: {cat_data['name']}")
            else:
                existing_cat.name = cat_data["name"]
                existing_cat.description = cat_data["description"]
                print(f"Category updated: {cat_data['name']}")
        db.commit()
        print("Seed completed!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()