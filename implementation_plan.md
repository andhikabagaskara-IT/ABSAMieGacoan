# Implementation Plan: Aspect-Based Sentiment Analysis — Mie Gacoan Surabaya

## Deskripsi Project

Project ini bertujuan untuk melakukan **Aspect-Based Sentiment Analysis (ABSA)** terhadap ulasan pelanggan restoran Mie Gacoan di seluruh kota Surabaya (12 cabang). Hasil analisis akan divisualisasikan dalam **dashboard interaktif VueJS** yang dapat digunakan oleh pihak manajemen sebagai tool analisa sentimen pelanggan.

**Sentimen**: Positif & Negatif  
**Algoritma Klasifikasi**: SVM & Naive Bayes (sebagai pembanding)  
**Algoritma Aspek**: LDA (Latent Dirichlet Allocation)  
**Evaluasi**: Accuracy, Precision, Recall, F1-Score (klasifikasi) + DBI (aspek)

---

## User Review Required

> [!IMPORTANT]
> **Pelabelan Sentimen Otomatis vs Manual**  
> Dengan target 60.000 ulasan, pelabelan manual tidak realistis. Saya mengusulkan **pelabelan otomatis berbasis rating**:
>
> - ⭐ Rating 1-2 → **Negatif**
> - ⭐ Rating 4-5 → **Positif**
> - ⭐ Rating 3 → **Dibuang** (ambigu/netral)
>
> Apakah pendekatan ini sesuai, atau Anda ingin menyertakan rating 3 ke salah satu kategori?

> [!IMPORTANT]
> **Target 5.000 ulasan per cabang**  
> Google Maps memiliki limitasi teknis — tidak semua cabang memiliki 5.000 ulasan yang tersedia. Scraper akan mengambil **sebanyak mungkin** ulasan yang tersedia per cabang. Jika total tidak mencapai 60.000, data tetap valid untuk analisis selama distribusinya cukup representatif.

> [!WARNING]
> **Waktu Scraping**  
> Scraping 60.000 ulasan dari 12 cabang akan memakan waktu cukup lama (estimasi 6-12 jam total tergantung koneksi internet). Proses ini akan berjalan otomatis satu cabang per satu cabang.

---

## Struktur Project

```
scrapinggacoan2026/
├── data/
│   ├── raw/                          # Data mentah per cabang (CSV)
│   ├── combined/                     # Data gabungan semua cabang
│   ├── labeled/                      # Data yang sudah dilabeli sentimen
│   └── preprocessed/                 # Data yang sudah di-preprocessing
├── models/                           # Model SVM, NB, LDA yang disimpan
├── results/                          # Hasil evaluasi & visualisasi
├── scripts/
│   ├── 01_scraping.py                # Scraping ulasan Google Maps
│   ├── 02_labeling.py                # Pelabelan sentimen otomatis
│   ├── 03_preprocessing.py           # Preprocessing NLP
│   ├── 04_classification.py          # Klasifikasi SVM & Naive Bayes
│   ├── 05_lda_aspect.py              # Ekstraksi aspek dengan LDA
│   └── 06_export_dashboard.py        # Export data untuk dashboard
├── dashboard/                        # VueJS Dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── assets/
│   │   ├── router/
│   │   ├── App.vue
│   │   └── main.js
│   ├── public/
│   └── package.json
├── requirements.txt                  # Python dependencies
└── README.md
```

---

## Proposed Changes

### Tahap 1: Setup Environment & Scraping Data

#### [NEW] [requirements.txt](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/requirements.txt)

Dependencies Python yang dibutuhkan:

- `selenium` — Web scraping automation
- `webdriver-manager` — Auto-manage ChromeDriver
- `pandas` — Data manipulation
- `numpy` — Numerical computing
- `scikit-learn` — SVM, Naive Bayes, evaluasi metrics, DBI
- `nltk` — NLP toolkit
- `Sastrawi` — Stemming Bahasa Indonesia
- `gensim` — LDA topic modeling
- `matplotlib` & `seaborn` — Visualisasi

#### [NEW] [scripts/01_scraping.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/01_scraping.py)

Script scraping yang diperbaiki dan ditingkatkan:

