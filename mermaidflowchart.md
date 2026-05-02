# Alur Proses Pipeline ABSA Mie Gacoan

Berikut adalah representasi visual dari alur data pada proyek Aspect-Based Sentiment Analysis Mie Gacoan Surabaya.

```mermaid
graph TD
    subgraph "Data Acquisition & Preparation"
        A[01_scraping.py<br/>Scraping Google Maps] --> B[02_quality_check.py<br/>Quality Check & Combining]
        B --> C[03_labeling.py<br/>Labeling Sentimen]
        C --> D[04_preprocessing.py<br/>Preprocessing Data NLP]
    end

    subgraph "Machine Learning Modeling"
        D --> E[05_classification.py<br/>Stratified K-Fold CV + SMOTE]
        E --> F[06_lda_aspect.py<br/>Ekstraksi Aspek LDA]

        subgraph "Detail Klasifikasi"
            E1[Inisialisasi Stratified K-Fold K=5] --> E2[Loop Fold 1..K]
            E2 --> E3[TF-IDF Vectorization]
            E3 --> E4[SMOTE pada Training]
            E4 --> E5[Training SVM & NB]
            E5 --> E6[Validasi Data Test]
        end
        E -.-> E1
    end

    subgraph "Presentation Layer"
        F --> G[07_export_dashboard.py<br/>Export JSON Dashboard]
        G --> H[Backend Flask API<br/>PostgreSQL + JWT Auth]
        H --> I[Dashboard VueJS<br/>Visualisasi Interaktif]
        G -.-> I
    end

    classDef python fill:#4FC3F7,stroke:#0288D1,stroke-width:2px,color:#000
    classDef output fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    classDef ui fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000
    classDef backend fill:#CE93D8,stroke:#8E24AA,stroke-width:2px,color:#000

    class A,B,C,D,E,F,G python
    class H backend
    class I ui
```

## Deskripsi Flow

1. **Scraping**: Pengumpulan data mentah dari ulasan Google Maps.
2. **Quality Check**: Pembersihan duplikat, pengecekan nilai null, dan menggabungkan semua data.
3. **Labeling**: Pelabelan ke kelas Positif, Negatif, Netral berdasarkan kombinasi rating bintang dan sentimen teks komentar (lexicon matching).
4. **Preprocessing**: Pembersihan teks, stemming, tokenizing.
5. **Classification**: Melatih model dengan mengatasi ketidakseimbangan data (SMOTE) dan divalidasi dengan K-Fold untuk hasil objektif.
6. **LDA Aspect**: Mengekstrak topik utama secara dinamis berdasarkan skor evaluasi DBI terendah (Range K=3-10) beserta pembuatan Word Cloud untuk visualisasi.
7. **Export**: Mempersiapkan dataset JSON akhir.
8. **Backend API**: REST API fullstack (Flask + PostgreSQL + JWT) untuk autentikasi, data serving, dan prediksi real-time.
9. **Dashboard**: Menampilkan metrik (Positif, Negatif, Netral), analisis cabang dengan sampel seimbang, performa algoritma, evaluasi DBI, dan tool sentimen secara interaktif dengan dukungan *Dark Mode*.

---

## Data Flow Diagram (DFD)

### DFD Level 0 — Context Diagram

Menunjukkan sistem ABSA Mie Gacoan sebagai satu proses tunggal beserta entitas eksternalnya.

