# Aspect-Based Sentiment Analysis (ABSA) - Mie Gacoan Surabaya

Selamat datang di repositori proyek **Analisis Sentimen Berbasis Aspek (Aspect-Based Sentiment Analysis)** untuk restoran Mie Gacoan cabang Surabaya. Proyek ini bertujuan untuk mengumpulkan, menganalisis, dan memvisualisasikan ulasan pelanggan dari platform Google Maps untuk memberikan wawasan bisnis mendalam bagi pihak manajemen.

## 📌 Deskripsi Proyek

Proyek machine learning ini dikembangkan secara *end-to-end* untuk menyelesaikan permasalahan di dunia nyata. Berikut adalah alur besar tahapannya:
1. **Scraping Ulasan**: Mengumpulkan total target 60.000 ulasan dari 12 cabang Mie Gacoan di Surabaya menggunakan Selenium Python.
2. **Pelabelan Sentimen**: Mengkategorikan ulasan secara otomatis menjadi **Positif**, **Negatif**, atau **Netral** berdasarkan kombinasi kata kunci dari teks komentar dan rating bintang yang diberikan oleh pelanggan.
3. **Preprocessing Data (NLP)**: Memproses data teks ulasan yang berantakan menggunakan pipeline *Natural Language Processing* Bahasa Indonesia (Cleaning, Case Folding, Normalisasi Slang, Tokenizing, Stopword Removal, Stemming Sastrawi).
4. **Klasifikasi Sentimen**: Melatih algoritma machine learning **Support Vector Machine (SVM)** dan membandingkannya dengan **Naive Bayes** menggunakan **Stratified K-Fold Cross-Validation (K=5) + SMOTE**.
5. **Ekstraksi Aspek (Topic Modeling)**: Mengidentifikasi topik/aspek utama ulasan secara dinamis dengan mencari *K optimal (Range K=3-10)* menggunakan **Latent Dirichlet Allocation (LDA)**, yang dievaluasi kualitas clusteringnya menggunakan metrik *Davies-Bouldin Index (DBI)*.
6. **Backend API Fullstack**: Menggunakan **Flask** + **PostgreSQL** + **Flask-JWT-Extended** sebagai backend REST API dengan autentikasi 3 role (Admin, Analyst, User), server-side pagination, prediksi sentimen real-time, dan pipeline execution.
7. **Dashboard Interaktif**: Menyajikan insight sentimen (3 Kelas: Positif, Negatif, Netral) dan metrik model dalam bentuk visualisasi web yang interaktif menggunakan **VueJS**, memuat 50.000+ data *explorer* lengkap dengan animasi transisi Dark Mode.

## 👥 Sistem Role Pengguna

| Role | Akun Default | Password | Hak Akses |
|------|-------------|----------|-----------|
| **Admin** | admin@miegacoan.com | admin123 | Full access — CRUD user, scraping, retrain, hapus data, export, migrasi DB |
| **Analyst** | analyst@miegacoan.com | analyst123 | Dashboard, prediksi sentimen, scraping, retrain, export, riwayat pipeline |
| **User** | staff@miegacoan.com | staff123 | Read-only — dashboard, data explorer, profil sendiri |

## 📂 Struktur Folder Repositori

- **`data/`**: Direktori penyimpanan segala dataset yang diperlukan di berbagai tahap.
  - `raw/` : Dataset mentah hasil scraping, dipisah per cabang (CSV).
  - `combined/` : Dataset yang telah digabung dan melewati *quality check*.
  - `labeled/` : Dataset yang sudah diberi target label sentimen.
  - `preprocessed/` : Dataset bersih yang sudah melalui tahap pemrosesan NLP.
  - `export/` : Data JSON untuk dashboard.
- **`scripts/`**: Kumpulan kode Python (bernomor sesuai urutan) untuk memproses pipeline data.
  - `01_scraping.py` — `07_export_dashboard.py`