- Fix semua bug dari script asli (lihat analisis sebelumnya)
- **Daftar 12 cabang** dengan link Google Maps
- Menggunakan `webdriver-manager` agar ChromeDriver otomatis terunduh
- Scroll otomatis untuk memuat semua ulasan
- Klik "Selengkapnya" / "Lainnya" untuk mendapatkan teks review lengkap
- Ekstraksi: `nama_cabang`, `nama_pelanggan`, `tanggal_ulasan`, `rating`, `teks_komentar`
- Output: CSV per cabang di `data/raw/`
- Resume capability (jika scraping terhenti, bisa dilanjutkan)
- Progress logging
- Quality Check & Data Combining: buat di `scripts/02_quality_check.py`fungsinya Scan semua CSV di `data/raw/`, Validasi struktur (kolom lengkap, tidak ada null di teks_komentar), Tampilkan statistik per cabang (jumlah data, distribusi rating), Deteksi duplikat, Gabungkan menjadi satu file `data/combined/all_reviews.csv`

#### [DELETE] [scrapinggacoan2026.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scrapinggacoan2026.py)

Script lama yang berisi banyak bug akan digantikan oleh `scripts/01_scraping.py`

---

### Tahap 2: Pelabelan Data

#### [NEW] [scripts/03_labeling.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/03_labeling.py)

- Gabungkan semua CSV dari `data/raw/` menjadi satu dataset
- Labeling otomatis berdasarkan rating:
  - Rating 1-2 → `negatif`
  - Rating 4-5 → `positif`
  - Rating 3 → dibuang (atau sesuai keputusan user)
- Output: `data/labeled/labeled_reviews.csv`
- Statistik distribusi label

---

### Tahap 3: Preprocessing Data

#### [NEW] [scripts/04_preprocessing.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/04_preprocessing.py)

Pipeline preprocessing Bahasa Indonesia:

1. **Cleaning Data** — Hapus URL, emoji, mentions, angka, karakter spesial
2. **Case Folding** — Semua teks menjadi lowercase
3. **Normalization** — Normalisasi slang/singkatan Bahasa Indonesia (misal: "gak" → "tidak", "bgt" → "banget" → "sangat", "ga" → "tidak", dll)
4. **Tokenizing** — Pecah teks menjadi token/kata
5. **Stopword Removal** — Hapus stopword Bahasa Indonesia menggunakan NLTK + custom stopwords
6. **Stemming** — Stemming Bahasa Indonesia menggunakan Sastrawi

- Output: `data/preprocessed/preprocessed_reviews.csv`
- Kolom tambahan untuk setiap tahap preprocessing (agar bisa di-track)

---

### Tahap 4: Klasifikasi Sentimen (SVM & Naive Bayes)

#### [NEW] [scripts/05_classification.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/05_classification.py)

- **TF-IDF Vectorization** untuk representasi teks
- **Train/Test Split** (80:20)
- **SVM (Support Vector Machine)** — Training & evaluasi
- **Naive Bayes (Multinomial)** — Training & evaluasi
- Evaluasi kedua model:
  - Accuracy
  - Precision
  - Recall
  - F1-Score
  - Confusion Matrix
  - Classification Report
- **Perbandingan performa** SVM vs Naive Bayes
- Simpan model ke `models/`
- Output evaluasi ke `results/`

---

### Tahap 5: Ekstraksi Aspek dengan LDA

#### [NEW] [scripts/06_lda_aspect.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/06_lda_aspect.py)

- LDA topic modeling menggunakan Gensim
- Eksperimen jumlah topik optimal (misal: 3, 5, 7, 10)
- Evaluasi menggunakan **Davies-Bouldin Index (DBI)**
- Identifikasi aspek dominan (misal: rasa, harga, pelayanan, kebersihan, dll)
- Mapping topik ke aspek yang mudah dipahami
- Visualisasi distribusi topik
- Output: aspek per ulasan + evaluasi DBI ke `results/`

---

### Tahap 6: Export Data untuk Dashboard

#### [NEW] [scripts/07_export_dashboard.py](file:///c:/PC%20DHIKA/2025/Kuliah/SKRIPSI/scrapinggacoan2026/scripts/07_export_dashboard.py)

