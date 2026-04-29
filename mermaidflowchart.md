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
        G --> H[Dashboard VueJS<br/>Visualisasi Interaktif]
    end

    classDef python fill:#4FC3F7,stroke:#0288D1,stroke-width:2px,color:#000
    classDef output fill:#81C784,stroke:#388E3C,stroke-width:2px,color:#000
    classDef ui fill:#FFB74D,stroke:#F57C00,stroke-width:2px,color:#000

    class A,B,C,D,E,F,G python
    class H ui
```

## Deskripsi Flow
1. **Scraping**: Pengumpulan data mentah dari ulasan Google Maps.
2. **Quality Check**: Pembersihan duplikat, pengecekan nilai null, dan menggabungkan semua data.
3. **Labeling**: Pelabelan ke kelas Positif, Negatif, Netral berdasarkan rating bintang.
4. **Preprocessing**: Pembersihan teks, stemming, tokenizing.
5. **Classification**: Melatih model dengan mengatasi ketidakseimbangan data (SMOTE) dan divalidasi dengan K-Fold untuk hasil objektif.
6. **LDA Aspect**: Mengekstrak topik yang sering dibicarakan (Rasa, Harga, dll).
7. **Export**: Mempersiapkan dataset JSON akhir.
8. **Dashboard**: Menampilkan metrik, analisis cabang, performa algoritma, dan tool sentimen.
