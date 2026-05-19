"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { API_BASE } from "@/lib/api";

interface Policy {
  id: string;
  title: string;
  slug: string;
  status: string;
  published_status: string;
  updated_at: string;
}

export default function AdminDashboardPage() {
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/admin/login");
      return;
    }
    fetchPolicies(token);
  }, [router]);

  const fetchPolicies = async (token: string) => {
    try {
      const res = await fetch(`${API_BASE}/admin/policies?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.status === 401) {
        localStorage.removeItem("token");
        router.push("/admin/login");
        return;
      }
      const data = await res.json();
      setPolicies(data.items || []);
    } catch {
      // handle error
    } finally {
      setLoading(false);
    }
  };

  const statusColor = (s: string) => {
    const colors: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      published: "bg-green-100 text-green-800",
      archived: "bg-yellow-100 text-yellow-800",
    };
    return colors[s] || "bg-gray-100 text-gray-800";
  };

  const policyStatusColor = (s: string) => {
    const colors: Record<string, string> = {
      wacana: "bg-purple-100 text-purple-800",
      draf: "bg-yellow-100 text-yellow-800",
      dibahas: "bg-blue-100 text-blue-800",
      disahkan: "bg-green-100 text-green-800",
      berlaku: "bg-emerald-100 text-emerald-800",
      ditunda: "bg-red-100 text-red-800",
      dibatalkan: "bg-gray-100 text-gray-800",
    };
    return colors[s] || "bg-gray-100 text-gray-800";
  };

  const STATUS_LABELS: Record<string, string> = {
    wacana: "Wacana", draf: "Draf", dibahas: "Dibahas",
    disahkan: "Disahkan", berlaku: "Berlaku", ditunda: "Ditunda", dibatalkan: "Dibatalkan",
  };

  const PUB_LABELS: Record<string, string> = { draft: "Draft", published: "Published", archived: "Archived" };

  if (loading) return <div className="p-8 text-center text-gray-500">Loading...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <Link
          href="/admin/policies/new"
          className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-dark transition text-sm font-medium"
        >
          + Tambah Kebijakan
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Judul</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Status</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Publikasi</th>
              <th className="px-4 py-3 text-left font-medium text-gray-500">Update</th>
              <th className="px-4 py-3 text-right font-medium text-gray-500">Aksi</th>
            </tr>
          </thead>
          <tbody>
            {policies.length === 0 ? (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Belum ada kebijakan.</td></tr>
            ) : (
              policies.map((p) => (
                <tr key={p.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-900 max-w-md truncate">{p.title}</td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${policyStatusColor(p.status)}`}>
                      {STATUS_LABELS[p.status] || p.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${statusColor(p.published_status)}`}>
                      {PUB_LABELS[p.published_status] || p.published_status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500">
                    {new Date(p.updated_at).toLocaleDateString("id-ID")}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/admin/policies/${p.id}/edit`} className="text-primary hover:underline text-sm">
                      Edit
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}