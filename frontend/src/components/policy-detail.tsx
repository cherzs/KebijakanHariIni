import { PolicyDetail, STATUS_LABELS } from "@/lib/api";
import { StatusBadge, CategoryBadge } from "@/components/layout";

interface PolicyDetailViewProps {
  policy: PolicyDetail;
}

export function PolicyDetailView({ policy }: PolicyDetailViewProps) {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center gap-2 mb-4">
        <StatusBadge status={policy.status} />
        {policy.categories.map((c) => (
          <CategoryBadge key={c.id} name={c.name} />
        ))}
      </div>

      <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-6">{policy.title}</h1>

      {policy.summary_30sec && (
        <section className="mb-8">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-amber-800 uppercase tracking-wider mb-2">
              Ringkasan 30 Detik
            </h2>
            <p className="text-gray-800 leading-relaxed">{policy.summary_30sec}</p>
          </div>
        </section>
      )}

      {policy.affected_groups && (
        <section className="mb-8">
          <div className="bg-purple-50 border border-purple-200 rounded-xl p-5">
            <h2 className="text-sm font-semibold text-purple-800 uppercase tracking-wider mb-2">
              Siapa yang Terdampak
            </h2>
            <p className="text-gray-800 leading-relaxed">{policy.affected_groups}</p>
          </div>
        </section>
      )}

      {policy.government_claim && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Klaim Pemerintah</h2>
          <p className="text-gray-700 leading-relaxed">{policy.government_claim}</p>
        </section>
      )}

      {policy.public_criticism && (
        <section className="mb-8">
          <div className="bg-red-50 border border-red-200 rounded-xl p-5">
            <h2 className="text-lg font-semibold text-red-900 mb-3">Kritik Publik</h2>
            <p className="text-gray-700 leading-relaxed">{policy.public_criticism}</p>
          </div>
        </section>
      )}

      {policy.simple_explanation && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Penjelasan Sederhana</h2>
          <div className="prose prose-gray max-w-none text-gray-700 leading-relaxed whitespace-pre-line">
            {policy.simple_explanation}
          </div>
        </section>
      )}

      {policy.impact_explanation && (
        <section className="mb-8">
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <h2 className="text-lg font-semibold text-blue-900 mb-3">Dampak ke Publik</h2>
            <div className="text-gray-700 leading-relaxed whitespace-pre-line">
              {policy.impact_explanation}
            </div>
          </div>
        </section>
      )}

      {policy.timelines.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Timeline</h2>
          <div className="relative pl-6 border-l-2 border-gray-200">
            {policy.timelines
              .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
              .map((t) => (
                <div key={t.id} className="mb-5 relative">
                  <div className="absolute -left-[1.85rem] w-3.5 h-3.5 rounded-full bg-primary border-4 border-white" />
                  <div className="text-xs text-gray-400 mb-1">
                    {new Date(t.date).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}
                  </div>
                  <div className="font-medium text-gray-900">{t.title}</div>
                  {t.description && <div className="text-sm text-gray-600 mt-0.5">{t.description}</div>}
                </div>
              ))}
          </div>
        </section>
      )}

      {policy.sources.length > 0 && (
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">Sumber</h2>
          <div className="space-y-2">
            {policy.sources.map((s) => (
              <a
                key={s.id}
                href={s.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block bg-white border border-gray-200 rounded-lg p-4 hover:border-primary-light transition"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${s.source_type === "official" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"}`}>
                    {s.source_type === "official" ? "Resmi" : "Berita"}
                  </span>
                  {s.site_name && <span className="text-xs text-gray-400">{s.site_name}</span>}
                </div>
                <div className="font-medium text-gray-900 text-sm">{s.title}</div>
                {s.snippet && <div className="text-xs text-gray-500 mt-1 line-clamp-2">{s.snippet}</div>}
                {s.published_date && (
                  <div className="text-xs text-gray-400 mt-1">
                    {new Date(s.published_date).toLocaleDateString("id-ID")}
                  </div>
                )}
              </a>
            ))}
          </div>
        </section>
      )}

      <div className="text-xs text-gray-400 pt-4 border-t border-gray-100">
        Terakhir diperbarui: {new Date(policy.updated_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}
      </div>
    </div>
  );
}