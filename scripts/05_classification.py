"""
05_classification.py — Klasifikasi Sentimen Menggunakan SVM & Naive Bayes
===========================================================================
Membaca data preprocessed, melakukan TF-IDF vectorization, melatih model,
mengevaluasi performa model, dan menyimpan hasil serta modelnya.
"""

import pandas as pd
import numpy as np
import os
import joblib
import time
import logging
import sys
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

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

# Buat folder jika belum ada
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def plot_confusion_matrix(cm, classes, title, filename):
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.ylabel('Label Sebenarnya (True)')
    plt.xlabel('Label Prediksi (Predicted)')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, filename), dpi=300)
    plt.close()

def main():
    log.info("=== TAHAP 4: KLASIFIKASI SENTIMEN (SVM & NAIVE BAYES) ===")
    
    # 1. Load Data
    log.info(f"Membaca dataset preprocessed: {INPUT_FILE}")
    if not os.path.exists(INPUT_FILE):
        log.error(f"File tidak ditemukan: {INPUT_FILE}")
        log.info("Pastikan Anda sudah menjalankan scripts/04_preprocessing.py.")
        return
        
    df = pd.read_csv(INPUT_FILE)
    
    # Menghapus data null akibat dari preprocessing (misal teks yang cuma berisi emoji dan setelah di-clean jadi kosong)
    df = df.dropna(subset=['text_preprocessed', 'sentimen'])
    
    X = df['text_preprocessed'].astype(str)
    y = df['sentimen'] 
    
    log.info(f"Total data siap untuk training dan testing: {len(df)}")
    
    # 2. TF-IDF Vectorization
    log.info("Memulai ekstraksi fitur teks dengan TF-IDF Vectorization...")
    # Membatasi max_features ke 5000 untuk mencegah dimensi terlalu besar dan memakan memori berlebih
    vectorizer = TfidfVectorizer(max_features=5000) 
    X_tfidf = vectorizer.fit_transform(X)
    
    # Simpan vectorizer untuk digunakan pada Prediksi Real-time di Dashboard nanti
    vectorizer_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')
    joblib.dump(vectorizer, vectorizer_path)
    log.info(f"Vectorizer TF-IDF berhasil disimpan di: {vectorizer_path}")
    
    # 3. Train-Test Split (80:20)
    log.info("Membagi data menjadi Training (80%) dan Testing (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42, stratify=y)
    
    log.info(f"Ukuran Data Latih (Train): {X_train.shape[0]} baris")
    log.info(f"Ukuran Data Uji (Test): {X_test.shape[0]} baris")
    
    # 4. Training SVM
    log.info("\n[1/2] Melatih model Support Vector Machine (SVM)...")
    start_time = time.time()
    # Menggunakan kernel linear karena efisien untuk Text Classification / TF-IDF
    svm_model = SVC(kernel='linear', random_state=42)
    svm_model.fit(X_train, y_train)
    svm_time = time.time() - start_time
    log.info(f"Training SVM selesai dalam waktu {svm_time:.2f} detik.")
    
    # Evaluasi SVM
    y_pred_svm = svm_model.predict(X_test)
    svm_acc = accuracy_score(y_test, y_pred_svm)
    svm_prec = precision_score(y_test, y_pred_svm, pos_label='positif')
    svm_rec = recall_score(y_test, y_pred_svm, pos_label='positif')
    svm_f1 = f1_score(y_test, y_pred_svm, pos_label='positif')
    
    # 5. Training Naive Bayes
    log.info("\n[2/2] Melatih model Naive Bayes (MultinomialNB)...")
    start_time = time.time()
    nb_model = MultinomialNB()
    nb_model.fit(X_train, y_train)
    nb_time = time.time() - start_time
    log.info(f"Training Naive Bayes selesai dalam waktu {nb_time:.2f} detik.")
    
    # Evaluasi NB
    y_pred_nb = nb_model.predict(X_test)
    nb_acc = accuracy_score(y_test, y_pred_nb)
    nb_prec = precision_score(y_test, y_pred_nb, pos_label='positif')
    nb_rec = recall_score(y_test, y_pred_nb, pos_label='positif')
    nb_f1 = f1_score(y_test, y_pred_nb, pos_label='positif')
    
    # 6. Simpan Model ML
    log.info("\nMenyimpan model Machine Learning...")
    svm_path = os.path.join(MODELS_DIR, 'svm_model.pkl')
    nb_path = os.path.join(MODELS_DIR, 'nb_model.pkl')
    joblib.dump(svm_model, svm_path)
    joblib.dump(nb_model, nb_path)
    log.info(f"Model SVM disimpan di: {svm_path}")
    log.info(f"Model NB disimpan di: {nb_path}")
    
    # 7. Simpan Hasil Evaluasi (Metrics & Visualisasi)
    log.info("\nMembuat visualisasi dan menyimpan laporan hasil evaluasi...")
    labels = ['negatif', 'positif']
    
    # Plot Confusion Matrix
    plot_confusion_matrix(confusion_matrix(y_test, y_pred_svm, labels=labels), labels, "Confusion Matrix - SVM", "cm_svm.png")
    plot_confusion_matrix(confusion_matrix(y_test, y_pred_nb, labels=labels), labels, "Confusion Matrix - Naive Bayes", "cm_nb.png")
    
    # Tulis laporan ke text
    report_path = os.path.join(RESULTS_DIR, 'classification_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== LAPORAN PERBANDINGAN PERFORMA MODEL ===\n\n")
        
        f.write("--- 1. SUPPORT VECTOR MACHINE (SVM) ---\n")
        f.write(f"Waktu Training : {svm_time:.2f} detik\n")
        f.write(f"Accuracy       : {svm_acc:.4f}\n")
        f.write(f"Precision      : {svm_prec:.4f}\n")
        f.write(f"Recall         : {svm_rec:.4f}\n")
        f.write(f"F1-Score       : {svm_f1:.4f}\n")
        f.write("\nClassification Report (SVM):\n")
        f.write(classification_report(y_test, y_pred_svm))
        f.write("\n-------------------------------------------------\n\n")
        
        f.write("--- 2. NAIVE BAYES (MULTINOMIAL) ---\n")
        f.write(f"Waktu Training : {nb_time:.2f} detik\n")
        f.write(f"Accuracy       : {nb_acc:.4f}\n")
        f.write(f"Precision      : {nb_prec:.4f}\n")
        f.write(f"Recall         : {nb_rec:.4f}\n")
        f.write(f"F1-Score       : {nb_f1:.4f}\n")
        f.write("\nClassification Report (Naive Bayes):\n")
        f.write(classification_report(y_test, y_pred_nb))
        
    log.info(f"Laporan evaluasi berhasil diekspor ke: {report_path}")
    log.info("Visualisasi Confusion Matrix tersimpan di folder 'results/'")
    log.info("\n✅ Tahap 4 (Klasifikasi) SELESAI SELURUHNYA!")

if __name__ == "__main__":
    main()
