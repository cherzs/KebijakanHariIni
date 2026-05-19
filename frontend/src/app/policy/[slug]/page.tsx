import { fetchAPI } from "@/lib/api";
import { PolicyDetail } from "@/lib/api";
import { PolicyDetailView } from "@/components/policy-detail";
import Link from "next/link";
import { notFound } from "next/navigation";

interface PolicyPageProps {
  params: Promise<{ slug: string }>;
}

export default async function PolicyPage({ params }: PolicyPageProps) {
  const { slug } = await params;
  let policy: PolicyDetail;
  try {
    policy = await fetchAPI<PolicyDetail>(`/policies/${slug}`);
  } catch {
    notFound();
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Link href="/" className="text-sm text-gray-500 hover:text-gray-700 mb-6 inline-block">
        &larr; Kembali ke daftar kebijakan
      </Link>
      <PolicyDetailView policy={policy} />
    </div>
  );
}