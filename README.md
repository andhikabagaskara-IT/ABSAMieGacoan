# Aspect-Based Sentiment Analysis (ABSA) - Mie Gacoan Surabaya

Selamat datang di repositori proyek **Analisis Sentimen Berbasis Aspek (Aspect-Based Sentiment Analysis)** untuk restoran Mie Gacoan cabang Surabaya. Proyek ini bertujuan untuk mengumpulkan, menganalisis, dan memvisualisasikan ulasan pelanggan dari platform Google Maps untuk memberikan wawasan bisnis mendalam bagi pihak manajemen.

## 📌 Deskripsi Proyek

Proyek machine learning ini dikembangkan secara _end-to-end_ untuk menyelesaikan permasalahan di dunia nyata. Berikut adalah alur besar tahapannya:

1. **Scraping Ulasan**: Mengumpulkan total target 60.000 ulasan dari 12 cabang Mie Gacoan di Surabaya menggunakan Selenium Python.
2. **Pelabelan Sentimen**: Mengkategorikan ulasan secara otomatis menjadi **Positif**, **Negatif**, atau **Netral** berdasarkan kombinasi kata kunci dari teks komentar dan rating bintang yang diberikan oleh pelanggan.
3. **Preprocessing Data (NLP)**: Memproses data teks ulasan yang berantakan menggunakan pipeline _Natural Language Processing_ Bahasa Indonesia (Cleaning, Case Folding, Normalisasi Slang, Tokenizing, Stopword Removal, Stemming Sastrawi).
4. **Klasifikasi Sentimen**: Melatih algoritma machine learning **Support Vector Machine (SVM)** dan membandingkannya dengan **Naive Bayes** menggunakan **Stratified K-Fold Cross-Validation (K=5) + SMOTE**.
5. **Ekstraksi Aspek (Topic Modeling)**: Mengidentifikasi topik/aspek utama ulasan secara dinamis dengan mencari _K optimal (Range K=3-10)_ menggunakan **Latent Dirichlet Allocation (LDA)**, yang dievaluasi kualitas clusteringnya menggunakan metrik _Davies-Bouldin Index (DBI)_.
6. **Backend API Fullstack**: Menggunakan **Flask** + **PostgreSQL** + **Flask-JWT-Extended** sebagai backend REST API dengan autentikasi 3 role (Admin, Analyst, User), server-side pagination, prediksi sentimen real-time, dan pipeline execution.
7. **Dashboard Interaktif**: Menyajikan insight sentimen (3 Kelas: Positif, Negatif, Netral) dan metrik model dalam bentuk visualisasi web yang interaktif menggunakan **VueJS**, memuat 50.000+ data _explorer_ lengkap dengan animasi transisi Dark Mode.

## 👥 Sistem Role Pengguna

| Role        | Akun Default          | Password   | Hak Akses                                                                  |
| ----------- | --------------------- | ---------- | -------------------------------------------------------------------------- |
| **Admin**   | admin@miegacoan.com   | admin123   | Full access — CRUD user, scraping, retrain, hapus data, export, migrasi DB |
| **Analyst** | analyst@miegacoan.com | analyst123 | Dashboard, prediksi sentimen, scraping, retrain, export, riwayat pipeline  |
| **User**    | staff@miegacoan.com   | staff123   | Read-only — dashboard, data explorer, profil sendiri                       |

## 📂 Struktur Folder Repositori

- **`data/`**: Direktori penyimpanan segala dataset yang diperlukan di berbagai tahap.
  - `raw/` : Dataset mentah hasil scraping, dipisah per cabang (CSV).
  - `combined/` : Dataset yang telah digabung dan melewati _quality check_.
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

## 🛠️ Teknologi Stack yang Dipakai

Aplikasi ini itu sejatinya gabungan dari berbagai macam teknologi keren yang saling "ngobrol" satu sama lain biar jadi _website fullstack_ yang utuh. Ini rinciannya:

### 🐍 Python & Machine Learning (Otaknya)

Bagian "cerdas" dari sistem kita ini dibangun sepenuhnya pakai **Python**. Beberapa _library_ kunci yang kerja keras di belakang layar:

- **Selenium**: Buat jalan-jalan otomatis di web dan sedot (scraping) ribuan data _review_ dari Google Maps.
- **Scikit-Learn**: Mesin utama yang bikin algoritma **Support Vector Machine (SVM)** dan **Naive Bayes** bisa jalan. Termasuk nyari topik-topik (aspek) pakai metode **Latent Dirichlet Allocation (LDA)**.
- **Sastrawi & NLTK**: Dua _tools_ NLP (Natural Language Processing) ini bertugas buat bersihin teks Bahasa Indonesia yang alay-alay, ngubah kata dasar (stemming), dan buang kata gak penting (stopword).
- **Imbalanced-learn (SMOTE)**: Ini trik sulap buat bikin data sentimen yang tadinya timpang (kebanyakan orang nge-rate positif) jadi seimbang, biar _AI_-nya belajar dengan adil.
- **Pandas & Numpy**: Spesialis tukang hitung dan pengatur tabel data berukuran raksasa.

### 🌐 Backend API (Penghubung Data)

Setelah otaknya pinter, datanya harus "dilempar" ke antarmuka (_interface_). Nah, buat tugas ini kita pakai:

