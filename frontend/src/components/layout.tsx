import Link from "next/link";
import { STATUS_LABELS, STATUS_COLORS } from "@/lib/api";

interface StatusBadgeProps {
  status: string;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = STATUS_COLORS[status] || "bg-gray-100 text-gray-800";
  const label = STATUS_LABELS[status] || status;
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
      {label}
    </span>
  );
}

interface CategoryBadgeProps {
  name: string;
  slug?: string;
}

export function CategoryBadge({ name }: CategoryBadgeProps) {
  return (
    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
      {name}
    </span>
  );
}

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">KK</span>
          </div>
          <span className="font-bold text-lg text-gray-900">KawalKebijakan</span>
        </Link>
        <nav className="flex items-center gap-6">
          <Link href="/" className="text-sm text-gray-600 hover:text-gray-900">Kebijakan</Link>
          <Link href="/about" className="text-sm text-gray-600 hover:text-gray-900">Tentang</Link>
        </nav>
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-16">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-bold text-gray-900 mb-2">KawalKebijakan</h3>
            <p className="text-sm text-gray-500">
              Membantu publik memahami kebijakan pemerintah tanpa harus membaca puluhan berita dan dokumen hukum.
            </p>
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-2">Kategori</h3>
            <div className="flex flex-col gap-1 text-sm text-gray-500">
              <span>Ekonomi, Pajak, UMKM</span>
              <span>Tenaga Kerja, Pendidikan</span>
              <span>Kesehatan, Digital, Hukum</span>
            </div>
          </div>
          <div>
            <h3 className="font-bold text-gray-900 mb-2">Info</h3>
            <p className="text-sm text-gray-500">
              Situs ini tidak berafiliasi dengan partai atau manusia politik manapun. Semua konten bersumber dan netral.
            </p>
          </div>
        </div>
        <div className="mt-8 pt-4 border-t border-gray-100 text-center text-xs text-gray-400">
          &copy; {new Date().getFullYear()} KawalKebijakan. Dibuat untuk publik Indonesia.
        </div>
      </div>
    </footer>
  );
}