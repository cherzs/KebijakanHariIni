import json
import uuid
from ..core.config import Settings

settings = Settings()


class AIProvider:
    def __init__(self):
        self._clients = {}

    def _get_client(self, provider: str):
        if provider == "openai":
            from openai import OpenAI
            return OpenAI(api_key=settings.GROQ_API_KEY)
        elif provider == "deepseek":
            from openai import OpenAI
            return OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url="https://api.deepseek.com/v1",
            )
        elif provider == "groq":
            from openai import OpenAI
            return OpenAI(
                api_key=settings.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
        raise ValueError(f"Unknown AI provider: {provider}")

    def complete(self, system_prompt: str, user_prompt: str, model: str | None = None) -> str:
        provider = settings.AI_PROVIDER
        client = self._get_client(provider)
        response = client.chat.completions.create(
            model=model or settings.AI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content


ai_provider = AIProvider()

PROMPTS = {
    "summarize": """Kamu adalah penulis kebijakan publik Indonesia. Buatkan ringkasan kebijakan berikut dalam 3-4 kalimat bahasa sehari-hari. Ringkasan harus:
- Bisa dipahami orang awam dalam 30 detik
- Faktual dan netral
- Menyebutkan apa yang diatur, siapa yang terdampak, dan kapan

Sumber:
{sources}""",

    "classify": """Klasifikasikan kebijakan berikut ke SATU kategori utama. Pilihan: ekonomi, pajak, UMKM, tenaga-kerja, pendidikan, kesehatan, digital-teknologi, infrastruktur, hukum.

Judul: {title}
Ringkasan: {summary}

Output hanya nama kategori, tanpa penjelasan.""",

    "detect_status": """Tentukan status kebijakan berikut. Pilihan: wacana, draf, dibahas, disahkan, berlaku, ditunda, dibatalkan.

Judul: {title}
Konteks sumber:
{context}

Pertimbangkan:
- "wacana" = baru diusulkan/diwacanakan
- "draf" = ada draf resmi yang dipublikasikan
- "dibahas" = sedang dibahas di DPR/kementerian
- "disahkan" = sudah disetujui tapi belum berlaku
- "berlaku" = sudah berlaku efektif
- "ditunda" = ditangguhkan pelaksanaannya
- "dibatalkan" = dibatalkan/dicabut

Output hanya nama status.""",

    "extract_timeline": """Buat timeline kebijakan berikut berdasarkan sumber-sumber ini. Output hanya array JSON tanpa markdown.

[{{"date": "YYYY-MM-DD", "title": "judul milestone", "description": "1 kalimat deskripsi"}}]

Aturan:
- Setiap milestone harus punya tanggal spesifik jika ada di sumber
- Jika tanggal tidak pasti, gunakan tanggal artikel/berita sebagai proxy
- Urutkan dari terlama ke terbaru
- Maksimum 10 milestone

Judul kebijakan: {title}
Sumber:
{sources}""",

    "explain_impact": """Jelaskan dampak kebijakan berikut ke masyarakat.

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
{sources}""",

    "simple_explanation": """Jelaskan kebijakan berikut seolah-olah kamu menjelaskan ke tetangga kamu. Gunakan:
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
{sources}""",
}


def format_sources(sources: list) -> str:
    parts = []
    for s in sources:
        snippet = f" - {s.snippet}" if s.snippet else ""
        parts.append(f"- [{s.title}]({s.url}) ({s.published_date}){snippet}" if s.published_date else f"- [{s.title}]({s.url}){snippet}")
    return "\n".join(parts)


def summarize_policy(title: str, sources: list) -> str:
    return ai_provider.complete(
        PROMPTS["summarize"],
        PROMPTS["summarize"].format(sources=format_sources(sources)),
    )


def classify_category(title: str, summary: str) -> str:
    return ai_provider.complete(
        PROMPTS["classify"],
        PROMPTS["classify"].format(title=title, summary=summary),
    ).strip().lower()


def detect_status(title: str, context: str) -> str:
    return ai_provider.complete(
        PROMPTS["detect_status"],
        PROMPTS["detect_status"].format(title=title, context=context),
    ).strip().lower()


def extract_timeline(title: str, sources: list) -> list:
    raw = ai_provider.complete(
        PROMPTS["extract_timeline"],
        PROMPTS["extract_timeline"].format(title=title, sources=format_sources(sources)),
    )
    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return []


def explain_impact(title: str, sources: list) -> str:
    return ai_provider.complete(
        PROMPTS["explain_impact"],
        PROMPTS["explain_impact"].format(title=title, sources=format_sources(sources)),
    )


def generate_simple_explanation(title: str, sources: list) -> str:
    return ai_provider.complete(
        PROMPTS["simple_explanation"],
        PROMPTS["simple_explanation"].format(title=title, sources=format_sources(sources)),
    )