import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { Header, Footer } from "@/components/layout";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "KawalKebijakan — Pahami kebijakan pemerintah dalam 30 detik",
  description: "Membantu publik memahami kebijakan pemerintah Indonesia dengan bahasa yang sederhana, netral, dan berbasis sumber.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className={`${geistSans.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}