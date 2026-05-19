"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { STATUS_LABELS } from "@/lib/api";

const CATEGORIES = [
  { slug: "", name: "Semua" },
  { slug: "ekonomi", name: "Ekonomi" },
  { slug: "pajak", name: "Pajak" },
  { slug: "umkm", name: "UMKM" },
  { slug: "tenaga-kerja", name: "Tenaga Kerja" },
  { slug: "pendidikan", name: "Pendidikan" },
  { slug: "kesehatan", name: "Kesehatan" },
  { slug: "digital-teknologi", name: "Digital & Teknologi" },
  { slug: "infrastruktur", name: "Infrastruktur" },
  { slug: "hukum", name: "Hukum" },
];

const STATUSES = [
  { value: "", name: "Semua Status" },
  ...Object.entries(STATUS_LABELS).map(([value, name]) => ({ value, name })),
];

export function FilterBar() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const currentCategory = searchParams.get("category") || "";
  const currentStatus = searchParams.get("status") || "";

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    router.push(`?${params.toString()}`);
  };

  return (
    <div className="flex flex-wrap gap-3 items-center">
      <select
        value={currentCategory}
        onChange={(e) => updateFilter("category", e.target.value)}
        className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
      >
        {CATEGORIES.map((c) => (
          <option key={c.slug} value={c.slug}>{c.name}</option>
        ))}
      </select>
      <select
        value={currentStatus}
        onChange={(e) => updateFilter("status", e.target.value)}
        className="px-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-light"
      >
        {STATUSES.map((s) => (
          <option key={s.value} value={s.value}>{s.name}</option>
        ))}
      </select>
      {(currentCategory || currentStatus) && (
        <button
          onClick={() => router.push("/")}
          className="text-sm text-gray-500 hover:text-gray-700 underline"
        >
          Reset filter
        </button>
      )}
    </div>
  );
}