```mermaid
graph LR
    GM["Google Maps<br/>(Sumber Data)"] -->|Ulasan Pelanggan| SYS["Sistem ABSA<br/>Mie Gacoan"]
    ADM["Admin<br/>(Manajemen)"] -->|Perintah Scraping,<br/>Kelola User,<br/>Retrain Model| SYS
    ANL["Analyst<br/>(Marketing/Data Scientist)"] -->|Input Teks Prediksi,<br/>Request Analisis| SYS
    USR["User<br/>(Pegawai/Staf)"] -->|Request Data<br/>Dashboard| SYS

    SYS -->|Data CSV Mentah| GM
    SYS -->|Dashboard Analisis,<br/>Manajemen User,<br/>Log Pipeline| ADM
    SYS -->|Hasil Prediksi,<br/>Dashboard Analisis,<br/>Export Data| ANL
    SYS -->|Dashboard Read-only,<br/>Data Explorer| USR

    classDef external fill:#FFE0B2,stroke:#F57C00,stroke-width:2px,color:#000
    classDef system fill:#E1BEE7,stroke:#8E24AA,stroke-width:3px,color:#000

    class GM,ADM,ANL,USR external
    class SYS system
```

### DFD Level 1 — Dekomposisi Proses Utama

Menunjukkan 6 proses utama di dalam sistem beserta data store-nya.

```mermaid
graph TD
    %% Entitas Eksternal
    GM["Google Maps"]
    ADM["Admin"]
    ANL["Analyst"]
    USR["User/Staf"]

    %% Proses-proses Utama
    P1["P1<br/>Akuisisi Data<br/>(Scraping + QC)"]
    P2["P2<br/>Analisis NLP<br/>(Labeling + Preprocessing)"]
    P3["P3<br/>Pemodelan ML<br/>(Classification + LDA)"]
    P4["P4<br/>Penyajian Data<br/>(Export + API)"]
    P5["P5<br/>Autentikasi<br/>(JWT Login/Register)"]
    P6["P6<br/>Prediksi Real-time<br/>(Algorithm Lab)"]

    %% Data Store
    DS1[("DS1<br/>Data Mentah<br/>(CSV per Cabang)")]
    DS2[("DS2<br/>Data Gabungan<br/>(all_reviews.csv)")]
    DS3[("DS3<br/>Data Preprocessed<br/>(preprocessed.csv)")]
    DS4[("DS4<br/>Model ML<br/>(SVM, NB, TF-IDF, LDA)")]
    DS5[("DS5<br/>PostgreSQL Database<br/>(reviews, users, logs)")]
    DS6[("DS6<br/>Dashboard JSON<br/>(dashboard_data.json)")]

    %% Alur Data
    GM -->|"Ulasan HTML"| P1
    ADM -->|"Parameter Scraping"| P1
    ADM -->|"Kredensial, Data User"| P5
    ANL -->|"Teks Ulasan"| P6
    ANL -->|"Kredensial"| P5
    USR -->|"Kredensial"| P5

    P1 -->|"Data CSV Mentah"| DS1
    DS1 -->|"CSV per Cabang"| P1
    P1 -->|"Data Gabungan Bersih"| DS2

    DS2 -->|"Data untuk Labeling"| P2
    P2 -->|"Data Terlabel + Preprocessed"| DS3

    DS3 -->|"Data untuk Training"| P3
    P3 -->|"Model Terlatih"| DS4
    P3 -->|"Hasil Evaluasi"| DS6

    DS3 -->|"Data + Aspek"| P4
    DS6 -->|"Dashboard JSON"| P4
    DS4 -->|"Model untuk Prediksi"| P6
    P4 -->|"Data Review"| DS5

    P5 -->|"JWT Token"| ADM
    P5 -->|"JWT Token"| ANL
    P5 -->|"JWT Token"| USR
    P5 -->|"Data User"| DS5
    DS5 -->|"Verifikasi User"| P5

    P4 -->|"Dashboard + Statistik"| ADM
    P4 -->|"Dashboard + Statistik"| ANL
    P4 -->|"Dashboard Read-only"| USR
    P6 -->|"Hasil Prediksi SVM/NB"| ANL

    classDef ext fill:#FFE0B2,stroke:#F57C00,stroke-width:2px,color:#000
    classDef proc fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#000
    classDef store fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000

    class GM,ADM,ANL,USR ext
    class P1,P2,P3,P4,P5,P6 proc
    class DS1,DS2,DS3,DS4,DS5,DS6 store
```

