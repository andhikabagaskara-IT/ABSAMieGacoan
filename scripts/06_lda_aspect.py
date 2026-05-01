"""
06_lda_aspect.py — Ekstraksi Aspek Sentimen Menggunakan LDA
===================================================================
Membaca data teks bersih yang sudah diklasifikasikan sentimennya,
melakukan topic modeling dengan Latent Dirichlet Allocation (LDA),
mengevaluasi beberapa variasi jumlah topik menggunakan Davies-Bouldin Index (DBI),
serta mengekstrak keyword untuk setiap topik untuk memetakan aspek bisnis.

Analisis LDA dilakukan di akhir pipeline (setelah klasifikasi) untuk:
  - Membedah topik/aspek apa yang sering muncul pada sentimen positif atau negatif
  - Menghasilkan insight per aspek per sentimen
"""

import pandas as pd
import numpy as np
import os
import joblib
import logging
import sys
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics import davies_bouldin_score
from wordcloud import WordCloud

# Konfigurasi stdout untuk log
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
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
    log.info("=" * 70)
    log.info("  TAHAP 5: EKSTRAKSI ASPEK MENGGUNAKAN LDA")
    log.info("=" * 70)

    # ─── 1. Load Data ───────────────────────────────────────────────────────
    log.info(f"Membaca dataset preprocessed: {INPUT_FILE}")
    if not os.path.exists(INPUT_FILE):
        log.error(f"File tidak ditemukan: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    df = df.dropna(subset=['text_preprocessed'])

    # Ambil teks saja
    X_text = df['text_preprocessed'].astype(str)

    log.info(f"Total ulasan untuk pemodelan topik (Topic Modeling): {len(X_text)}")

    # ─── 2. Vectorization (CountVectorizer — disarankan untuk LDA) ──────────
    log.info("Mengekstraksi fitur teks (Term Frequency) dengan CountVectorizer...")
    # Menghapus kata yang sangat umum (muncul di 90% dokumen) atau sangat langka (muncul kurang dari 5 dokumen)
    vectorizer = CountVectorizer(max_features=5000, max_df=0.9, min_df=5)
    X_tf = vectorizer.fit_transform(X_text)
    feature_names = vectorizer.get_feature_names_out()

    # ─── 3. Eksperimen Jumlah Topik & Evaluasi DBI ──────────────────────────
    # Rentang pencarian topik yang lebih luas — LDA akan memilih K optimal secara otomatis
    num_topics_list = [3, 4, 5, 6, 7, 8, 9, 10]
    dbi_scores = []
    best_dbi = float('inf')  # Metrik DBI: Semakin kecil nilainya, semakin baik clustering/klasifikasi aspeknya
    best_k = 3
    best_lda_model = None
    best_doc_topic_dist = None

    log.info("Memulai eksperimen pencarian jumlah topik optimal berdasarkan skor DBI...")
    log.info(f"Rentang K yang diuji: {num_topics_list}")

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
    log.info(f"   (LDA TIDAK dipaksa ke jumlah topik tertentu — hasilnya murni dari evaluasi DBI)")

    # ─── 4. Visualisasi Grafik DBI Evaluasi ─────────────────────────────────
    plt.figure(figsize=(10, 6))
    plt.plot(num_topics_list, dbi_scores, marker='o', linestyle='dashed', color='b', linewidth=2, markersize=8)
    plt.title('Evaluasi Jumlah Topik (LDA) Menggunakan Davies-Bouldin Index')
    plt.xlabel('Jumlah Topik / Aspek (K)')
    plt.ylabel('Skor DBI (Lebih Rendah = Lebih Baik)')
    plt.xticks(num_topics_list)
    plt.grid(True, linestyle='--', alpha=0.7)

    # Beri anotasi titik terbaik
    best_index = num_topics_list.index(best_k)
    plt.annotate(f'Best (K={best_k})', xy=(best_k, best_dbi), xytext=(best_k, best_dbi + 0.1),
                 arrowprops=dict(facecolor='red', shrink=0.05), horizontalalignment='center')

    plot_path = os.path.join(RESULTS_DIR, 'lda_dbi_evaluation.png')
    plt.savefig(plot_path, dpi=300)
    plt.close()
    log.info(f"Grafik visualisasi evaluasi DBI disimpan di: {plot_path}")

    # ─── 5. Ekstraksi Top Keyword per Aspek/Topik & WordCloud ───────────────
    log.info(f"\nMengekstrak 10 keyword (kata kunci) utama untuk masing-masing dari {best_k} topik:")
    n_top_words = 10
    topics_keywords = {}
    
    # Direktori dashboard/public
    dashboard_public_dir = os.path.join(BASE_DIR, 'dashboard', 'public')
    os.makedirs(dashboard_public_dir, exist_ok=True)

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
            
            # Buat WordCloud
            wc = WordCloud(width=800, height=400, background_color='white', colormap='viridis', max_words=20)
            # Buat string frequencies dari score
            word_freq = {feature_names[i]: topic[i] for i in top_features_ind}
            wc.generate_from_frequencies(word_freq)
            wc_path = os.path.join(dashboard_public_dir, f'wordcloud_topik_{topic_idx+1}.png')
            wc.to_file(wc_path)
            log.info(f"    WordCloud disimpan ke: {wc_path}")

        f.write("\n* Catatan untuk Penulis (Mahasiswa):\n")
        f.write("Analis perlu membaca keyword di atas untuk menamai label aspek secara manual.\n")
        f.write("Contoh: Jika Topik 1 berisi 'enak, gurih, pedas', maka Topik 1 merepresentasikan aspek 'RASA'.\n")
        f.write("Jika Topik 2 berisi 'kotor, meja, lalat', maka merepresentasikan 'KEBERSIHAN'.\n")

    log.info(f"Laporan detil kata kunci topik diekspor ke: {report_path}")

    # ─── 6. Menambahkan Label Topik Dominan ke Data Keseluruhan ─────────────
    log.info("\nMenyematkan Aspek Prediksi LDA kembali ke dataset ulasan utama...")
    dominant_topic = np.argmax(best_doc_topic_dist, axis=1)
    df['aspek_lda'] = [f"Topik {t+1}" for t in dominant_topic]
    df['probabilitas_aspek'] = np.max(best_doc_topic_dist, axis=1)  # Menyimpan seberapa yakin LDA tsb

    # ─── 7. Analisis Aspek per Sentimen ─────────────────────────────────────
    log.info("\nMenganalisis distribusi aspek berdasarkan sentimen...")

    if 'sentimen' in df.columns:
        aspect_sentiment_path = os.path.join(RESULTS_DIR, 'aspect_sentiment_analysis.txt')
        with open(aspect_sentiment_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("  ANALISIS ASPEK PER SENTIMEN (LDA + Klasifikasi)\n")
            f.write("=" * 70 + "\n\n")

            for sentiment in df['sentimen'].unique():
                df_sent = df[df['sentimen'] == sentiment]
                f.write(f"\n{'─'*50}\n")
                f.write(f"  Sentimen: {sentiment.upper()} ({len(df_sent)} ulasan)\n")
                f.write(f"{'─'*50}\n")

                aspect_counts = df_sent['aspek_lda'].value_counts()
                for aspect, count in aspect_counts.items():
                    pct = count / len(df_sent) * 100
                    keywords = topics_keywords.get(aspect, [])
                    f.write(f"  {aspect}: {count} ulasan ({pct:.1f}%)\n")
                    f.write(f"    Keywords: {', '.join(keywords)}\n")

                log.info(f"  Sentimen {sentiment.upper()}: {len(df_sent)} ulasan")
                for aspect, count in aspect_counts.items():
                    log.info(f"    {aspect}: {count} ({count/len(df_sent)*100:.1f}%)")

        log.info(f"Analisis aspek per sentimen disimpan di: {aspect_sentiment_path}")

    # ─── 8. Simpan Dataset Final ────────────────────────────────────────────
    df.to_csv(OUTPUT_FILE, index=False)
    log.info(f"Dataset Master dengan kombinasi Klasifikasi Sentimen & Aspek tersimpan di:\n -> {OUTPUT_FILE}")

    # ─── 9. Simpan Model Vectorizer & LDA ───────────────────────────────────
    joblib.dump(vectorizer, os.path.join(MODELS_DIR, 'lda_count_vectorizer.pkl'))
    joblib.dump(best_lda_model, os.path.join(MODELS_DIR, 'lda_model.pkl'))
    log.info("Model CountVectorizer dan LDA (Latent Dirichlet Allocation) berhasil disimpan di direktori 'models/'.")

    # ─── 10. Export Data LDA ke JSON (untuk Dashboard) ──────────────────────
    lda_results = {
        'best_k': int(best_k),
        'best_dbi': float(best_dbi),
        'dbi_scores': {str(k): float(s) for k, s in zip(num_topics_list, dbi_scores)},
        'topics_keywords': topics_keywords
    }

    lda_json_path = os.path.join(RESULTS_DIR, 'lda_results.json')
    with open(lda_json_path, 'w', encoding='utf-8') as f:
        json.dump(lda_results, f, ensure_ascii=False, indent=4)

    log.info(f"Hasil LDA diekspor ke JSON: {lda_json_path}")
    log.info("✅ Tahap 5 SELESAI KESELURUHANNYA!")


if __name__ == "__main__":
    main()
