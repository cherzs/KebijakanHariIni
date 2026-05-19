interface PaginationProps {
  pages: number;
  currentPage: number;
  basePath?: string;
}

export function Pagination({ pages, currentPage, basePath = "/" }: PaginationProps) {
  if (pages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2 mt-8">
      {Array.from({ length: pages }, (_, i) => i + 1).map((page) => (
        <a
          key={page}
          href={`${basePath}?page=${page}`}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
            page === currentPage
              ? "bg-primary text-white"
              : "bg-white border border-gray-200 text-gray-600 hover:bg-gray-50"
          }`}
        >
          {page}
        </a>
      ))}
    </div>
  );
}