### DFD Level 2 — Detail Proses Kritis

#### DFD Level 2.1 — Dekomposisi P1: Akuisisi Data

```mermaid
graph TD
    GM["Google Maps"]
    ADM["Admin"]

    P1_1["P1.1<br/>Scraping Ulasan<br/>(01_scraping.py)"]
    P1_2["P1.2<br/>Quality Check<br/>(02_quality_check.py)"]
    P1_3["P1.3<br/>Combining Data<br/>(02_quality_check.py)"]

    DS1[("DS1<br/>CSV per Cabang<br/>(data/raw/)")]
    DS2[("DS2<br/>all_reviews.csv<br/>(data/combined/)")]
    DS_LOG[("DS_LOG<br/>pipeline_logs<br/>(PostgreSQL)")]

    ADM -->|"Target Cabang,<br/>Limit, Filter Tahun"| P1_1
    GM -->|"HTML Ulasan"| P1_1

    P1_1 -->|"CSV per cabang:<br/>nama, tanggal, rating, teks"| DS1
    P1_1 -->|"Log Eksekusi"| DS_LOG

    DS1 -->|"12 File CSV"| P1_2
    P1_2 -->|"Validasi Struktur,<br/>Hapus Duplikat,<br/>Hapus Null"| P1_3
    P1_3 -->|"Data Gabungan Bersih"| DS2
    P1_2 -->|"Log QC"| DS_LOG

    classDef ext fill:#FFE0B2,stroke:#F57C00,stroke-width:2px,color:#000
    classDef proc fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#000
    classDef store fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000

    class GM,ADM ext
    class P1_1,P1_2,P1_3 proc
    class DS1,DS2,DS_LOG store
```

#### DFD Level 2.3 — Dekomposisi P3: Pemodelan ML

```mermaid
graph TD
    DS3[("DS3<br/>preprocessed<br/>_reviews.csv")]

    P3_1["P3.1<br/>Inisialisasi<br/>Stratified K-Fold (K=5)"]
    P3_2["P3.2<br/>TF-IDF Vectorization<br/>(per Fold)"]
    P3_3["P3.3<br/>SMOTE Oversampling<br/>(Training Only)"]
    P3_4["P3.4<br/>Training SVM<br/>(Linear Kernel)"]
    P3_5["P3.5<br/>Training Naive Bayes<br/>(MultinomialNB)"]
    P3_6["P3.6<br/>Evaluasi K-Fold<br/>(Avg Metrics + CM)"]
    P3_7["P3.7<br/>Ekstraksi Aspek LDA<br/>(DBI Optimal)"]
    P3_8["P3.8<br/>Generate Word Cloud<br/>& Analisis Aspek"]

    DS4_SVM[("Model SVM<br/>(svm_model.pkl)")]
    DS4_NB[("Model NB<br/>(nb_model.pkl)")]
    DS4_TFIDF[("TF-IDF Vectorizer<br/>(tfidf_vectorizer.pkl)")]
    DS4_LDA[("Model LDA<br/>(lda_model.pkl)")]
    DS_RES[("Hasil Evaluasi<br/>(results/)")]

    DS3 -->|"Teks Preprocessed<br/>+ Label Sentimen"| P3_1
    P3_1 -->|"Split Train/Test<br/>per Fold"| P3_2
    P3_2 -->|"Vektor TF-IDF<br/>(Training)"| P3_3
    P3_2 -->|"Vektor TF-IDF<br/>(Test)"| P3_6
    P3_2 -->|"Vectorizer Terbaik"| DS4_TFIDF
    P3_3 -->|"Data Training<br/>Balanced"| P3_4
    P3_3 -->|"Data Training<br/>Balanced"| P3_5
    P3_4 -->|"Model SVM Terbaik"| DS4_SVM
    P3_5 -->|"Model NB Terbaik"| DS4_NB
    P3_4 -->|"Prediksi SVM"| P3_6
    P3_5 -->|"Prediksi NB"| P3_6
    P3_6 -->|"Accuracy, F1,<br/>Confusion Matrix"| DS_RES

    DS3 -->|"Teks Preprocessed"| P3_7
    P3_7 -->|"Topik Optimal<br/>(DBI Terendah)"| DS4_LDA
    P3_7 -->|"Label Aspek<br/>per Ulasan"| P3_8
    P3_8 -->|"Word Cloud PNG,<br/>Analisis Aspek"| DS_RES

    classDef proc fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#000
    classDef store fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000

    class P3_1,P3_2,P3_3,P3_4,P3_5,P3_6,P3_7,P3_8 proc
    class DS3,DS4_SVM,DS4_NB,DS4_TFIDF,DS4_LDA,DS_RES store
```