- **`models/`**: Model yang sudah di-training (SVM, NB, TF-IDF, LDA) dalam format `.pkl`.
- **`results/`**: Laporan metrik evaluasi (Confusion Matrix, K-Fold, DBI Score).
- **`backend/`**: Flask REST API Fullstack.
  - `app.py` — App Factory (JWT, Rate Limiter, Blueprint)
  - `models/` — SQLAlchemy ORM (User, Review, AnalysisResult, PipelineLog)
  - `routes/` — Blueprint (auth, dashboard, reviews, predict, pipeline, admin)
- **`dashboard/`**: Frontend VueJS untuk visualisasi sentimen.

## 🛠️ Teknologi Stack

| Komponen | Teknologi |
|----------|-----------|
| **ML Pipeline** | Python, Scikit-learn (SVM, NB), SMOTE, LDA, Sastrawi, NLTK |
| **Backend** | Flask, Flask-JWT-Extended, SQLAlchemy, Flask-Limiter |
| **Database** | PostgreSQL (JSONB untuk data semi-structured) |
| **Frontend** | VueJS, Vite |
| **Scraping** | Selenium, WebDriver Manager |

## 🚀 Cara Menjalankan

### A. Pipeline Machine Learning

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Jalankan pipeline berurutan
python scripts/01_scraping.py          # Scraping (memakan waktu lama)
python scripts/02_quality_check.py     # Quality Check & Combining
python scripts/03_labeling.py          # Labeling sentimen
python scripts/04_preprocessing.py     # NLP Preprocessing (stemming lambat)
python scripts/05_classification.py    # K-Fold CV + SMOTE + SVM & NB
python scripts/06_lda_aspect.py        # Ekstraksi Aspek LDA
python scripts/07_export_dashboard.py  # Export JSON untuk dashboard
```

### B. Backend Fullstack (Flask + PostgreSQL)

```bash
# 1. Install & jalankan PostgreSQL, lalu buat database:
#    psql -U postgres
#    CREATE DATABASE miegacoan_absa;

# 2. Konfigurasi environment
cd backend
copy .env.example .env
# Edit .env: sesuaikan DATABASE_URL dengan password PostgreSQL Anda

# 3. Install dependencies & jalankan
pip install -r requirements.txt
python app.py
# Server berjalan di http://localhost:5000

# 4. (Pertama kali) Migrasi data CSV ke PostgreSQL
# Login dulu via POST /api/auth/login, lalu:
# POST /api/admin/migrate-csv dengan header Authorization: Bearer <token>
```

### C. Dashboard VueJS

```bash
cd dashboard
npm install
npm run dev
# Dashboard berjalan di http://localhost:5173
```

## 📡 API Endpoints Utama

| Method | Endpoint | Akses | Deskripsi |
|--------|----------|-------|-----------|
| POST | `/api/auth/login` | Public | Login & dapatkan JWT token |
| POST | `/api/auth/logout` | All | Logout & revoke token |
| GET | `/api/dashboard` | All | Data agregasi dashboard |
| GET | `/api/reviews` | All | Ulasan (server-side pagination) |
| POST | `/api/predict` | Admin, Analyst | Prediksi sentimen real-time |
| POST | `/api/pipeline/start` | Admin, Analyst | Mulai pipeline (scraping/retrain) |
| GET | `/api/pipeline/export-csv` | Admin, Analyst | Export data ke CSV |
| GET | `/api/pipeline/role-permissions` | All | Permissions berdasarkan role |
| GET | `/api/admin/users` | Admin | Daftar semua user |
| POST | `/api/admin/migrate-csv` | Admin | Migrasi CSV ke PostgreSQL |

> **Catatan**: Semua endpoint `/api/*` (kecuali login) memerlukan header `Authorization: Bearer <token>`.

## 🔐 Keamanan

- **JWT Authentication** — Access token (1 jam) + Refresh token (30 hari)
- **Token Blacklisting** — Token yang di-logout tidak bisa dipakai lagi
- **Rate Limiting** — 200 request/jam per IP (mencegah abuse)
- **Password Hashing** — bcrypt (salt-based)
- **RBAC** — Role-Based Access Control dengan 3 level

> **Catatan**: Tahapan lanjutan akan diupdate seiring berjalannya proyek. Lihat `implementation_plan.md` untuk detail lengkap.
