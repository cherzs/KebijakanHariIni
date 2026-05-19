"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
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

export default function NewPolicyPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [status, setStatus] = useState("wacana");
  const [summary, setSummary] = useState("");
  const [explanation, setExplanation] = useState("");
  const [impact, setImpact] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [categories, setCategories] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useState(() => {
    fetch(`${API_BASE}/categories`)
      .then((r) => r.json())
      .then(setCategories)
      .catch(() => {});
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_BASE}/admin/policies`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title,
          status,
          summary_30sec: summary || undefined,
          simple_explanation: explanation || undefined,
          impact_explanation: impact || undefined,
          primary_category_id: categoryId || undefined,
        }),
      });
      if (!res.ok) throw new Error("Gagal membuat kebijakan");
      const data = await res.json();
      router.push(`/admin/policies/${data.id}/edit`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Gagal membuat kebijakan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Tambah Kebijakan Baru</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Judul *</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              {STATUSES.map((s) => (
                <option key={s.value} value={s.value}>{s.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Kategori</label>
            <select
              value={categoryId}
              onChange={(e) => setCategoryId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            >
              <option value="">Pilih kategori</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{c.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Ringkasan 30 Detik</label>
          <textarea
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light"
            placeholder="Bisa diisi manual atau digenerate oleh AI..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Penjelasan Sederhana</label>
          <textarea
            value={explanation}
            onChange={(e) => setExplanation(e.target.value)}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Dampak ke Publik</label>
          <textarea
            value={impact}
            onChange={(e) => setImpact(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light"
          />
        </div>

        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="bg-primary text-white px-6 py-2.5 rounded-lg hover:bg-primary-dark transition font-medium disabled:opacity-50"
          >
            {loading ? "Menyimpan..." : "Simpan Draft"}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="bg-gray-100 text-gray-700 px-6 py-2.5 rounded-lg hover:bg-gray-200 transition font-medium"
          >
            Batal
          </button>
        </div>
      </form>
    </div>
  );
}