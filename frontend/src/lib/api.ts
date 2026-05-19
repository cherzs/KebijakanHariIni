const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API Error");
  }
  return res.json();
}

async function fetchAuthAPI<T>(path: string, token: string, options?: RequestInit): Promise<T> {
  return fetchAPI<T>(path, {
    ...options,
    headers: {
      ...options?.headers,
      Authorization: `Bearer ${token}`,
    },
  });
}

export interface Category {
  id: string;
  slug: string;
  name: string;
  description: string | null;
}

export interface Source {
  id: string;
  source_type: string;
  title: string;
  url: string;
  snippet: string | null;
  published_date: string | null;
  site_name: string | null;
}

export interface Timeline {
  id: string;
  date: string;
  title: string;
  description: string | null;
  sort_order: number;
}

export interface PolicyListItem {
  id: string;
  title: string;
  slug: string;
  status: string;
  summary_30sec: string | null;
  primary_category: Category | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PolicyDetail extends PolicyListItem {
  simple_explanation: string | null;
  impact_explanation: string | null;
  categories: Category[];
  timelines: Timeline[];
  sources: Source[];
  published_status: string;
}

export interface PolicyListResponse {
  items: PolicyListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface SearchResponse {
  items: PolicyListItem[];
  total: number;
  query: string;
}

export const STATUS_LABELS: Record<string, string> = {
  wacana: "Wacana",
  draf: "Draf",
  dibahas: "Dibahas",
  disahkan: "Disahkan",
  berlaku: "Berlaku",
  ditunda: "Ditunda",
  dibatalkan: "Dibatalkan",
};

export const STATUS_COLORS: Record<string, string> = {
  wacana: "bg-purple-100 text-purple-800",
  draf: "bg-yellow-100 text-yellow-800",
  dibahas: "bg-blue-100 text-blue-800",
  disahkan: "bg-green-100 text-green-800",
  berlaku: "bg-emerald-100 text-emerald-800",
  ditunda: "bg-red-100 text-red-800",
  dibatalkan: "bg-gray-100 text-gray-800",
};

export { fetchAPI, fetchAuthAPI, API_BASE };