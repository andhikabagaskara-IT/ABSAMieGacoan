"""
07_export_dashboard.py — Ekspor Data Analisis untuk Dashboard VueJS
===================================================================
Membaca dataset hasil final (reviews_with_aspects.csv) yang memuat teks asli, 
sentimen, dan aspek LDA, kemudian mengkalkulasi berbagai statistik untuk divisualisasikan,
serta menyimpannya dalam format JSON untuk dikonsumsi frontend VueJS.
"""

import pandas as pd
import os
import json
import logging
import sys

# Konfigurasi stdout
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'preprocessed', 'reviews_with_aspects.csv')
EXPORT_DIR = os.path.join(BASE_DIR, 'data', 'export')

# Kita buat folder export tersendiri yang nantinya akan di-copy ke VueJS
os.makedirs(EXPORT_DIR, exist_ok=True)

def main():
    log.info("=== TAHAP 6: EKSPOR DATA AGREGASI UNTUK DASHBOARD ===")
    
    if not os.path.exists(INPUT_FILE):
        log.error(f"File dataset final tidak ditemukan: {INPUT_FILE}")
        log.info("Pastikan tahap pemodelan LDA (scripts/06_lda_aspect.py) telah dijalankan.")
        return
        
    log.info(f"Membaca dataset final yang memiliki label Sentimen & Aspek: {INPUT_FILE}")
    # Menggunakan parameter low_memory=False jika ukuran file besar
    df = pd.read_csv(INPUT_FILE, low_memory=False)
    
    # Menyiapkan payload dictionary JSON
    export_data = {}
    
    # 1. Total Keseluruhan Data Ulasan
    export_data['total_reviews'] = len(df)
    log.info(f" -> Total baris diproses: {export_data['total_reviews']}")
    
    # 2. Distribusi Sentimen Keseluruhan
    if 'sentimen' in df.columns:
        sentiment_counts = df['sentimen'].value_counts().to_dict()
        export_data['sentiment_distribution'] = sentiment_counts
    
    # 3. Distribusi Aspek Keseluruhan (Dari LDA)
    if 'aspek_lda' in df.columns:
        aspect_counts = df['aspek_lda'].value_counts().to_dict()
        export_data['aspect_distribution'] = aspect_counts
    
    # 4. Agregasi Berdasarkan Cabang (jika kolom ada)
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
            
    # 5. Export Sampel Data Detail untuk Tabel "Data Explorer" di Dashboard Vue
    # Mengirim seluruh 60ribu baris ke JSON akan membuat ukuran file membengkak dan website lemot (nge-lag).
    # Oleh karena itu, kita berikan sampel representatif untuk keperluan tabel (misal: 1500 terbaru/acak).
    log.info(" -> Mengambil 1500 sampel ulasan representatif untuk tabel explorer UI...")
    sample_size = min(1500, len(df))
    # Buang kolom yang tidak perlu ditampilkan di tabel frontend (seperti text_preprocessed, dsb)
    display_columns = [col for col in ['nama_cabang', 'nama_pelanggan', 'tanggal_ulasan', 'rating', 'teks_komentar', 'sentimen', 'aspek_lda'] if col in df.columns]
    
    sample_df = df.sample(sample_size, random_state=42)[display_columns]
    # Handle masalah format data kosong/nan
    sample_df = sample_df.fillna("Tidak Ada Data")
    export_data['sample_reviews'] = sample_df.to_dict(orient='records')
    
    # 6. Simpan Semuanya ke JSON
    output_path = os.path.join(EXPORT_DIR, 'dashboard_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        # ensure_ascii=False sangat penting agar karakter bahasa indonesia (dan emoji jika masih tersisa) tidak rusak
        json.dump(export_data, f, ensure_ascii=False, indent=4)
        
    log.info(f"Semua agregasi JSON berhasil diekspor ke: {output_path}")
    log.info("File inilah yang akan digunakan oleh VueJS untuk merender Chart/Grafik.")
    log.info("✅ TAHAP EXPORT (TAHAP 6) SELESAI!")

if __name__ == "__main__":
    main()
