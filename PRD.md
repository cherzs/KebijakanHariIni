# PRD — KawalKebijakan (codename)

> Versi: MVP v1 | Tanggal: 2026-05-20

---

## 1. Product Overview

KawalKebijakan adalah website publik yang membantu masyarakat Indonesia memahami kebijakan pemerintah dengan bahasa sederhana, netral, dan berbasis sumber. Ini bukan portal berita — ini **policy tracker**.

Satu tempat untuk melihat kebijakan apa saja yang sedang dibahas, sudah berlaku, atau dibatalkan, lengkap dengan ringkasan singkat, status terkini, timeline, dan dampak ke publik.

---

## 2. Problem Statement

| Problem | Impact |
|---------|--------|
| Info kebijakan tersebar di puluhan situs resmi | Masyarakat tidak tahu kebijakan apa yang sedang dibahas |
| Dokumen hukum ditulis dalam bahasa legalese | Orang awam tidak mengerti substansi kebijakan |
| Media berita hanya liput saat sudah jadi berita | Tidak ada tracking dari wacana hingga berlaku |
| Tidak ada satu tempat yang netral dan terstruktur | Jurnalis, UMKM, warga sulit mengambil posisi terinformasi |

---

## 3. Target Users

| Segment | Need | Priority |
|---------|------|----------|
| Masyarakat umum | Pahami kebijakan yang affect hidup mereka | P0 |
| Jurnalis | Cari sumber, track status, dapatkan konteks cepat | P0 |
| Mahasiswa | Bahan riset/kuliah tentang kebijakan publik | P1 |
| Content creator | Buat konten edukasi dari kebijakan | P1 |
| UMKM / freelancer | Tahu regulasi yang impact bisnis | P1 |
| Analis kebijakan | Track perubahan status & perbandingan draf | P2 |
| Perusahaan | Monitor regulasi yang relevant ke industri | P2 |

---

## 4. Core Value Proposition

**"Pahami kebijakan pemerintah dalam 30 detik — tanpa harus baca puluhan berita dan dokumen hukum."**

Three pillars:
1. **Ringkas** — 30-second summary dalam bahasa sehari-hari
2. **Terstruktur** — status, timeline, kategori, dampak, semua di satu tempat
3. **Bersumber** — setiap klaim bisa dilacak ke sumber resmi

---

## 5. MVP Scope

| Feature | Detail |
|---------|--------|
| List kebijakan terbaru | Paginated, sorted by update terbaru |
| Detail kebijakan | Halaman lengkap per kebijakan |
| Ringkasan 30 detik | AI-generated, admin-reviewed |
| Status kebijakan | wacana → draf → dibahas → disahkan → berlaku / ditunda / dibatalkan |
| Timeline kebijakan | Milestone dates dengan deskripsi singkat |
| Dampak ke publik | "Siapa yang terdampak?" per kebijakan |
| Kategori | ekonomi, pajak, UMKM, tenaga kerja, pendidikan, kesehatan, digital-teknologi, infrastruktur, hukum |
| Sumber resmi & berita | Link + judul + tanggal + snippet pendek |
| Search & filter | Full-text search + filter by kategori & status |
| Admin review | Draft mode, admin approve sebelum publish |
| Mobile-responsive | Harus bisa diakses dengan nyaman di HP |

---

## 6. Non-MVP Scope

- User login / akun publik
- Bookmark & notifikasi push/email
- Komentar / diskusi
- Perbandingan side-by-side antar kebijakan
- API publik untuk developer
- Embed widget untuk media
- PDF export
- Multi-bahasa (English)
- Meilisearch/Typesense
- OAuth / SSO
- Payment/monetisasi
- Mobile app (native)

---

## 7. User Flow

```
Landing Page (list kebijakan)
  ├── Filter by kategori
  ├── Filter by status
  ├── Search keyword
  └── Click kebijakan
        └── Detail Page
              ├── Ringkasan 30 detik
              ├── Status saat ini
              ├── Timeline
              ├── Dampak ke publik
              ├── Kategori
              └── Sumber & berita terkait
```

---

## 8. Admin Flow

```
Admin Login → Dashboard
  ├── Daftar kebijakan (draft + published)
  ├── Create kebijakan baru
  │     ├── Input judul & deskripsi awal
  │     └── Trigger AI processing
  ├── Review AI output
  │     ├── Edit ringkasan
  │     ├── Edit status
  │     ├── Edit timeline
  │     ├── Edit dampak
  │     ├── Edit kategori
  │     └── Tambah/edit sumber
  ├── Approve & publish
  └── Edit kebijakan yang sudah published
```

