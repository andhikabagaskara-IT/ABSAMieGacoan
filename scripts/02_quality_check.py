import os
import glob
import pandas as pd
import numpy as np

# Tentukan direktori berbasis lokasi script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
COMBINED_DIR = os.path.join(BASE_DIR, "data", "combined")
OUTPUT_FILE = os.path.join(COMBINED_DIR, "all_reviews.csv")

def main():
    import sys
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
        
    # Buat folder output jika belum ada
    os.makedirs(COMBINED_DIR, exist_ok=True)
    
    # Ambil semua file CSV di folder raw
    csv_files = glob.glob(os.path.join(RAW_DIR, "*.csv"))
    
    if not csv_files:
        print(f"❌ Tidak ada file CSV ditemukan di direktori {RAW_DIR}")
        return
        
    all_data = []
    total_raw_rows = 0
    total_dropped_nulls = 0
    total_dropped_duplicates = 0
    
    print("=" * 60)
    print("🔍 MULAI PROSES QUALITY CHECK & COMBINING")
    print("=" * 60)
    
    for file in csv_files:
        branch_name = os.path.basename(file).replace(".csv", "").replace("_", " ")
        try:
            df = pd.read_csv(file)
            
            # Cek kolom wajib
            required_cols = ["nama_cabang", "nama_pelanggan", "tanggal_ulasan", "rating", "teks_komentar"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print(f"⚠️ Melewati {branch_name} karena kurang kolom: {missing_cols}")
                continue
                
            raw_rows = len(df)
            total_raw_rows += raw_rows
            
            # 1. Menghapus baris yang 'teks_komentar' nya NaN atau string kosong
            # Ganti spasi kosong dengan NaN
            if df["teks_komentar"].dtype == object:
                df["teks_komentar"] = df["teks_komentar"].replace(r'^\s*$', np.nan, regex=True)
            df_cleaned = df.dropna(subset=["teks_komentar", "rating"])
            dropped_nulls = raw_rows - len(df_cleaned)
            total_dropped_nulls += dropped_nulls
            
            # 2. Menghapus duplikat
            # Kita anggap duplikat jika kombinasi nama_pelanggan, rating, dan teks_komentar sama
            df_dedup = df_cleaned.drop_duplicates(subset=["nama_pelanggan", "rating", "teks_komentar"])
            dropped_duplicates = len(df_cleaned) - len(df_dedup)
            total_dropped_duplicates += dropped_duplicates
            
            final_rows = len(df_dedup)
            
            # Statistik rating per cabang
            rating_counts = df_dedup["rating"].value_counts().sort_index().to_dict()
            
            print(f"✅ {branch_name}")
            print(f"   - Baris mentah: {raw_rows}")
            print(f"   - Dihapus (Teks kosong): {dropped_nulls}")
            print(f"   - Dihapus (Duplikat): {dropped_duplicates}")
            print(f"   - Baris bersih: {final_rows}")
            print(f"   - Distribusi Rating: {rating_counts}\n")
            
            all_data.append(df_dedup)
            
        except Exception as e:
            print(f"❌ Gagal memproses file {file}: {e}")
            
    if all_data:
        # Gabungkan semua data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Simpan ke file output
        combined_df.to_csv(OUTPUT_FILE, index=False)
        
        print("=" * 60)
        print("📊 RINGKASAN HASIL")
        print("=" * 60)
        print(f"Total Baris Mentah         : {total_raw_rows}")
        print(f"Total Dihapus (Kosong)     : {total_dropped_nulls}")
        print(f"Total Dihapus (Duplikat)   : {total_dropped_duplicates}")
        print(f"Total Baris Bersih Akhir   : {len(combined_df)}")
        print(f"File disimpan di           : {OUTPUT_FILE}")
        
        print("\nDistribusi Rating Keseluruhan:")
        for rating, count in combined_df["rating"].value_counts().sort_index().items():
            print(f"Bintang {int(rating)} : {count}")
    else:
        print("⚠️ Tidak ada data yang berhasil digabungkan.")

if __name__ == "__main__":
    main()
