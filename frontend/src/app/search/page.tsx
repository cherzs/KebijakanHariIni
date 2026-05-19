import { fetchAPI } from "@/lib/api";
import { SearchResponse } from "@/lib/api";
import { PolicyList } from "@/components/policy-card";
import { SearchBar } from "@/components/search-bar";
import { Pagination } from "@/components/pagination";

interface SearchPageProps {
  searchParams: Promise<{ q?: string; page?: string }>;
}

export default async function SearchPage({ searchParams }: SearchPageProps) {
  const params = await searchParams;
  const query = params.q || "";
  const page = parseInt(params.page || "1");

  let data: SearchResponse = { items: [], total: 0, query };
  if (query) {
    try {
      data = await fetchAPI<SearchResponse>(`/policies/search?q=${encodeURIComponent(query)}&page=${page}`);
    } catch {
      // keep defaults
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Cari Kebijakan</h1>
      <div className="max-w-xl mb-8">
        <SearchBar />
      </div>

      {query && (
        <p className="text-sm text-gray-500 mb-4">
          {data.total} hasil untuk &quot;{query}&quot;
        </p>
      )}

      <PolicyList
        policies={data.items}
        emptyMessage={query ? "Tidak ada kebijakan yang cocok dengan pencarian Anda." : "Ketik kata kunci untuk mencari kebijakan."}
      />

      {data.total > 20 && (
        <Pagination pages={Math.ceil(data.total / 20)} currentPage={page} basePath={`/search?q=${encodeURIComponent(query)}`} />
      )}
    </div>
  );
}