---

## 9. Data Pipeline Flow

```
Scraper Layer
  ├── JDIH Setneg scraper
  ├── JDIH BPK scraper
  ├── DPR/Prolegnas scraper
  ├── Kementerian scraper (per kementerian)
  ├── Sekretariat Kabinet scraper
  └── RSS/news scraper (media Indonesia)
        │
        ▼
Raw Data Storage (PostgreSQL: raw_documents table)
        │
        ▼
Deduplication & Enrichment (Celery task)
        │
        ▼
AI Processing (Celery task)
  ├── Summarize
  ├── Classify category
  ├── Detect status
  ├── Extract timeline
  ├── Explain impact
  └── Generate simple explanation
        │
        ▼
Policy Record (PostgreSQL: policies table — status=draft)
        │
        ▼
Admin Review & Approve
        │
        ▼
Published (status=published → visible di frontend)
```

---

## 10. AI Processing Flow

```
Raw documents + news articles (clustered by topic)
        │
        ▼
┌─────────────────────────────────┐
│  Step 1: Classify Category     │
│  Input: judul + snippet        │
│  Output: primary category      │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 2: Detect Status         │
│  Input: judul + konteks sumber │
│  Output: status enum           │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 3: Summarize Policy      │
│  Input: aggregated sumber      │
│  Output: ringkasan 30 detik    │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 4: Extract Timeline      │
│  Input: semua sumber           │
│  Output: list of milestones    │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 5: Explain Impact        │
│  Input: kebijakan + konteks    │
│  Output: dampak ke publik      │
└─────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────┐
│  Step 6: Simple Explanation    │
│  Input: kebijakan full         │
│  Output: penjelasan bahasa     │
│          sehari-hari            │
└─────────────────────────────────┘
        │
        ▼
Policy draft record → admin review
```

---

## 11. Database Schema

```sql
-- ============================================
-- CORE TABLES
-- ============================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    role            VARCHAR(20) NOT NULL DEFAULT 'viewer'
                        CHECK (role IN ('admin', 'editor', 'viewer')),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug        VARCHAR(50) UNIQUE NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Pre-seed categories
INSERT INTO categories (slug, name) VALUES
    ('ekonomi', 'Ekonomi'),
    ('pajak', 'Pajak'),
    ('umkm', 'UMKM'),
    ('tenaga-kerja', 'Tenaga Kerja'),
    ('pendidikan', 'Pendidikan'),
    ('kesehatan', 'Kesehatan'),
    ('digital-teknologi', 'Digital & Teknologi'),
    ('infrastruktur', 'Infrastruktur'),
    ('hukum', 'Hukum');

CREATE TABLE policies (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title                VARCHAR(500) NOT NULL,
    slug                 VARCHAR(500) UNIQUE NOT NULL,
    summary_30sec        TEXT,
    simple_explanation   TEXT,
    impact_explanation   TEXT,
    status               VARCHAR(20) NOT NULL DEFAULT 'wacana'
                            CHECK (status IN (
                                'wacana', 'draf', 'dibahas',
                                'disahkan', 'berlaku',
                                'ditunda', 'dibatalkan'
                            )),
    category_id          UUID REFERENCES categories(id),
    published_status     VARCHAR(20) NOT NULL DEFAULT 'draft'
                            CHECK (published_status IN ('draft', 'published', 'archived')),
    created_by           UUID REFERENCES users(id),
    reviewed_by          UUID REFERENCES users(id),
    published_at         TIMESTAMPTZ,
    created_at           TIMESTAMPTZ DEFAULT NOW(),
    updated_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE policy_categories (
    policy_id    UUID REFERENCES policies(id) ON DELETE CASCADE,
    category_id  UUID REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (policy_id, category_id)
);

CREATE TABLE policy_timelines (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id   UUID REFERENCES policies(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    sort_order  INT DEFAULT 0,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE sources (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id   UUID REFERENCES policies(id) ON DELETE CASCADE,
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('official', 'news')),
    title       VARCHAR(500) NOT NULL,
    url         TEXT NOT NULL,
    snippet     TEXT,
    published_date DATE,
    site_name   VARCHAR(200),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE raw_documents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_url      TEXT NOT NULL,
    source_type     VARCHAR(50) NOT NULL,
    site_name       VARCHAR(200),
    title           VARCHAR(500),
    content_text    TEXT,
    published_date   DATE,
    fetched_at      TIMESTAMPTZ DEFAULT NOW(),
    processed       BOOLEAN DEFAULT FALSE,
    policy_id       UUID REFERENCES policies(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_policies_status ON policies(status);
CREATE INDEX idx_policies_category ON policies(category_id);
CREATE INDEX idx_policies_published ON policies(published_status);
CREATE INDEX idx_policies_published_at ON policies(published_at DESC);
CREATE INDEX idx_policies_slug ON policies(slug);
CREATE INDEX idx_policy_timelines_policy ON policy_timelines(policy_id);
CREATE INDEX idx_sources_policy ON sources(policy_id);
CREATE INDEX idx_raw_docs_processed ON raw_documents(processed);
CREATE INDEX idx_raw_docs_source ON raw_documents(source_url);

-- ============================================
-- FULL-TEXT SEARCH
-- ============================================

ALTER TABLE policies ADD COLUMN search_vector TSVECTOR;

CREATE INDEX idx_policies_search ON policies USING GIN(search_vector);

-- Trigger to auto-update search_vector
CREATE OR REPLACE FUNCTION policies_search_vector_update() RETURNS trigger AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('simple', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('simple', COALESCE(NEW.summary_30sec, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.simple_explanation, '')), 'C') ||
        setweight(to_tsvector('simple', COALESCE(NEW.impact_explanation, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_policies_search_vector
    BEFORE INSERT OR UPDATE OF title, summary_30sec, simple_explanation, impact_explanation
    ON policies
    FOR EACH ROW EXECUTE FUNCTION policies_search_vector_update();
```

