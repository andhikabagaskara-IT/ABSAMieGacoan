"""
05_classification.py — Klasifikasi Sentimen dengan Stratified K-Fold Cross-Validation
======================================================================================
Alur Proses:
  1. Membaca data preprocessed
  2. Inisialisasi Stratified K-Fold (K=5)
  3. Loop K-Fold:
     a) TF-IDF Vectorization  — dilakukan di dalam tiap fold (mencegah data leakage)
     b) SMOTE                 — hanya diterapkan pada data Training
     c) Training Model        — SVM & Naive Bayes
     d) Prediksi & Validasi   — pada data Testing murni (tanpa SMOTE)
  4. Evaluasi Akhir: Rata-rata Accuracy, Precision, Recall, F1-Score dari semua fold
  5. Simpan model terbaik & laporan evaluasi
"""

import pandas as pd
import numpy as np
import os
import joblib
import time
import logging
import sys
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
from imblearn.over_sampling import SMOTE

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

# Buat folder jika belum ada
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# ===================== KONFIGURASI =====================
K_FOLDS = 5          # Jumlah K untuk Stratified K-Fold
MAX_FEATURES = 5000  # Batas fitur TF-IDF
RANDOM_STATE = 42    # Seed untuk reproduksibilitas
# =======================================================


def plot_confusion_matrix(cm, classes, title, filename):
    """Membuat dan menyimpan visualisasi Confusion Matrix."""
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=classes, yticklabels=classes)
    plt.title(title)
    plt.ylabel('Label Sebenarnya (True)')
    plt.xlabel('Label Prediksi (Predicted)')
    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, filename), dpi=300)
    plt.close()


