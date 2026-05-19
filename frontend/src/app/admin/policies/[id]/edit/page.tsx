"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { API_BASE } from "@/lib/api";

const STATUSES = [
  { value: "wacana", label: "Wacana" },
  { value: "draf", label: "Draf" },
  { value: "dibahas", label: "Dibahas" },
  { value: "disahkan", label: "Disahkan" },
  { value: "berlaku", label: "Berlaku" },
  { value: "ditunda", label: "Ditunda" },
  { value: "dibatalkan", label: "Dibatalkan" },
];

interface Policy {
  id: string;
  title: string;
  slug: string;
  status: string;
  published_status: string;
  summary_30sec: string | null;
  simple_explanation: string | null;
  impact_explanation: string | null;
  primary_category_id: string | null;
  categories: { id: string; name: string }[];
  sources: { id: string; source_type: string; title: string; url: string; snippet: string | null; published_date: string | null; site_name: string | null }[];
  timelines: { id: string; date: string; title: string; description: string | null }[];
}

export default function EditPolicyPage() {
  const router = useRouter();
  const params = useParams();
  const policyId = params.id as string;

  const [policy, setPolicy] = useState<Policy | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("wacana");
  const [summary, setSummary] = useState("");
  const [explanation, setExplanation] = useState("");
  const [impact, setImpact] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) { router.push("/admin/login"); return; }
    fetchPolicy(token);
  }, [policyId]);

  const fetchPolicy = async (token: string) => {
    try {
      const res = await fetch(`${API_BASE}/admin/policies/${policyId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Not found");
      const data = await res.json();
      setPolicy(data);
      setTitle(data.title);
      setStatus(data.status);
      setSummary(data.summary_30sec || "");
      setExplanation(data.simple_explanation || "");
      setImpact(data.impact_explanation || "");
    } catch {
      alert("Kebijakan tidak ditemukan");
      router.push("/admin/dashboard");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/admin/policies/${policyId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          title,
          status,
          summary_30sec: summary || null,
          simple_explanation: explanation || null,
          impact_explanation: impact || null,
        }),
      });
      if (!res.ok) throw new Error("Gagal menyimpan");
      alert("Tersimpan!");
    } catch {
      alert("Gagal menyimpan");
    } finally {
      setSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!confirm("Publish kebijakan ini?")) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/admin/policies/${policyId}/publish`, {
        method: "PATCH",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error("Gagal publish");
      alert("Berhasil dipublish!");
      fetchPolicy(token!);
    } catch {
      alert("Gagal publish");
    }
  };

  const handleAIProcess = async () => {
    setProcessing(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/admin/policies/${policyId}/process`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ force: true }),
      });
      if (!res.ok) throw new Error("Gagal memproses");
      alert("AI processing dimulai. Refresh halaman setelah beberapa detik untuk melihat hasilnya.");
    } catch {
      alert("Gagal memproses");
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>;
  if (!policy) return null;

  const PUB_LABELS: Record<string, string> = { draft: "Draft", published: "Published", archived: "Archived" };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Edit Kebijakan</h1>
        <div className="flex items-center gap-2">
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${policy.published_status === "published" ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
            {PUB_LABELS[policy.published_status] || policy.published_status}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Judul</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg">
            {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ringkasan 30 Detik</label>
          <textarea value={summary} onChange={(e) => setSummary(e.target.value)} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Penjelasan Sederhana</label>
          <textarea value={explanation} onChange={(e) => setExplanation(e.target.value)} rows={5} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Dampak ke Publik</label>
          <textarea value={impact} onChange={(e) => setImpact(e.target.value)} rows={3} className="w-full px-3 py-2 border border-gray-300 rounded-lg" />
        </div>

        {policy.timelines.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timeline</label>
            <div className="space-y-2">
              {policy.timelines.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()).map((t) => (
                <div key={t.id} className="flex gap-3 text-sm bg-gray-50 p-3 rounded-lg">
                  <span className="text-gray-400">{new Date(t.date).toLocaleDateString("id-ID")}</span>
                  <span className="font-medium text-gray-900">{t.title}</span>
                  {t.description && <span className="text-gray-500">{t.description}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {policy.sources.length > 0 && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sumber</label>
            <div className="space-y-2">
              {policy.sources.map((s) => (
                <div key={s.id} className="flex gap-3 text-sm bg-gray-50 p-3 rounded-lg">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${s.source_type === "official" ? "bg-green-100 text-green-800" : "bg-blue-100 text-blue-800"}`}>
                    {s.source_type === "official" ? "Resmi" : "Berita"}
                  </span>
                  <a href={s.url} target="_blank" rel="noopener noreferrer" className="font-medium text-primary hover:underline">{s.title}</a>
                  {s.site_name && <span className="text-gray-400">{s.site_name}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3 pt-4 border-t border-gray-200">
          <button onClick={handleSave} disabled={saving} className="bg-primary text-white px-6 py-2.5 rounded-lg hover:bg-primary-dark transition font-medium disabled:opacity-50">
            {saving ? "Menyimpan..." : "Simpan"}
          </button>
          <button onClick={handleAIProcess} disabled={processing} className="bg-secondary text-white px-6 py-2.5 rounded-lg hover:bg-emerald-700 transition font-medium disabled:opacity-50">
            {processing ? "Memproses..." : "Generate AI"}
          </button>
          {policy.published_status === "draft" && (
            <button onClick={handlePublish} className="bg-accent text-white px-6 py-2.5 rounded-lg hover:bg-amber-700 transition font-medium">
              Publish
            </button>
          )}
          <button onClick={() => router.push("/admin/dashboard")} className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-lg hover:bg-gray-200 transition font-medium">
            Kembali
          </button>
        </div>
      </div>
    </div>
  );
}