---

## 12. API Endpoint List

### Auth (Admin)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Admin login |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/auth/me` | Current user info |

### Policies (Public)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/policies` | List published policies (paginated, filterable) |
| GET | `/api/policies/{slug}` | Get policy detail |
| GET | `/api/policies/search?q={query}` | Full-text search |

Query params for list: `?category={slug}&status={status}&page=1&limit=20&sort=updated_at`

### Policies (Admin)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/admin/policies` | List all policies (including drafts) |
| POST | `/api/admin/policies` | Create policy |
| GET | `/api/admin/policies/{id}` | Get policy (any status) |
| PUT | `/api/admin/policies/{id}` | Update policy |
| PATCH | `/api/admin/policies/{id}/publish` | Publish policy |
| PATCH | `/api/admin/policies/{id}/archive` | Archive policy |
| DELETE | `/api/admin/policies/{id}` | Delete policy (soft) |

### Timelines (Admin)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/admin/policies/{id}/timelines` | Add timeline entry |
| PUT | `/api/admin/policies/{id}/timelines/{tid}` | Update timeline |
| DELETE | `/api/admin/policies/{id}/timelines/{tid}` | Delete timeline |

### Sources (Admin)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/admin/policies/{id}/sources` | Add source |
| PUT | `/api/admin/policies/{id}/sources/{sid}` | Update source |
| DELETE | `/api/admin/policies/{id}/sources/{sid}` | Delete source |

### AI Processing (Admin)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/admin/policies/{id}/process` | Trigger AI processing |
| GET | `/api/admin/policies/{id}/process/status` | Check processing status |

### Categories (Public)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/categories` | List all categories |

### Scraping (Internal)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/internal/scrape/jdih-setneg` | Trigger JDIH Setneg scrape |
| POST | `/api/internal/scrape/jdih-bpk` | Trigger JDIH BPK scrape |
| POST | `/api/internal/scrape/rss` | Trigger RSS news scrape |
| GET | `/api/internal/scrape/status` | Get scraping task status |

---

## 13. Frontend Page Structure

```
/                          → Landing (list kebijakan terbaru)
/search?q=                 → Search results
/policy/{slug}             → Policy detail
/about                     → Tentang situs

/admin/login               → Admin login
/admin/dashboard            → Dashboard overview
/admin/policies             → List all policies (draft + published)
/admin/policies/new         → Create policy
/admin/policies/{id}/edit   → Edit policy
```

---

## 14. Detail Halaman Policy

