import Link from "next/link";
import { PolicyListItem, STATUS_LABELS } from "@/lib/api";
import { StatusBadge, CategoryBadge } from "./layout";

interface PolicyCardProps {
  policy: PolicyListItem;
}

export function PolicyCard({ policy }: PolicyCardProps) {
  return (
    <Link href={`/policy/${policy.slug}`} className="block group">
      <article className="bg-white rounded-xl border border-gray-200 p-5 hover:border-primary-light hover:shadow-md transition-all">
        <div className="flex items-center gap-2 mb-3">
          <StatusBadge status={policy.status} />
          {policy.primary_category && (
            <CategoryBadge name={policy.primary_category.name} />
          )}
        </div>
        <h2 className="text-lg font-semibold text-gray-900 group-hover:text-primary mb-2 line-clamp-2">
          {policy.title}
        </h2>
        {policy.summary_30sec && (
          <p className="text-sm text-gray-600 line-clamp-3 mb-3">
            {policy.summary_30sec}
          </p>
        )}
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <time>
            {policy.published_at
              ? new Date(policy.published_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })
              : new Date(policy.updated_at).toLocaleDateString("id-ID", { day: "numeric", month: "long", year: "numeric" })}
          </time>
        </div>
      </article>
    </Link>
  );
}

interface PolicyListProps {
  policies: PolicyListItem[];
  emptyMessage?: string;
}

export function PolicyList({ policies, emptyMessage = "Belum ada kebijakan." }: PolicyListProps) {
  if (!policies.length) {
    return <p className="text-center text-gray-500 py-12">{emptyMessage}</p>;
  }
  return (
    <div className="grid gap-4">
      {policies.map((p) => (
        <PolicyCard key={p.id} policy={p} />
      ))}
    </div>
  );
}