"""
07_export_dashboard.py — Ekspor Data Analisis untuk Dashboard VueJS
===================================================================
Membaca dataset hasil final (reviews_with_aspects.csv) yang memuat teks asli,
sentimen, dan aspek LDA, kemudian mengkalkulasi berbagai statistik untuk divisualisasikan,
serta menyimpannya dalam format JSON untuk dikonsumsi frontend VueJS.

Data yang diekspor meliputi:
  - Statistik sentimen keseluruhan & per cabang
  - Distribusi aspek keseluruhan & per cabang
  - Hasil K-Fold Cross-Validation (SVM & NB)
  - Hasil LDA (DBI, keywords per topik)
  - Analisis aspek per sentimen
  - Sampel ulasan untuk Data Explorer
"""

import pandas as pd
import os
import json
import logging
import sys

# Konfigurasi stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'preprocessed', 'reviews_with_aspects.csv')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
EXPORT_DIR = os.path.join(BASE_DIR, 'data', 'export')

# Kita buat folder export tersendiri yang nantinya akan di-copy ke VueJS
os.makedirs(EXPORT_DIR, exist_ok=True)


def load_json_safe(filepath):
    """Memuat file JSON dengan penanganan error."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            log.warning(f"Gagal memuat {filepath}: {e}")
    return None


def main():
    log.info("=" * 70)
    log.info("  TAHAP 6: EKSPOR DATA AGREGASI UNTUK DASHBOARD")
    log.info("=" * 70)

    if not os.path.exists(INPUT_FILE):
        log.error(f"File dataset final tidak ditemukan: {INPUT_FILE}")
        log.info("Pastikan tahap pemodelan LDA (scripts/06_lda_aspect.py) telah dijalankan.")
        return

    log.info(f"Membaca dataset final yang memiliki label Sentimen & Aspek: {INPUT_FILE}")
    # Menggunakan parameter low_memory=False jika ukuran file besar
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    # Menyiapkan payload dictionary JSON
    export_data = {}

    # ─── 1. Total Keseluruhan Data Ulasan ───────────────────────────────────
    export_data['total_reviews'] = len(df)
    log.info(f" -> Total baris diproses: {export_data['total_reviews']}")

    # ─── 2. Distribusi Sentimen Keseluruhan ─────────────────────────────────
    if 'sentimen' in df.columns:
        sentiment_counts = df['sentimen'].value_counts().to_dict()
        export_data['sentiment_distribution'] = sentiment_counts
        log.info(f" -> Distribusi sentimen: {sentiment_counts}")

    # ─── 3. Distribusi Aspek Keseluruhan (Dari LDA) ────────────────────────
    if 'aspek_lda' in df.columns:
        aspect_counts = df['aspek_lda'].value_counts().to_dict()
        export_data['aspect_distribution'] = aspect_counts
        log.info(f" -> Distribusi aspek: {aspect_counts}")

    # ─── 4. Agregasi Berdasarkan Cabang ─────────────────────────────────────
    if 'nama_cabang' in df.columns:
        log.info(" -> Melakukan agregasi data cabang...")

        # Sentimen per cabang
        if 'sentimen' in df.columns:
            branch_sentiment = df.groupby(['nama_cabang', 'sentimen']).size().unstack(fill_value=0)
            export_data['branch_sentiment'] = branch_sentiment.to_dict(orient='index')

        # Aspek per cabang
        if 'aspek_lda' in df.columns:
            branch_aspect = df.groupby(['nama_cabang', 'aspek_lda']).size().unstack(fill_value=0)
            export_data['branch_aspect'] = branch_aspect.to_dict(orient='index')

    # ─── 5. Aspek per Sentimen (Cross-tabulation) ──────────────────────────
    if 'sentimen' in df.columns and 'aspek_lda' in df.columns:
        log.info(" -> Mengkalkulasi cross-tabulation Aspek × Sentimen...")
        aspect_sentiment_cross = {}
        for sentiment in df['sentimen'].unique():
            df_sent = df[df['sentimen'] == sentiment]
            aspect_sentiment_cross[sentiment] = df_sent['aspek_lda'].value_counts().to_dict()
        export_data['aspect_sentiment_cross'] = aspect_sentiment_cross

    # ─── 6. Hasil K-Fold Cross-Validation (dari file JSON) ─────────────────
    kfold_json_path = os.path.join(RESULTS_DIR, 'kfold_results.json')
    kfold_results = load_json_safe(kfold_json_path)
    if kfold_results:
        export_data['kfold_results'] = kfold_results
        log.info(f" -> Data K-Fold CV dimuat dari: {kfold_json_path}")
    else:
        log.warning(f" -> File K-Fold results tidak ditemukan: {kfold_json_path}")

    # ─── 7. Hasil LDA (dari file JSON) ─────────────────────────────────────
    lda_json_path = os.path.join(RESULTS_DIR, 'lda_results.json')
    lda_results = load_json_safe(lda_json_path)
    if lda_results:
        export_data['lda_results'] = lda_results
        log.info(f" -> Data LDA dimuat dari: {lda_json_path}")
    else:
        log.warning(f" -> File LDA results tidak ditemukan: {lda_json_path}")

    # ─── 8. Export Sampel Data Detail untuk Tabel "Data Explorer" ──────────
    log.info(" -> Mengambil 1500 sampel ulasan representatif untuk tabel explorer UI...")
    sample_size = min(1500, len(df))
    # Buang kolom yang tidak perlu ditampilkan di tabel frontend (seperti text_preprocessed, dsb)
    display_columns = [col for col in [
        'nama_cabang', 'nama_pelanggan', 'tanggal_ulasan', 'rating',
        'teks_komentar', 'sentimen', 'aspek_lda'
    ] if col in df.columns]

    sample_df = df.sample(sample_size, random_state=42)[display_columns]
    # Handle masalah format data kosong/nan
    sample_df = sample_df.fillna("Tidak Ada Data")
    export_data['sample_reviews'] = sample_df.to_dict(orient='records')

    # ─── 9. Simpan Semuanya ke JSON ────────────────────────────────────────
    output_path = os.path.join(EXPORT_DIR, 'dashboard_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False sangat penting agar karakter bahasa indonesia (dan emoji jika masih tersisa) tidak rusak
        json.dump(export_data, f, ensure_ascii=False, indent=4)

    file_size_kb = os.path.getsize(output_path) / 1024
    log.info(f"\nSemua agregasi JSON berhasil diekspor ke: {output_path}")
    log.info(f"Ukuran file: {file_size_kb:.1f} KB")
    log.info("File inilah yang akan digunakan oleh VueJS untuk merender Chart/Grafik.")
    log.info("✅ TAHAP EXPORT (TAHAP 6) SELESAI!")


if __name__ == "__main__":
    main()
