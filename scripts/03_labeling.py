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
    
    # List kata positif dan negatif sederhana
    positive_words = ['enak', 'mantap', 'bagus', 'keren', 'suka', 'puas', 'cepat', 'ramah', 'lezat', 'murah', 'bersih', 'rekomendasi', 'terbaik', 'oke', 'sip', 'kren', 'good', 'worth', 'nyaman']
    negative_words = ['jelek', 'buruk', 'kecewa', 'lama', 'kotor', 'mahal', 'kurang', 'lambat', 'keras', 'asin', 'pahit', 'basi', 'parah', 'payah', 'bau', 'nyamuk', 'kacau', 'bad', 'lelet']
    
    def label_sentiment(row):
        rating = row['rating']
        text = str(row['teks_komentar']).lower()
        
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        
        text_sentiment = 'netral'
        if pos_count > neg_count:
            text_sentiment = 'positif'
        elif neg_count > pos_count:
            text_sentiment = 'negatif'
            
        # Kombinasi rating dan teks
        if rating >= 4:
            if text_sentiment == 'negatif':
                return 'netral'
            return 'positif'
        elif rating <= 2:
            if text_sentiment == 'positif':
                return 'netral'
            return 'negatif'
        else: # rating 3
            return text_sentiment
            
    # Beri label sentimen
    log.info("📊 Memproses pelabelan dengan 3 kelas (positif, negatif, netral) menggunakan rating dan teks komentar...")
    filtered_df = df.copy()
    filtered_df['sentimen'] = filtered_df.apply(label_sentiment, axis=1)
    
    # Hapus baris yang mungkin None (safety check)
    final_df = filtered_df.dropna(subset=['sentimen']).copy()
    
    # Tampilkan statistik
    stats = final_df['sentimen'].value_counts()
    log.info("========================================")
    log.info("📈 DISTRIBUSI SENTIMEN (3 KELAS)")
    log.info("========================================")
    for sentimen, count in stats.items():
        percentage = (count / len(final_df)) * 100
        log.info(f"  - {str(sentimen).upper()}: {count} ulasan ({percentage:.1f}%)")
    log.info("========================================")
        
    # Simpan data yang sudah dilabeli
    final_df.to_csv(OUTPUT_FILE, index=False)
    log.info(f"💾 Data pelabelan berhasil disimpan di: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
