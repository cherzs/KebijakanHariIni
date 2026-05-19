export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Tentang KawalKebijakan</h1>

      <div className="space-y-6 text-gray-700 leading-relaxed">
        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Apa itu KawalKebijakan?</h2>
          <p>
            KawalKebijakan adalah situs yang membantu masyarakat Indonesia memahami kebijakan pemerintah dengan bahasa yang sederhana, netral, dan berbasis sumber. Kami bukan portal berita — kami adalah policy tracker.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Mengapa ini penting?</h2>
          <p>
            Informasi kebijakan pemerintah tersebar di puluhan situs resmi. Dokumen hukum ditulis dalam bahasa yang sulit dipahami. Media hanya liput saat sudah jadi berita. KawalKebijakan mengumpulkan, meringkas, dan mengstrukturkan info ini agar siapa pun bisa memahami dalam 30 detik.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Prinsip kami</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Bersumber:</strong> Setiap klaim bisa ditelusuri ke sumber asli.</li>
            <li><strong>Netral:</strong> Kami tidak mengambil posisi pro/kontra. Kami menyajikan fakta.</li>
            <li><strong>Mudah dipahami:</strong> Bahasa sehari-hari, bukan bahasa hukum.</li>
            <li><strong>Independen:</strong> Situs ini tidak berafiliasi dengan partai atau manusia politik manapun.</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Sumber data</h2>
          <p>
            Kami mengumpulkan data dari sumber resmi pemerintah (JDIH Setneg, JDIH BPK, DPR/Prolegnas, website kementerian, Sekretariat Kabinet) dan berita dari media terpercaya di Indonesia.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Disclaimer</h2>
          <p className="text-sm text-gray-500">
            Ringkasan kebijakan di situs ini dibuat oleh AI dan direview oleh tim editorial. Konten ini bukan pengganti dokumen hukum resmi. Selalu merujuk ke sumber asli untuk keperluan hukum.
          </p>
        </section>
      </div>
    </div>
  );
}