- **Flask**: _Framework_ web Python yang ringan, kencang, dan dipake buat ngebangun REST API kita.
- **PostgreSQL**: _Database_ utamanya! Gak pakai abal-abal, kita pakai PostgreSQL buat nyimpen ribuan ulasan dan log secara permanen. Kerennya, kita pakai tipe data `JSONB` biar fleksibel nyimpen hasil _preprocessing_ teks.
- **SQLAlchemy (ORM)**: Jembatan buat ngomong dari kode Python langsung ke database PostgreSQL tanpa pusing nulis _query SQL_ panjang-panjang.
- **Flask-JWT-Extended**: Satpam sistem kita. Dia yang ngurus _login_, _logout_, dan memastikan kalau _user_ bodong nggak bakal bisa masuk sembarangan.
- **Flask-Limiter**: Mencegah orang usil nge-spam API kita terlalu banyak.

### 🎨 Frontend UI (Tampilan Web)

Biar aplikasinya enak dipandang mata (dan bos Gacoan seneng liatnya), bagian antarmuka (_interface_) digarap dengan:

- **Vue.js 3 (Composition API)**: Framework _JavaScript_ super canggih buat bikin halaman web yang interaktif tanpa perlu nge-_refresh_ halaman terus-terusan (Single Page Application).
- **Vite**: Alat _bundler_ masa kini yang bikin proses _development_ Vue.js ngebut pol!
- **Pinia**: Kotak penyimpan memori sementara (State Management). Berguna banget buat nyimpen info kayak "siapa sih yang lagi _login_ sekarang?" dan "apa token _JWT_-nya?".
- **Axios**: Kurir andalan yang tugasnya ngirim permohonan (_HTTP Request_) dari web Vue ke server Flask. Dia juga dilengkapi "Interceptor" (buat masang token rahasia otomatis di tiap kiriman).
- **Vanilla CSS (No Framework)**: Buat masalah desain (warna, animasi, bayangan, mode gelap/terang), semuanya murni pakai CSS murni hasil koding manual, tanpa ngandelin Tailwind atau Bootstrap. Kustomisasi level dewa!
- **Lucide-Vue-Next**: Kumpulan _icon_ minimalis dan cakep biar webnya berasa lebih profesional.

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

### B. Menjalankan Aplikasi Web Fullstack (Backend + Frontend)

Untuk menggunakan dashboard dan fitur API secara bersamaan, Anda perlu menjalankan kedua server (backend dan frontend) di terminal yang terpisah.

**Terminal 1: Menjalankan Backend (Flask API)**

```bash
# 1. Masuk ke folder backend & aktifkan virtual environment (jika ada)
cd backend
venv\Scripts\activate  # Windows

# 2. Pastikan PostgreSQL berjalan dan database sudah terhubung di .env
# 3. Jalankan server Flask
python app.py
# Backend akan berjalan di: http://localhost:5000
```

**Terminal 2: Menjalankan Frontend (VueJS Dashboard)**

```bash
# 1. Buka terminal baru, masuk ke folder dashboard
cd dashboard

# 2. Install package (hanya pertama kali)
npm install

# 3. Jalankan development server
npm run dev
# Frontend akan berjalan di: http://localhost:5173
```

> Buka browser dan akses **`http://localhost:5173`** untuk menggunakan aplikasi. Anda bisa login menggunakan akun default admin: `admin@miegacoan.com` (pass: `admin123`).

## 📡 API Endpoints Utama

| Method | Endpoint                         | Akses          | Deskripsi                         |
| ------ | -------------------------------- | -------------- | --------------------------------- |
| POST   | `/api/auth/login`                | Public         | Login & dapatkan JWT token        |
| POST   | `/api/auth/logout`               | All            | Logout & revoke token             |
| GET    | `/api/dashboard`                 | All            | Data agregasi dashboard           |
| GET    | `/api/reviews`                   | All            | Ulasan (server-side pagination)   |
| POST   | `/api/predict`                   | Admin, Analyst | Prediksi sentimen real-time       |
| POST   | `/api/pipeline/start`            | Admin, Analyst | Mulai pipeline (scraping/retrain) |
| GET    | `/api/pipeline/export-csv`       | Admin, Analyst | Export data ke CSV                |
| GET    | `/api/pipeline/role-permissions` | All            | Permissions berdasarkan role      |
| GET    | `/api/admin/users`               | Admin          | Daftar semua user                 |
| POST   | `/api/admin/migrate-csv`         | Admin          | Migrasi CSV ke PostgreSQL         |

> **Catatan**: Semua endpoint `/api/*` (kecuali login) memerlukan header `Authorization: Bearer <token>`.

## 🔐 Keamanan

- **JWT Authentication** — Access token (1 jam) + Refresh token (30 hari)
- **Token Blacklisting** — Token yang di-logout tidak bisa dipakai lagi
- **Rate Limiting** — 200 request/jam per IP (mencegah abuse)
- **Password Hashing** — bcrypt (salt-based)
- **RBAC** — Role-Based Access Control dengan 3 level

> **Catatan**: Tahapan lanjutan akan diupdate seiring berjalannya proyek. Lihat `implementation_plan.md` untuk detail lengkap.