- Export semua hasil analisis ke format JSON untuk dikonsumsi dashboard VueJS
- Data meliputi:
  - Statistik sentimen per cabang
  - Perbandingan evaluasi SVM vs Naive Bayes
  - Distribusi aspek per cabang
  - Trend sentimen berdasarkan waktu
  - Top keywords per aspek
  - Raw review data dengan label & aspek

---

### Tahap 7: Dashboard Interaktif VueJS

#### [NEW] `dashboard/` — Aplikasi VueJS

Fitur-fitur dashboard untuk manajemen restoran:

1. **Dashboard Overview**
   - Total ulasan yang dianalisis
   - Distribusi sentimen keseluruhan (pie/donut chart)
   - Perbandingan sentimen antar cabang (bar chart)
   - Trend sentimen berdasarkan waktu (line chart)

2. **Analisis Per Cabang**
   - Pilih cabang tertentu
   - Distribusi sentimen cabang tersebut
   - Aspek dominan per cabang
   - Ulasan terbaru dengan sentimen & aspek

3. **Perbandingan Algoritma**
   - Tabel perbandingan SVM vs Naive Bayes
   - Metrics: Accuracy, Precision, Recall, F1-Score
   - Confusion Matrix visual
   - Insight mana yang lebih baik

4. **Analisis Aspek (LDA)**
   - Daftar aspek yang ditemukan
   - Word cloud per aspek
   - Distribusi sentimen per aspek
   - DBI score dan evaluasi
   - Aspek mana yang perlu perbaikan

5. **Tool Analisis Sentimen Real-time**
   - Input teks ulasan manual
   - Prediksi sentimen menggunakan SVM & Naive Bayes
   - Tampilkan hasil kedua algoritma sebagai pembanding

6. **Data Explorer**
   - Tabel interaktif semua ulasan
   - Filter berdasarkan cabang, sentimen, aspek
   - Search functionality
   - Export data

---

## Open Questions

> [!IMPORTANT]
> **Rating 3 bintang** — Dibuang, dikategorikan positif, atau dikategorikan negatif? Rekomendasi saya: **dibuang** karena ambigu dan bisa menurunkan akurasi model.

---

## Verification Plan

### Automated Tests

1. **Scraping**: Cek jumlah data yang berhasil di-scrape per cabang, validasi format CSV
2. **Preprocessing**: Cek integritas data sebelum dan sesudah preprocessing
3. **Klasifikasi**: Evaluasi metrics (Accuracy, Precision, Recall, F1-Score) untuk SVM & NB
4. **LDA**: DBI score untuk mengevaluasi kualitas clustering aspek
5. **Dashboard**: Test semua fitur di browser, memastikan data tampil dengan benar

### Manual Verification

- User memverifikasi sample hasil scraping apakah sesuai dengan ulasan di Google Maps
- User memverifikasi kualitas hasil preprocessing
- User memvalidasi aspek yang ditemukan LDA apakah masuk akal secara bisnis
- User menguji dashboard di browser untuk keperluan presentasi/skripsi

---

## Urutan Pengerjaan

| No  | Tahap                                    | Status      |
| --- | ---------------------------------------- | ----------- |
| 1   | Setup environment + Install dependencies | ✅ Selesai  |
| 2   | Scraping data 12 cabang                  | ✅ Selesai  |
| 3   | Pelabelan sentimen                       | ✅ Selesai  |
| 4   | Preprocessing data                       | ✅ Selesai  |
| 5   | Klasifikasi SVM & Naive Bayes            | ✅ Selesai  |
| 6   | Ekstraksi aspek LDA                      | ✅ Selesai  |
| 7   | Export data untuk dashboard              | ✅ Selesai  |
| 8   | Dashboard VueJS (Frontend)               | 🔜 Sedang  |

> [!NOTE]
> **Tahap 1–7 telah selesai.** Data telah diekspor ke `data/export/dashboard_data.json` (51.885 ulasan, 568KB).
> Tahap 8 (Dashboard VueJS) sedang dalam pengerjaan — detail plan frontend tersedia di artifact terpisah.
