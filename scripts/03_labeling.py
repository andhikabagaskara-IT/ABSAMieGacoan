"""
03_labeling.py — Pelabelan Sentimen Otomatis
================================================================
Membaca data dari data/combined/all_reviews.csv dan memberikan label 
sentimen berdasarkan rating (1-2 = negatif, 4-5 = positif, 3 = dibuang).
"""

import os
import pandas as pd
import logging
import sys

# Konfigurasi stdout agar mendukung UTF-8 (menghindari UnicodeEncodeError di Windows)
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMBINED_DIR = os.path.join(BASE_DIR, "data", "combined")
LABELED_DIR = os.path.join(BASE_DIR, "data", "labeled")

INPUT_FILE = os.path.join(COMBINED_DIR, "all_reviews.csv")
OUTPUT_FILE = os.path.join(LABELED_DIR, "labeled_reviews.csv")

def main():
    log.info("🚀 Mulai proses pelabelan sentimen...")
    
    os.makedirs(LABELED_DIR, exist_ok=True)
    
    if not os.path.exists(INPUT_FILE):
        log.error(f"❌ File input tidak ditemukan: {INPUT_FILE}")
        log.info("Silakan jalankan scripts/02_quality_check.py terlebih dahulu.")
        return
        
    try:
        df = pd.read_csv(INPUT_FILE)
    except Exception as e:
        log.error(f"❌ Gagal membaca file input: {e}")
        return
        
    log.info(f"✅ Berhasil memuat {len(df)} ulasan dari data gabungan.")
    
    # Validasi tipe data rating
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    
    # Filter rating (buang rating 3)
    filtered_df = df[df['rating'] != 3].copy()
    dropped_count = len(df) - len(filtered_df)
    log.info(f"🧹 Membuang {dropped_count} ulasan dengan rating 3 (ambigu).")
    log.info(f"📊 Total ulasan yang akan dilabeli: {len(filtered_df)}")
    
    # Beri label sentimen
    # Rating 1-2 = negatif, 4-5 = positif
    def label_sentiment(rating):
        if rating >= 4:
            return 'positif'
        elif rating <= 2:
            return 'negatif'
        return None
        
    filtered_df['sentimen'] = filtered_df['rating'].apply(label_sentiment)
    
    # Hapus baris yang mungkin None (safety check)
    final_df = filtered_df.dropna(subset=['sentimen']).copy()
    
    # Tampilkan statistik
    stats = final_df['sentimen'].value_counts()
    log.info("========================================")
    log.info("📈 DISTRIBUSI SENTIMEN")
    log.info("========================================")
    for sentimen, count in stats.items():
        percentage = (count / len(final_df)) * 100
        log.info(f"  - {sentimen.upper()}: {count} ulasan ({percentage:.1f}%)")
    log.info("========================================")
        
    # Simpan data yang sudah dilabeli
    final_df.to_csv(OUTPUT_FILE, index=False)
    log.info(f"💾 Data pelabelan berhasil disimpan di: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