def plot_fold_metrics(fold_metrics_svm, fold_metrics_nb, metric_names):
    """Membuat grafik perbandingan metrik per fold untuk SVM dan NB."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Perbandingan Metrik Per Fold (Stratified {K_FOLDS}-Fold CV)', fontsize=14, fontweight='bold')

    folds = list(range(1, K_FOLDS + 1))

    for idx, metric in enumerate(metric_names):
        ax = axes[idx // 2][idx % 2]
        svm_vals = [m[metric] for m in fold_metrics_svm]
        nb_vals = [m[metric] for m in fold_metrics_nb]

        ax.plot(folds, svm_vals, 'o-', color='#2196F3', linewidth=2, markersize=8, label='SVM')
        ax.plot(folds, nb_vals, 's--', color='#FF5722', linewidth=2, markersize=8, label='Naive Bayes')
        ax.set_title(metric.capitalize(), fontsize=12, fontweight='bold')
        ax.set_xlabel('Fold')
        ax.set_ylabel('Skor')
        ax.set_xticks(folds)
        ax.set_ylim([0.0, 1.05])
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(os.path.join(RESULTS_DIR, 'kfold_metrics_comparison.png'), dpi=300)
    plt.close()


def main():
    log.info("=" * 70)
    log.info("  TAHAP 4: KLASIFIKASI SENTIMEN — Stratified K-Fold Cross-Validation")
    log.info("=" * 70)

    # ─── 1. Load Data ───────────────────────────────────────────────────────
    log.info(f"Membaca dataset preprocessed: {INPUT_FILE}")
    if not os.path.exists(INPUT_FILE):
        log.error(f"File tidak ditemukan: {INPUT_FILE}")
        log.info("Pastikan Anda sudah menjalankan scripts/04_preprocessing.py.")
        return

    df = pd.read_csv(INPUT_FILE)
    df = df.dropna(subset=['text_preprocessed', 'sentimen'])

    X = df['text_preprocessed'].astype(str).values
    y = df['sentimen'].values

    # Encode label: positif = 1, negatif = 0 (untuk SMOTE compatibility)
    label_map = {'positif': 1, 'negatif': 0}
    label_map_inv = {v: k for k, v in label_map.items()}
    y_encoded = np.array([label_map.get(lbl, -1) for lbl in y])

    # Hapus data dengan label tidak dikenal
    valid_mask = y_encoded >= 0
    X = X[valid_mask]
    y_encoded = y_encoded[valid_mask]

    log.info(f"Total data siap untuk Stratified K-Fold: {len(X)}")
    log.info(f"Distribusi label: Positif={np.sum(y_encoded == 1)}, Negatif={np.sum(y_encoded == 0)}")
    log.info(f"Rasio Positif:Negatif = {np.sum(y_encoded == 1)/len(y_encoded)*100:.1f}% : {np.sum(y_encoded == 0)/len(y_encoded)*100:.1f}%")

    # ─── 2. Inisialisasi Stratified K-Fold ──────────────────────────────────
    skf = StratifiedKFold(n_splits=K_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    log.info(f"\nStratified K-Fold diinisialisasi dengan K={K_FOLDS}")

    # Wadah untuk menyimpan metrik per fold
    fold_metrics_svm = []
    fold_metrics_nb = []

    # Wadah untuk confusion matrix keseluruhan (akumulasi semua fold)
    all_y_true = []
    all_y_pred_svm = []
    all_y_pred_nb = []

    # Track model terbaik berdasarkan F1-Score
    best_svm_f1 = 0
    best_nb_f1 = 0
    best_svm_model = None
    best_nb_model = None
    best_vectorizer = None

    total_start_time = time.time()

    # ─── 3. Loop Stratified K-Fold ──────────────────────────────────────────
    for fold_idx, (train_index, test_index) in enumerate(skf.split(X, y_encoded), 1):
        log.info(f"\n{'─'*60}")
        log.info(f"  FOLD {fold_idx}/{K_FOLDS}")
        log.info(f"{'─'*60}")

        X_train_text, X_test_text = X[train_index], X[test_index]
        y_train, y_test = y_encoded[train_index], y_encoded[test_index]

        log.info(f"  Data Train: {len(X_train_text)} | Data Test: {len(X_test_text)}")
        log.info(f"  Train - Positif: {np.sum(y_train == 1)}, Negatif: {np.sum(y_train == 0)}")
        log.info(f"  Test  - Positif: {np.sum(y_test == 1)}, Negatif: {np.sum(y_test == 0)}")

        # ─── 3a. TF-IDF Vectorization (di dalam fold untuk mencegah data leakage) ──
        log.info("  [a] TF-IDF Vectorization (fit pada train, transform pada test)...")
        fold_vectorizer = TfidfVectorizer(max_features=MAX_FEATURES)
        X_train_tfidf = fold_vectorizer.fit_transform(X_train_text)
        X_test_tfidf = fold_vectorizer.transform(X_test_text)

        # ─── 3b. SMOTE (hanya pada data Training) ──────────────────────────
        log.info("  [b] SMOTE Oversampling pada data Training...")
        smote = SMOTE(random_state=RANDOM_STATE)
        X_train_smote, y_train_smote = smote.fit_resample(X_train_tfidf, y_train)
        log.info(f"      Sebelum SMOTE: Positif={np.sum(y_train == 1)}, Negatif={np.sum(y_train == 0)}")
        log.info(f"      Sesudah SMOTE: Positif={np.sum(y_train_smote == 1)}, Negatif={np.sum(y_train_smote == 0)}")

        # ─── 3c. Training Model SVM ────────────────────────────────────────
        log.info("  [c] Training SVM (kernel=linear)...")
        start = time.time()
        svm_model = SVC(kernel='linear', random_state=RANDOM_STATE)
        svm_model.fit(X_train_smote, y_train_smote)
        svm_time = time.time() - start
        log.info(f"      SVM training selesai dalam {svm_time:.2f} detik")

        # ─── Training Model Naive Bayes ────────────────────────────────────
        log.info("  [c] Training Naive Bayes (MultinomialNB)...")
        start = time.time()
        nb_model = MultinomialNB()
        nb_model.fit(X_train_smote, y_train_smote)
        nb_time = time.time() - start
        log.info(f"      NB training selesai dalam {nb_time:.2f} detik")

        # ─── 3d. Prediksi & Validasi (data test murni tanpa SMOTE) ─────────
        log.info("  [d] Prediksi & Validasi pada data Testing (tanpa SMOTE)...")

        y_pred_svm = svm_model.predict(X_test_tfidf)
        y_pred_nb = nb_model.predict(X_test_tfidf)

        # Hitung metrik SVM untuk fold ini
        svm_metrics = {
            'accuracy':  accuracy_score(y_test, y_pred_svm),
            'precision': precision_score(y_test, y_pred_svm, average='weighted', zero_division=0),
            'recall':    recall_score(y_test, y_pred_svm, average='weighted', zero_division=0),
            'f1_score':  f1_score(y_test, y_pred_svm, average='weighted', zero_division=0),
            'train_time': svm_time
        }
        fold_metrics_svm.append(svm_metrics)

        # Hitung metrik NB untuk fold ini
        nb_metrics = {
            'accuracy':  accuracy_score(y_test, y_pred_nb),
            'precision': precision_score(y_test, y_pred_nb, average='weighted', zero_division=0),
            'recall':    recall_score(y_test, y_pred_nb, average='weighted', zero_division=0),
            'f1_score':  f1_score(y_test, y_pred_nb, average='weighted', zero_division=0),
            'train_time': nb_time
        }
        fold_metrics_nb.append(nb_metrics)

        log.info(f"      SVM  → Acc: {svm_metrics['accuracy']:.4f} | Prec: {svm_metrics['precision']:.4f} | Rec: {svm_metrics['recall']:.4f} | F1: {svm_metrics['f1_score']:.4f}")
        log.info(f"      NB   → Acc: {nb_metrics['accuracy']:.4f} | Prec: {nb_metrics['precision']:.4f} | Rec: {nb_metrics['recall']:.4f} | F1: {nb_metrics['f1_score']:.4f}")

        # Akumulasi prediksi untuk confusion matrix keseluruhan
        all_y_true.extend(y_test.tolist())
        all_y_pred_svm.extend(y_pred_svm.tolist())
        all_y_pred_nb.extend(y_pred_nb.tolist())

        # Simpan model terbaik berdasarkan F1-Score
        if svm_metrics['f1_score'] > best_svm_f1:
            best_svm_f1 = svm_metrics['f1_score']
            best_svm_model = svm_model
            best_vectorizer = fold_vectorizer  # Simpan vectorizer dari fold terbaik

        if nb_metrics['f1_score'] > best_nb_f1:
            best_nb_f1 = nb_metrics['f1_score']
            best_nb_model = nb_model

    total_time = time.time() - total_start_time

    # ─── 4. Evaluasi Akhir: Rata-rata Metrik dari Semua Fold ────────────────
    log.info(f"\n{'='*70}")
    log.info("  EVALUASI AKHIR: RATA-RATA PERFORMA DARI SEMUA FOLD")
    log.info(f"{'='*70}")

    metric_names = ['accuracy', 'precision', 'recall', 'f1_score']

    avg_svm = {m: np.mean([f[m] for f in fold_metrics_svm]) for m in metric_names}
    std_svm = {m: np.std([f[m] for f in fold_metrics_svm]) for m in metric_names}
    avg_nb = {m: np.mean([f[m] for f in fold_metrics_nb]) for m in metric_names}
    std_nb = {m: np.std([f[m] for f in fold_metrics_nb]) for m in metric_names}

    log.info(f"\n  ┌─────────────────────────────────────────────────┐")
    log.info(f"  │          SUPPORT VECTOR MACHINE (SVM)           │")
    log.info(f"  ├─────────────────────────────────────────────────┤")
    log.info(f"  │  Accuracy  : {avg_svm['accuracy']:.4f} ± {std_svm['accuracy']:.4f}        │")
    log.info(f"  │  Precision : {avg_svm['precision']:.4f} ± {std_svm['precision']:.4f}        │")
    log.info(f"  │  Recall    : {avg_svm['recall']:.4f} ± {std_svm['recall']:.4f}        │")
    log.info(f"  │  F1-Score  : {avg_svm['f1_score']:.4f} ± {std_svm['f1_score']:.4f}        │")
    log.info(f"  └─────────────────────────────────────────────────┘")

    log.info(f"\n  ┌─────────────────────────────────────────────────┐")
    log.info(f"  │          NAIVE BAYES (MULTINOMIAL)               │")
    log.info(f"  ├─────────────────────────────────────────────────┤")
    log.info(f"  │  Accuracy  : {avg_nb['accuracy']:.4f} ± {std_nb['accuracy']:.4f}        │")
    log.info(f"  │  Precision : {avg_nb['precision']:.4f} ± {std_nb['precision']:.4f}        │")
    log.info(f"  │  Recall    : {avg_nb['recall']:.4f} ± {std_nb['recall']:.4f}        │")
    log.info(f"  │  F1-Score  : {avg_nb['f1_score']:.4f} ± {std_nb['f1_score']:.4f}        │")
    log.info(f"  └─────────────────────────────────────────────────┘")

    # ─── 5. Simpan Model Terbaik ────────────────────────────────────────────
    log.info("\nMenyimpan model terbaik (best fold) ke direktori models/...")

    svm_path = os.path.join(MODELS_DIR, 'svm_model.pkl')
    nb_path = os.path.join(MODELS_DIR, 'nb_model.pkl')
    vectorizer_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')

    joblib.dump(best_svm_model, svm_path)
    joblib.dump(best_nb_model, nb_path)
    joblib.dump(best_vectorizer, vectorizer_path)

    log.info(f"  Model SVM disimpan di: {svm_path}")
    log.info(f"  Model NB disimpan di: {nb_path}")
    log.info(f"  Vectorizer TF-IDF disimpan di: {vectorizer_path}")

    # ─── 6. Confusion Matrix Keseluruhan (Akumulasi Semua Fold) ─────────────
    log.info("\nMembuat Confusion Matrix (akumulasi seluruh fold)...")

    all_y_true = np.array(all_y_true)
    all_y_pred_svm = np.array(all_y_pred_svm)
    all_y_pred_nb = np.array(all_y_pred_nb)

    class_labels_encoded = [0, 1]
    class_labels_display = ['negatif', 'positif']

    cm_svm = confusion_matrix(all_y_true, all_y_pred_svm, labels=class_labels_encoded)
    cm_nb = confusion_matrix(all_y_true, all_y_pred_nb, labels=class_labels_encoded)

    plot_confusion_matrix(cm_svm, class_labels_display,
                          f"Confusion Matrix — SVM\n(Stratified {K_FOLDS}-Fold CV, Akumulasi Seluruh Fold)",
                          "cm_svm.png")
    plot_confusion_matrix(cm_nb, class_labels_display,
                          f"Confusion Matrix — Naive Bayes\n(Stratified {K_FOLDS}-Fold CV, Akumulasi Seluruh Fold)",
                          "cm_nb.png")

    # ─── 7. Grafik Perbandingan Metrik Per Fold ─────────────────────────────
    log.info("Membuat grafik perbandingan metrik per fold...")
    plot_fold_metrics(fold_metrics_svm, fold_metrics_nb, metric_names)

    # ─── 8. Tulis Laporan Evaluasi ke File ──────────────────────────────────
    log.info("Menulis laporan evaluasi lengkap...")

    report_path = os.path.join(RESULTS_DIR, 'classification_report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("  LAPORAN KLASIFIKASI SENTIMEN\n")
        f.write(f"  Metode: Stratified {K_FOLDS}-Fold Cross-Validation + SMOTE\n")
        f.write("=" * 70 + "\n\n")

        f.write(f"Total data      : {len(X)}\n")
        f.write(f"Jumlah Fold (K) : {K_FOLDS}\n")
        f.write(f"Max TF-IDF feat : {MAX_FEATURES}\n")
        f.write(f"SMOTE           : Diterapkan hanya pada data Training tiap fold\n")
        f.write(f"Total waktu     : {total_time:.2f} detik ({total_time/60:.2f} menit)\n\n")

        f.write("-" * 70 + "\n")
        f.write("  DETAIL METRIK PER FOLD\n")
        f.write("-" * 70 + "\n\n")

        for fold_i in range(K_FOLDS):
            f.write(f"  Fold {fold_i+1}:\n")
            f.write(f"    SVM → Acc: {fold_metrics_svm[fold_i]['accuracy']:.4f} | "
                    f"Prec: {fold_metrics_svm[fold_i]['precision']:.4f} | "
                    f"Rec: {fold_metrics_svm[fold_i]['recall']:.4f} | "
                    f"F1: {fold_metrics_svm[fold_i]['f1_score']:.4f} | "
                    f"Time: {fold_metrics_svm[fold_i]['train_time']:.2f}s\n")
            f.write(f"    NB  → Acc: {fold_metrics_nb[fold_i]['accuracy']:.4f} | "
                    f"Prec: {fold_metrics_nb[fold_i]['precision']:.4f} | "
                    f"Rec: {fold_metrics_nb[fold_i]['recall']:.4f} | "
                    f"F1: {fold_metrics_nb[fold_i]['f1_score']:.4f} | "
                    f"Time: {fold_metrics_nb[fold_i]['train_time']:.2f}s\n\n")

        f.write("-" * 70 + "\n")
        f.write("  RATA-RATA METRIK (MEAN ± STD)\n")
        f.write("-" * 70 + "\n\n")

        f.write("  1. SUPPORT VECTOR MACHINE (SVM)\n")
        f.write(f"     Accuracy  : {avg_svm['accuracy']:.4f} ± {std_svm['accuracy']:.4f}\n")
        f.write(f"     Precision : {avg_svm['precision']:.4f} ± {std_svm['precision']:.4f}\n")
        f.write(f"     Recall    : {avg_svm['recall']:.4f} ± {std_svm['recall']:.4f}\n")
        f.write(f"     F1-Score  : {avg_svm['f1_score']:.4f} ± {std_svm['f1_score']:.4f}\n\n")

        f.write("  2. NAIVE BAYES (MULTINOMIAL)\n")
        f.write(f"     Accuracy  : {avg_nb['accuracy']:.4f} ± {std_nb['accuracy']:.4f}\n")
        f.write(f"     Precision : {avg_nb['precision']:.4f} ± {std_nb['precision']:.4f}\n")
        f.write(f"     Recall    : {avg_nb['recall']:.4f} ± {std_nb['recall']:.4f}\n")
        f.write(f"     F1-Score  : {avg_nb['f1_score']:.4f} ± {std_nb['f1_score']:.4f}\n\n")

        f.write("-" * 70 + "\n")
        f.write("  CLASSIFICATION REPORT (Akumulasi Semua Fold)\n")
        f.write("-" * 70 + "\n\n")

        # Konversi kembali ke label string untuk classification report
        y_true_labels = [label_map_inv[v] for v in all_y_true]
        y_pred_svm_labels = [label_map_inv[v] for v in all_y_pred_svm]
        y_pred_nb_labels = [label_map_inv[v] for v in all_y_pred_nb]

        f.write("  SVM:\n")
        f.write(classification_report(y_true_labels, y_pred_svm_labels, digits=4))
        f.write("\n\n")
        f.write("  Naive Bayes:\n")
        f.write(classification_report(y_true_labels, y_pred_nb_labels, digits=4))

        f.write("\n" + "-" * 70 + "\n")
        f.write("  CONFUSION MATRIX (Akumulasi Semua Fold)\n")
        f.write("-" * 70 + "\n\n")
        f.write("  SVM:\n")
        f.write(f"  {cm_svm}\n\n")
        f.write("  Naive Bayes:\n")
        f.write(f"  {cm_nb}\n")

    log.info(f"Laporan evaluasi disimpan di: {report_path}")

    # ─── 9. Export Metrik K-Fold ke JSON (untuk dashboard) ──────────────────
    kfold_results = {
        'k_folds': K_FOLDS,
        'total_data': int(len(X)),
        'method': f'Stratified {K_FOLDS}-Fold Cross-Validation + SMOTE',
        'svm': {
            'fold_metrics': fold_metrics_svm,
            'average': {k: float(v) for k, v in avg_svm.items()},
            'std': {k: float(v) for k, v in std_svm.items()},
            'confusion_matrix': cm_svm.tolist()
        },
        'nb': {
            'fold_metrics': fold_metrics_nb,
            'average': {k: float(v) for k, v in avg_nb.items()},
            'std': {k: float(v) for k, v in std_nb.items()},
            'confusion_matrix': cm_nb.tolist()
        }
    }

    kfold_json_path = os.path.join(RESULTS_DIR, 'kfold_results.json')
    with open(kfold_json_path, 'w', encoding='utf-8') as f:
        json.dump(kfold_results, f, ensure_ascii=False, indent=4)

    log.info(f"Hasil K-Fold Cross-Validation diekspor ke JSON: {kfold_json_path}")
    log.info(f"\nTotal waktu eksekusi: {total_time:.2f} detik ({total_time/60:.2f} menit)")
    log.info("✅ Tahap 4 (Klasifikasi Sentimen — Stratified K-Fold CV) SELESAI!")


if __name__ == "__main__":
    main()