```
┌─────────────────────────────────────────────┐
│  [Status Badge]  [Kategori Badge]           │
│                                             │
│  JUDUL KEBIJAKAN                            │
│                                             │
│  ┌─ RINGKASAN 30 DETIK ──────────────────┐  │
│  │  3-4 kalimat dalam bahasa sehari-hari │  │
│  │  yang menjelaskan inti kebijakan.      │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ PENJELASAN SEDERHANA ────────────────┐  │
│  │  Versi lebih panjang, analogi, konteks │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ DAMPAK KE PUBLIK ────────────────────┐  │
│  │  • Siapa yang terdampak               │  │
│  │  • Apa yang berubah                   │  │
│  │  • Kapan berlaku                      │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ TIMELINE ────────────────────────────┐  │
│  │  ● 2026-01-15  Wacana muncul          │  │
│  │  ● 2026-03-20  Draf diterbitkan       │  │
│  │  ● 2026-05-10  Dibahas di DPR         │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  ┌─ SUMBER ──────────────────────────────┐  │
│  │  📎 Peraturan Pemerintah No. X/2026   │  │
│  │  📰 Kompas - "Judul berita"           │  │
│  │  📅 Detik - "Judul berita"             │  │
│  └───────────────────────────────────────┘  │
│                                             │
│  Terakhir diperbarui: 20 Mei 2026           │
└─────────────────────────────────────────────┘
```

---

## 15. Role dan Permission

| Role | Permission |
|------|-----------|
| **viewer** (publik) | Lihat kebijakan published, search, filter |
| **editor** | CRUD kebijakan, trigger AI, manage sumber & timeline |
| **admin** | Semua permission editor + manage user + publish/approve + manage scraping |

Initial setup: 1 admin account dibuat via seed/script.

---

## 16. Scraping Strategy

### Prinsip

1. **Jangan copy full article** — ambil metadata, judul, tanggal, snippet (max 200 karakter), dan link sumber
2. **Rate limit** — 1 request per 2-3 detik per source
3. **Respect robots.txt** — cek dulu sebelum scrape
4. **Identify yourself** — User-Agent header yang jelas
5. **Schedule** — scrape rutin (2-4x sehari), bukan agresif

### Source-by-Source

| Source | Method | Schedule | Notes |
|--------|--------|----------|-------|
| JDIH Setneg | BeautifulSoup/requests | 4x/hari | Struktur HTML relatif stabil |
| JDIH BPK | BeautifulSoup/requests | 2x/hari | Cek API publik dulu |
| DPR/Prolegnas | BeautifulSoup | 2x/hari | Focus di halaman daftar |
| Kementerian | Per kementerian, BeautifulSoup | 1x/hari | Prioritas: Keuangan, Kemenaker, Kemenkes |
| Sekretariat Kabinet | BeautifulSoup | 2x/hari | Cek siaran pers |
| RSS Media | RSS parser (feedparser) | 4x/hari | Kompas, Detik, Tempo, CNN Indonesia, Bisnis.com |

### Deduplication Strategy

- URL-based: skip jika `source_url` sudah ada di `raw_documents`
- Content-based: hash judul + tanggal untuk deteksi duplikat antar source
- Cluster: group berita yang membahas topik yang sama → jadi satu policy record

---

## 17. AI Prompt Strategy

Semua prompt menggunakan **Bahasa Indonesia**. AI model bersifat provider-agnostic via abstraction layer.

### 17a. Summarize Policy

```
Kamu adalah penulis kebijakan publik Indonesia. Buatkan ringkasan kebijakan berikut dalam 3-4 kalimat bahasa sehari-hari. Ringkasan harus:
- Bisa dipahami orang awam dalam 30 detik
- Faktual dan netral
- Menyebutkan apa yang diatur, siapa yang terdampak, dan kapan

Sumber:
{aggregated_sources_text}

Output: ringkasan dalam bahasa Indonesia.
```

### 17b. Classify Category

```
Klasifikasikan kebijakan berikut ke SATU kategori utama. Pilihan: ekonomi, pajak, UMKM, tenaga kerja, pendidikan, kesehatan, digital-teknologi, infrastruktur, hukum.

Judul: {title}
Ringkasan: {summary_or_snippet}

Output hanya nama kategori, tanpa penjelasan.
```

### 17c. Detect Status

