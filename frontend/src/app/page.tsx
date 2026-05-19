import { fetchAPI } from "@/lib/api";
import { PolicyListResponse } from "@/lib/api";
import { PolicyList } from "@/components/policy-card";
import { SearchBar } from "@/components/search-bar";
import { FilterBar } from "@/components/filter-bar";
import { Pagination } from "@/components/pagination";

interface HomePageProps {
  searchParams: Promise<{ page?: string; category?: string; status?: string }>;
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = await searchParams;
  const page = parseInt(params.page || "1");
  const category = params.category || "";
  const status = params.status || "";

  let data: PolicyListResponse;
  try {
    const queryParams = new URLSearchParams();
    queryParams.set("page", page.toString());
    queryParams.set("limit", "20");
    if (category) queryParams.set("category", category);
    if (status) queryParams.set("status", status);
    data = await fetchAPI<PolicyListResponse>(`/policies?${queryParams.toString()}`);
  } catch {
    data = { items: [], total: 0, page: 1, limit: 20, pages: 0 };
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <section className="mb-8 text-center">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Kebijakan pemerintah, dibahasarkan.
        </h1>
        <p className="text-gray-600 text-lg mb-6">
          Baca, pahami, dan pantau kebijakan pemerintah Indonesia — tanpa jargon.
        </p>
        <div className="max-w-xl mx-auto">
          <SearchBar />
        </div>
      </section>

      <section className="mb-6">
        <FilterBar />
      </section>

      <section>
        <PolicyList policies={data.items} emptyMessage="Belum ada kebijakan yang dipublikasikan." />
      </section>

      {data.pages > 1 && (
        <Pagination
          pages={data.pages}
          currentPage={data.page}
          basePath="/"
        />
      )}
    </div>
  );
}