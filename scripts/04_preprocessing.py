import pandas as pd
import numpy as np
import re
import os
import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Download NLTK data (run once)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, 'data', 'labeled', 'labeled_reviews.csv')
OUTPUT_DIR = os.path.join(BASE_DIR, 'data', 'preprocessed')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'preprocessed_reviews.csv')

# Create output dir if not exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Stemmer
print("Initializing Sastrawi Stemmer (this may take a few seconds)...")
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# Initialize Stopwords
list_stopwords = set(stopwords.words('indonesian'))
# Add some custom stopwords if needed
custom_stopwords = {'nya', 'sih', 'ya', 'aja', 'kok', 'deh', 'kan', 'dong', 'mah', 'buat', 'yang', 'di', 'ke', 'dari', 'dan', 'atau', 'yg', 'ga'}
list_stopwords.update(custom_stopwords)

# Kamus Normalisasi (Slang / Singkatan)
# (Sebaiknya bisa pakai file csv eksternal, tapi untuk awal kita pakai dict ini)
slang_dict = {
    "yg": "yang",
    "gak": "tidak",
    "ga": "tidak",
    "nggak": "tidak",
    "gk": "tidak",
    "bgt": "banget",
    "bgtt": "banget",
    "udh": "sudah",
    "udah": "sudah",
    "dgn": "dengan",
    "krn": "karena",
    "kalo": "kalau",
    "klo": "kalau",
    "trus": "terus",
    "tp": "tapi",
    "tpi": "tapi",
    "sm": "sama",
    "bkn": "bukan",
    "jd": "jadi",
    "jdi": "jadi",
    "bnyk": "banyak",
    "pke": "pakai",
    "pake": "pakai",
    "utk": "untuk",
    "pdhl": "padahal",
    "bgs": "bagus",
    "lg": "lagi",
    "kl": "kalau",
    "tdk": "tidak",
    "blm": "belum"
}

def clean_text(text):
    """Tahap 1: Cleaning Data"""
    if pd.isna(text):
        return ""
    text = str(text)
    # Hapus URL
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Hapus mention @ dan hashtag #
    text = re.sub(r'\@\w+|\#\w+', '', text)
    # Hapus angka
    text = re.sub(r'\d+', '', text)
    # Hapus karakter spesial / tanda baca (hanya simpan huruf dan spasi)
    text = re.sub(r'[^\w\s]', ' ', text)
    # Hapus whitespace di awal dan akhir, serta whitespace ganda di tengah
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def case_folding(text):
    """Tahap 2: Case Folding"""
    return text.lower()

def normalize_text(text):
    """Tahap 3: Normalization"""
    words = text.split()
    normalized_words = [slang_dict.get(word, word) for word in words]
    return " ".join(normalized_words)

def tokenize_text(text):
    """Tahap 4: Tokenizing"""
    return word_tokenize(text)

def remove_stopwords(tokens):
    """Tahap 5: Stopword Removal"""
    return [word for word in tokens if word not in list_stopwords]

def stem_text(tokens):
    """Tahap 6: Stemming"""
    # Sastrawi expects string
    text = " ".join(tokens)
    return stemmer.stem(text)

def preprocess_pipeline(df, text_column):
    print(f"\nMemulai preprocessing untuk {len(df)} data...")
    start_time = time.time()
    
    # Copy DataFrame
    df_processed = df.copy()
    
    print("1/6 Cleaning Data...")
    df_processed['text_clean'] = df_processed[text_column].apply(clean_text)
    
    print("2/6 Case Folding...")
    df_processed['text_casefold'] = df_processed['text_clean'].apply(case_folding)
    
    print("3/6 Normalisasi Slang...")
    df_processed['text_normalized'] = df_processed['text_casefold'].apply(normalize_text)
    
    # NOTE: Tokenizing bisa sangat lambat untuk dataset besar
    print("4/6 Tokenizing (NLTK)...")
    df_processed['text_tokenized'] = df_processed['text_normalized'].apply(tokenize_text)
    
    print("5/6 Stopword Removal...")
    df_processed['text_stopword_removed'] = df_processed['text_tokenized'].apply(remove_stopwords)
    
    # PERHATIAN: Stemming Sastrawi sangat lambat jika dilakukan pada data besar (60k baris).
    print("6/6 Stemming (Ini akan memakan waktu paling lama)...")
    
    stemmed_results = []
    total_data = len(df_processed)
    
    # Logika looping untuk progress bar sederhana
    for i, tokens in enumerate(df_processed['text_stopword_removed']):
        if i > 0 and i % 500 == 0:
            print(f"  Progress Stemming: {i}/{total_data} ({(i/total_data)*100:.1f}%)")
        stemmed_results.append(stem_text(tokens))
    
    df_processed['text_preprocessed'] = stemmed_results
    
    # Menghapus data yang menjadi kosong setelah preprocessing
    initial_len = len(df_processed)
    df_processed = df_processed[df_processed['text_preprocessed'].str.strip() != '']
    final_len = len(df_processed)
    print(f"\nMenghapus {initial_len - final_len} ulasan yang menjadi kosong setelah text diproses.")
    
    end_time = time.time()
    print(f"Preprocessing selesai dalam {(end_time - start_time)/60:.2f} menit!")
    return df_processed

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: File input tidak ditemukan di {INPUT_FILE}")
        print("Silakan jalankan script 03_labeling.py terlebih dahulu.")
        return

    print("=== TAHAP 3: PREPROCESSING DATA ===")
    print(f"Membaca dataset dari: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)
    
    # Sebagai opsional, kalau mau mencoba dengan subset kecil dulu, bisa di-uncomment:
    # df = df.head(100) # Untuk test jalan cepat
    
    print(f"Total data yang akan diproses: {len(df)}")
    
    # Jalankan pipeline text prepocessing
    df_preprocessed = preprocess_pipeline(df, text_column='teks_komentar')
    
    # Simpan hasil
    print(f"\nMenyimpan hasil ke: {OUTPUT_FILE}")
    df_preprocessed.to_csv(OUTPUT_FILE, index=False)
    print("Selesai!")

if __name__ == "__main__":
    main()
