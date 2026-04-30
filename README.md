# Aspect-Based Sentiment Analysis (ABSA) - Mie Gacoan Surabaya

Selamat datang di repositori proyek **Analisis Sentimen Berbasis Aspek (Aspect-Based Sentiment Analysis)** untuk restoran Mie Gacoan cabang Surabaya. Proyek ini bertujuan untuk mengumpulkan, menganalisis, dan memvisualisasikan ulasan pelanggan dari platform Google Maps untuk memberikan wawasan bisnis mendalam bagi pihak manajemen.

## 📌 Deskripsi Proyek

Proyek machine learning ini dikembangkan secara *end-to-end* untuk menyelesaikan permasalahan di dunia nyata. Berikut adalah alur besar tahapannya:
1. **Scraping Ulasan**: Mengumpulkan total target 60.000 ulasan dari 12 cabang Mie Gacoan di Surabaya menggunakan Selenium Python.
2. **Pelabelan Sentimen**: Mengkategorikan ulasan secara otomatis menjadi **Positif**, **Negatif**, atau **Netral** berdasarkan kombinasi kata kunci dari teks komentar dan rating bintang yang diberikan oleh pelanggan.
3. **Preprocessing Data (NLP)**: Memproses data teks ulasan yang berantakan menggunakan pipeline *Natural Language Processing* Bahasa Indonesia (Cleaning, Case Folding, Normalisasi Slang, Tokenizing, Stopword Removal, Stemming Sastrawi).
4. **Klasifikasi Sentimen**: Melatih algoritma machine learning **Support Vector Machine (SVM)** dan membandingkannya dengan **Naive Bayes**.
5. **Ekstraksi Aspek (Topic Modeling)**: Mengidentifikasi 4 topik/aspek utama ulasan (seperti Rasa, Harga, Pelayanan, Tempat) menggunakan **Latent Dirichlet Allocation (LDA)**, yang dievaluasi kualitas clusteringnya menggunakan metrik *Davies-Bouldin Index (DBI)*. Ekstraksi ini juga secara otomatis menghasilkan gambar Word Cloud.
6. **Dashboard Interaktif**: Menyajikan insight sentimen dan metrik model dalam bentuk visualisasi web yang interaktif menggunakan **VueJS**, lengkap dengan animasi transisi Dark Mode dan penjelasan algoritma yang ramah pengguna.

## 📂 Struktur Folder Repositori

- **`data/`**: Direktori penyimpanan segala dataset yang diperlukan di berbagai tahap.
  - `raw/` : Dataset mentah hasil scraping, dipisah per cabang (CSV).
  - `combined/` : Dataset yang telah digabung dan melewati *quality check*.
  - `labeled/` : Dataset yang sudah diberi target label sentimen (`positif`, `negatif`, `netral`).
  - `preprocessed/` : Dataset bersih yang sudah melalui tahap pemrosesan NLP.
- **`scripts/`**: Kumpulan kode Python (bernomor sesuai urutan) untuk memproses pipeline data.
  - `01_scraping.py` : Automasi scraping data dari web.
  - `02_quality_check.py` : Pemeriksaan kualitas data dan penggabungan dataset.
  - `03_labeling.py` : Pelabelan sentiment otomatis.
  - `04_preprocessing.py` : Skrip NLP preprocessing (sedang dikerjakan).
  - `05_classification.py` : Skrip Klasifikasi dengan SVM & NB, Stratified K-Fold, dan SMOTE.
  - `06_lda_aspect.py` : Skrip ekstraksi aspek menggunakan LDA.
  - `07_export_dashboard.py` : Skrip export JSON untuk dashboard.
- **`models/`**: Folder ini akan berisi model yang sudah di-training (`.pkl` atau `.joblib`) agar tidak perlu training ulang saat dipanggil aplikasi.
- **`results/`**: Menyimpan dokumen laporan metrik evaluasi seperti Confusion Matrix, *classification reports*, hingga DBI Score dari pemodelan LDA.
- **`dashboard/`**: Folder *frontend* berisi proyek VueJS yang berfungsi sebagai *user interface* untuk melihat statistik sentimen dan prediksi *real-time*.

## 🚀 Cara Menjalankan

Bagi yang ingin mencoba menjalankan *pipeline* dari awal secara lokal, silakan ikuti petunjuk berikut:

1. **Persiapan Environtment & Install Dependencies**
   Pastikan Python 3.8+ sudah terinstall. Kemudian jalankan:
   ```bash
   pip install -r requirements.txt
   ```
2. **Jalankan Skrip Python Berurutan**
   ```bash
   # 1. Mulai scraping (pastikan koneksi stabil, memakan waktu lama)
   python scripts/01_scraping.py
   
   # 2. Cek kualitas data raw, dan menggabungkan menjadi file utuh
   python scripts/02_quality_check.py
   
   # 3. Memberikan label sentimen otomatis
   python scripts/03_labeling.py
   
   # 4. Melakukan NLP preprocessing (memakan waktu saat proses Stemming Sastrawi)
   python scripts/04_preprocessing.py
   
   # 5. Klasifikasi dengan K-Fold & SMOTE
   python scripts/05_classification.py
   
   # 6. Pemodelan Topik/Aspek dengan LDA
   python scripts/06_lda_aspect.py
   
   # 7. Ekspor hasil ke Dashboard (JSON)
   python scripts/07_export_dashboard.py
   ```

> **Catatan**: Tahapan lanjutan akan diupdate seiring berjalannya proyek. Harap berhati-hati saat menjalankan skrip yang memakan waktu lama (seperti scraping dan stemming) — Anda mungkin bisa mengedit kodenya sedikit untuk memproses sampel data (misalnya `df.head(100)`) bila hanya ingin menguji *pipeline*.