```
Tentukan status kebijakan berikut. Pilihan: wacana, draf, dibahas, disahkan, berlaku, ditunda, dibatalkan.

Judul: {title}
Konteks sumber:
{source_snippets}

Pertimbangkan:
- "wacana" = baru diusulkan/diwacanakan
- "draf" = ada draf resmi yang dipublikasikan
- "dibahas" = sedang dibahas di DPR/kementerian
- "disahkan" = sudah disetujui tapi belum berlaku
- "berlaku" = sudah berlaku efektif
- "ditunda" = ditangguhkan pelaksanaannya
- "dibatalkan" = dibatalkan/dicabut

Output hanya nama status.
```

### 17d. Extract Timeline

```
Buat timeline kebijakan berikut berdasarkan sumber-sumber ini. Format: array JSON.

[{"date": "YYYY-MM-DD", "title": "judul milestone", "description": "1 kalimat deskripsi"}]

Aturan:
- Setiap milestone harus punya tanggal spesifik jika ada di sumber
- Jika tanggal tidak pasti, gunakan tanggal artikel/berita sebagai proxy
- Urutkan dari terlama ke terbaru
- Maksimum 10 milestone

Judul kebijakan: {title}
Sumber:
{aggregated_sources_text}
```

### 17e. Explain Impact

```
Jelaskan dampak kebijakan berikut ke masyarakat. Format:

**Siapa yang terdampak:** [kelompok masyarakat]
**Apa yang berubah:** [perubahan konkret]
**Kapan berlaku:** [tanggal jika ada]

Aturan:
- Tulis dalam bahasa sehari-hari
- Fokus pada dampak nyata, bukan bahasa hukum
- Jika dampak belum jelas, tulis "Dampak masih dipelajari"
- Netral, tidak mengambil posisi pro/kontra

Judul: {title}
Sumber:
{aggregated_sources_text}
```

### 17f. Generate Simple Explanation

```
Jelaskan kebijakan berikut seolah-olah kamu menjelaskan ke tetangga kamu. Gunakan:
- Bahasa sehari-hari, bukan bahasa hukum
- Analogi jika membantu
- Kalimat pendek
- Tidak ada jargon kecuali perlu dijelaskan

Struktur:
1. Apa si kebijakan ini? (1-2 paragraf)
2. Kenapa ini muncul? (1 paragraf)
3. Terus gimana dampaknya? (1-2 paragraf)

Judul: {title}
Sumber:
{aggregated_sources_text}
```

---

## 18. Risiko Hukum / Copyright

| Risiko | Mitigasi |
|--------|----------|
| Copy artikel media | JANGAN copy full article. Hanya ambil judul, tanggal, snippet pendek (max 200 char), dan link. AI buat ringkasan ORIGINAL berdasarkan banyak sumber. |
| Copy dokumen hukum | Boleh referensi dan kutip parsial (fair use). Jangan tampilkan full text dokumen. |
| Defamasi | Semua konten harus fact-based. Klaim harus punya sumber. Admin review sebelum publish. |
| HKDP / UU ITE | Tidak boleh ada konten yang mengandung SARA, ujaran kebencian, atau hoaks. Admin moderation wajib. |
| Data pribadi | Jangan simpan data pribadi user (MVP tidak ada akun publik). |

**Prinsip utama:** Setiap kalimat di ringkasan harus bisa ditelusuri ke sumber asli. Jangan fabricate.

---

## 19. Risiko Bias Politik dan Mitigasi

| Risiko | Mitigasi |
|--------|----------|
| AI hallucination | Selalu sertakan sumber. Human review sebelum publish. |
| Bias seleksi sumber | Gunakan beragam media (mainstream + independen). Jangan hanya 1-2 media. |
| Framing pro/pemerintah | Prompt AI diberi instruksi eksplisit: netral, faktual, tanpa opini. |
| Absence of opposition view | Sertakan berita yang menyajikan berbagai perspektif. Prioritaskan sumber yang mengutip banyak pihak. |
| Status misclassification | Admin wajib verifikasi status. AI hanya saran. |

### Mitigasi tambahan:

- Di halaman About, tulis eksplisit: "Situs ini tidak berafiliasi dengan partai/manusia politik manapun."
- Tampilkan sumber dari berbagai sisi (pemerintah + kritik)
- Review guidelines untuk editor: jika kebijakan kontroversial, WAJIB sertakan minimal 2 sumber dengan perspektif berbeda

---

## 20. Monetisasi Jangka Panjang

