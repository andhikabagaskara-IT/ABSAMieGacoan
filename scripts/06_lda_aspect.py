"""
06_lda_aspect.py — Ekstraksi Aspek Sentimen Menggunakan LDA
===================================================================
Membaca data teks bersih, melakukan topic modeling dengan Latent Dirichlet Allocation (LDA),
mengevaluasi beberapa variasi jumlah topik menggunakan Davies-Bouldin Index (DBI),
serta mengekstrak keyword untuk setiap topik untuk memetakan aspek bisnis.
"""

import pandas as pd
import numpy as np
import os
import joblib
import logging
import sys
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import davies_bouldin_score

# Konfigurasi stdout untuk log
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", stream=sys.stdout)
log = logging.getLogger(__name__)

# Setup Path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'preprocessed', 'preprocessed_reviews.csv')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
OUTPUT_FILE = os.path.join(BASE_DIR, 'data', 'preprocessed', 'reviews_with_aspects.csv')

# Buat folder jika belum ada (safety)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def main():
    log.info("=== TAHAP 5: EKSTRAKSI ASPEK MENGGUNAKAN LDA ===")
    
    # 1. Load Data
    log.info(f"Membaca dataset preprocessed: {INPUT_FILE}")
    if not os.path.exists(INPUT_FILE):
        log.error(f"File tidak ditemukan: {INPUT_FILE}")
        return
        
    df = pd.read_csv(INPUT_FILE)
    df = df.dropna(subset=['text_preprocessed'])
    
    # Ambil teks saja
    X_text = df['text_preprocessed'].astype(str)
    
    log.info(f"Total ulasan untuk pemodelan topik (Topic Modeling): {len(X_text)}")
    
    # 2. Vectorization (LDA sangat disarankan memakai Term Frequency / CountVectorizer)
    log.info("Mengekstraksi fitur teks (Term Frequency) dengan CountVectorizer...")
    # Menghapus kata yang sangat umum (muncul di 90% dokumen) atau sangat langka (muncul kurang dari 5 dokumen)
    vectorizer = CountVectorizer(max_features=5000, max_df=0.9, min_df=5)
    X_tf = vectorizer.fit_transform(X_text)
    feature_names = vectorizer.get_feature_names_out()
    
    # 3. Eksperimen Jumlah Topik & Evaluasi DBI
    num_topics_list = [3, 4, 5, 6, 7]
    dbi_scores = []
    best_dbi = float('inf') # Metrik DBI: Semakin kecil nilainya, semakin baik clustering/klasifikasi aspeknya
    best_k = 3
    best_lda_model = None
    best_doc_topic_dist = None
    
    log.info("Memulai eksperimen pencarian jumlah topik optimal berdasarkan skor DBI...")
    
    for k in num_topics_list:
        log.info(f"  -> Melatih LDA dengan jumlah aspek (n_components) = {k} ...")
        lda = LatentDirichletAllocation(n_components=k, random_state=42, max_iter=10)
        # Menghasilkan sebaran probabilitas dokumen ke topik
        doc_topic_dist = lda.fit_transform(X_tf)
        
        # Penentuan label cluster untuk perhitungan DBI (topik mana yg peluangnya paling besar di tiap dokumen)
        cluster_labels = np.argmax(doc_topic_dist, axis=1)
        
        # Pastikan ada minimal 2 cluster yang terbentuk agar bisa dihitung DBI-nya
        if len(np.unique(cluster_labels)) > 1:
            # Hitung skor DBI pada fitur matriks doc_topic_dist
            dbi = davies_bouldin_score(doc_topic_dist, cluster_labels)
        else:
            dbi = float('inf')
            
        dbi_scores.append(dbi)
        log.info(f"     Skor DBI (K={k}) : {dbi:.4f}")
        
        # Lacak LDA terbaik
        if dbi < best_dbi:
            best_dbi = dbi
            best_k = k
            best_lda_model = lda
            best_doc_topic_dist = doc_topic_dist
            
    log.info(f"\n✅ PENCARIAN SELESAI: Jumlah Aspek/Topik terbaik adalah {best_k} dengan skor DBI terendah = {best_dbi:.4f}")
    
    # 4. Visualisasi Grafik DBI Evaluasi
    plt.figure(figsize=(8,5))
    plt.plot(num_topics_list, dbi_scores, marker='o', linestyle='dashed', color='b', linewidth=2, markersize=8)
    plt.title('Evaluasi Jumlah Topik (LDA) Menggunakan Davies-Bouldin Index')
    plt.xlabel('Jumlah Topik / Aspek (K)')
    plt.ylabel('Skor DBI (Lebih Rendah = Lebih Baik)')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Beri anotasi titik terbaik
    best_index = num_topics_list.index(best_k)
    plt.annotate(f'Best (K={best_k})', xy=(best_k, best_dbi), xytext=(best_k, best_dbi + 0.1),
                 arrowprops=dict(facecolor='red', shrink=0.05), horizontalalignment='center')
                 
    plot_path = os.path.join(RESULTS_DIR, 'lda_dbi_evaluation.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    log.info(f"Grafik visualisasi evaluasi DBI disimpan di: {plot_path}")
    
    # 5. Ekstraksi Top Keyword per Aspek/Topik
    log.info(f"\nMengekstrak 10 keyword (kata kunci) utama untuk masing-masing dari {best_k} topik:")
    n_top_words = 10
    topics_keywords = {}
    
    report_path = os.path.join(RESULTS_DIR, 'lda_topics_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"=== LAPORAN HASIL LDA (TOPIC MODELING) ===\n")
        f.write(f"Jumlah Aspek/Topik Terbaik : {best_k}\n")
        f.write(f"Skor DBI Terbaik           : {best_dbi:.4f}\n\n")
        f.write("Daftar Keyword Berdasarkan Topik Terbentuk:\n\n")
        
        for topic_idx, topic in enumerate(best_lda_model.components_):
            # Mengurutkan fitur/kata paling relevan
            top_features_ind = topic.argsort()[:-n_top_words - 1:-1]
            top_features = [feature_names[i] for i in top_features_ind]
            
            topics_keywords[f"Topik {topic_idx+1}"] = top_features
            
            # Print & tulis ke file
            topic_desc = f"Topik {topic_idx+1} : " + ", ".join(top_features)
            log.info(f"  {topic_desc}")
            f.write(topic_desc + "\n")
            
        f.write("\n* Catatan untuk Penulis (Mahasiswa):\n")
        f.write("Analis perlu membaca keyword di atas untuk menamai label aspek secara manual.\n")
        f.write("Contoh: Jika Topik 1 berisi 'enak, gurih, pedas', maka Topik 1 merepresentasikan aspek 'RASA'.\n")
        f.write("Jika Topik 2 berisi 'kotor, meja, lalat', maka merepresentasikan 'KEBERSIHAN'.\n")
    
    log.info(f"Laporan detil kata kunci topik diekspor ke: {report_path}")
    
    # 6. Menambahkan Label Topik Dominan ke Data Keseluruhan
    log.info("\nMenyematkan Aspek Prediksi LDA kembali ke dataset ulasan utama...")
    dominant_topic = np.argmax(best_doc_topic_dist, axis=1)
    df['aspek_lda'] = [f"Topik {t+1}" for t in dominant_topic]
    df['probabilitas_aspek'] = np.max(best_doc_topic_dist, axis=1) # Menyimpan seberapa yakin LDA tsb
    
    # Simpan dataset versi baru yang kini sudah memuat sentimen + aspek
    df.to_csv(OUTPUT_FILE, index=False)
    log.info(f"Dataset Master dengan kombinasi Klasifikasi Sentimen & Aspek tersimpan di:\n -> {OUTPUT_FILE}")
    
    # 7. Simpan Model Vectorizer & LDA
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, 'lda_count_vectorizer.pkl'))
    joblib.dump(best_lda_model, os.path.join(MODELS_DIR, 'lda_model.pkl'))
    log.info("Model CountVectorizer dan LDA (Latent Dirichlet Allocation) berhasil disimpan di direktori 'models/'.")
    log.info("✅ Tahap 5 SELESAI KESELURUHANNYA!")

if __name__ == "__main__":
    main()