#### DFD Level 2.5 — Dekomposisi P5: Autentikasi & RBAC

```mermaid
graph TD
    ADM["Admin"]
    ANL["Analyst"]
    USR["User/Staf"]

    P5_1["P5.1<br/>Login<br/>(POST /api/auth/login)"]
    P5_2["P5.2<br/>Verifikasi Password<br/>(bcrypt)"]
    P5_3["P5.3<br/>Generate JWT Token<br/>(Access + Refresh)"]
    P5_4["P5.4<br/>Register User<br/>(POST /api/auth/register)"]
    P5_5["P5.5<br/>RBAC Middleware<br/>(@role_required)"]

    DS_USR[("Tabel users<br/>(PostgreSQL)")]

    ADM -->|"Email + Password"| P5_1
    ANL -->|"Email + Password"| P5_1
    USR -->|"Email + Password"| P5_1

    P5_1 -->|"Kredensial"| P5_2
    DS_USR -->|"Password Hash +<br/>Role + Status"| P5_2
    P5_2 -->|"User Valid"| P5_3
    P5_3 -->|"Access Token<br/>+ Refresh Token<br/>+ User Profile"| ADM
    P5_3 -->|"Access Token<br/>+ Refresh Token<br/>+ User Profile"| ANL
    P5_3 -->|"Access Token<br/>+ Refresh Token<br/>+ User Profile"| USR

    ADM -->|"Data User Baru<br/>(email, nama, role)"| P5_4
    P5_4 -->|"User Baru"| DS_USR

    P5_5 -->|"Cek Role dari<br/>JWT Claims"| DS_USR
    P5_3 -->|"Token dengan<br/>Role Claims"| P5_5

    classDef ext fill:#FFE0B2,stroke:#F57C00,stroke-width:2px,color:#000
    classDef proc fill:#BBDEFB,stroke:#1565C0,stroke-width:2px,color:#000
    classDef store fill:#C8E6C9,stroke:#2E7D32,stroke-width:2px,color:#000

    class ADM,ANL,USR ext
    class P5_1,P5_2,P5_3,P5_4,P5_5 proc
    class DS_USR store
```

---

## Legenda DFD

| Simbol | Arti |
|--------|------|
| Persegi panjang (rounded) | **Entitas Eksternal** — aktor di luar sistem |
| Persegi panjang (blue) | **Proses** — transformasi data |
| Silinder (green) | **Data Store** — penyimpanan data |
| Panah | **Aliran Data** — arah pergerakan data |

### Mapping Role → Hak Akses per Proses

| Proses | Admin | Analyst | User |
|--------|-------|---------|------|
| P1 — Akuisisi Data (Scraping) | ✅ Mulai/Stop | ❌ | ❌ |
| P2 — Analisis NLP | ✅ Trigger | ❌ | ❌ |
| P3 — Pemodelan ML (Retrain) | ✅ Trigger | ✅ Trigger | ❌ |
| P4 — Penyajian Data (Dashboard) | ✅ Full | ✅ Full | ✅ Read-only |
| P5 — Autentikasi (Register User) | ✅ CRUD User | ❌ | ❌ |
| P6 — Prediksi Real-time | ✅ Prediksi | ✅ Prediksi | ❌ |