| Phase | Model | Detail |
|-------|-------|--------|
| MVP | Gratis penuh | Tanpa iklan, tanpa bayar. Fokus kebangkitan user base. |
| 3-6 bulan | Donasi / Sponsor | Kofi, Saweria, atau sponsor dari organisasi yang align dengan misi. |
| 6-12 bulan | Premium tier | Email digest mingguan, notifikasi per kategori, akses API. |
| 12+ bulan | B2B / Enterprise | Dashboard monitoring regulasi untuk perusahaan, webhook API, custom report. |

---

## 21. Roadmap 7 Hari untuk MVP

| Hari | Task | Owner |
|------|------|-------|
| **1** | Setup project: FastAPI skeleton, Next.js skeleton, PostgreSQL schema, Docker Compose | Backend |
| **2** | CRUD API: policies, categories, timelines, sources. Auth (JWT). Admin endpoints. | Backend |
| **3** | Scraper: RSS media (2-3 source pertama) + JDIH Setneg. Celery + Redis queue. | Backend |
| **4** | AI processing pipeline: semua prompt, provider abstraction, Celery task. | Backend |
| **5** | Frontend: landing page (list), detail page, search. Tailwind styling. | Frontend |
| **6** | Frontend: admin dashboard, policy form, review flow. Connect ke API. | Frontend |
| **7** | Integration testing, seed data, bug fixes, deploy. | Full-stack |

**Target akhir hari 7:** Situs bisa diakses, menampilkan 10-20 kebijakan sample, admin bisa create/review/publish.

---

## 22. Roadmap 30 Hari Setelah MVP

| Minggu | Fokus |
|--------|-------|
| **Minggu 1** | Bug fixes performance. Tambah sumber scraper (5+ media, JDIH BPK, DPR). Mobile polish. |
| **Minggu 2** | SEO optimization (meta tags, sitemap, structured data). Tambah kategori. Notifikasi Slack untuk admin saat ada kebijakan baru. |
| **Minggu 3** | Email digest mingguan (sekarhicon/mailer). Analytics (PostHog/Plausible). Halaman About + Disclaimer. |
| **Minggu 4** | Bookmark & notifikasi per kategori (membutuhkan user auth). API rate limiting. Load testing. |

---

## 23. Rekomendasi Nama Produk

| Nama | Alasan |
|------|--------|
| **KawalKebijakan** | Kuat, familiar dengan format "Kawal*", jelas misinya. Direct. |
| RingkasKebijakan | Baik tapi kurang "aksi". Lebih cocok sebagai tagline. |
| BukaKebijakan | Friendly tapi terlalu umum. |
| KebijakanKita | Emosional tapi bisa diinterpretasikan bias. |
| PolicyID | Keren tapi kurang Indonesia banget. |

**Rekomendasi:** **KawalKebijakan** — kuat, Indonesia, actionable.

---

## 24. Positioning dan Tagline

**Positioning:**
Policy tracker Indonesia yang membuat kebijakan pemerintah bisa dipahami siapa saja dalam 30 detik.

**Tagline options:**
- **"Kebijakan pemerintah, dibahasarkan."** ← rekomendasi utama
- "30 detik pahami kebijakan."
- "Kebijakan pemerintah, sederhananya."
- "Urusan negara, urusan kita."

**Sub-tagline (untuk header):**
"Baca, pahami, dan pantau kebijakan pemerintah Indonesia."

---

## 25. Prioritas Task Development (by Impact)

| Priority | Task | Impact |
|----------|------|--------|
| **P0** | DB schema + API CRUD policies | Foundation, everything depends on this |
| **P0** | Policy list page (public) | Core user-facing feature |
| **P0** | Policy detail page (public) | Core user-facing feature |
| **P0** | AI processing pipeline | Core differentiation (vs just aggregating links) |
| **P1** | Admin policy form + review flow | Must-have for content quality |
| **P1** | RSS scraper (media) | Data source, but can start with manual input |
| **P1** | JDIH scraper | Key official source |
| **P1** | Search + filter | UX critical but can be simple at first |
| **P2** | Admin dashboard stats | Nice-to-have for MVP |
| **P2** | Celery scheduling & monitoring | Can do manual trigger at first |
| **P3** | Multiple categories per policy | Can do single category in MVP |
| **P3** | Meilisearch integration | PostgreSQL FTS is enough for MVP |

---

*PRD ini bersifat living document. Update seiring development berjalan.*