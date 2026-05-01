"""
app.py — Flask Backend untuk Mie Gacoan ABSA Dashboard
=======================================================
REST API yang menyajikan data analisis sentimen dan aspek
untuk dikonsumsi oleh frontend VueJS.

Cara Menjalankan:
  cd backend
  pip install -r requirements.txt
  python app.py

Endpoints:
  GET /api/dashboard         → Seluruh data agregasi dashboard
  GET /api/reviews           → Data ulasan (dengan paginasi & filter)
  GET /api/branches          → Daftar cabang beserta statistiknya
  GET /api/branch/<name>     → Detail satu cabang
  GET /api/lda               → Hasil LDA (topik, DBI, keywords)
  GET /api/kfold             → Hasil K-Fold Cross Validation
  GET /api/stats             → Ringkasan statistik keseluruhan
  GET /health                → Health check endpoint
"""

import os
import sys
import json
import logging

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import config_map, DASHBOARD_JSON, REVIEWS_CSV, KFOLD_JSON, LDA_JSON

# ─── Setup Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
log = logging.getLogger(__name__)

# ─── Inisialisasi Flask ───────────────────────────────────────────────────────
app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config_map.get(env, config_map['default']))

# CORS — Mengizinkan akses dari VueJS dev server
CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

# ─── Data Cache (Lazy Load) ──────────────────────────────────────────────────
_cache = {}


def load_json(filepath, cache_key):
    """Memuat file JSON dengan caching sederhana."""
    if cache_key in _cache:
        return _cache[cache_key]
    
    if not os.path.exists(filepath):
        log.warning(f"File tidak ditemukan: {filepath}")
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _cache[cache_key] = data
        log.info(f"Berhasil memuat {cache_key} dari {filepath}")
        return data
    except Exception as e:
        log.error(f"Gagal memuat {filepath}: {e}")
        return None


def load_reviews_df():
    """Memuat dataset ulasan dari CSV ke DataFrame."""
    if 'reviews_df' in _cache:
        return _cache['reviews_df']
    
    if not os.path.exists(REVIEWS_CSV):
        log.warning(f"File CSV ulasan tidak ditemukan: {REVIEWS_CSV}")
        return None
    
    try:
        df = pd.read_csv(REVIEWS_CSV, low_memory=False)
        _cache['reviews_df'] = df
        log.info(f"Berhasil memuat {len(df)} ulasan dari CSV")
        return df
    except Exception as e:
        log.error(f"Gagal memuat CSV: {e}")
        return None


# ─── API Routes ───────────────────────────────────────────────────────────────

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'Mie Gacoan ABSA Backend',
        'version': '1.0.0'
    })


@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Mengembalikan seluruh data agregasi dashboard (dari dashboard_data.json)."""
    data = load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data dashboard belum tersedia. Jalankan scripts/07_export_dashboard.py terlebih dahulu.'}), 404
    return jsonify(data)


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Mengembalikan ringkasan statistik keseluruhan."""
    data = load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data belum tersedia'}), 404
    
    stats = {
        'total_reviews': data.get('total_reviews', 0),
        'sentiment_distribution': data.get('sentiment_distribution', {}),
        'aspect_distribution': data.get('aspect_distribution', {}),
        'total_branches': len(data.get('branch_sentiment', {}))
    }
    return jsonify(stats)


@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """
    Mengembalikan data ulasan dengan paginasi dan filter.
    
    Query Parameters:
      - page (int): Nomor halaman (default: 1)
      - per_page (int): Jumlah per halaman (default: 25, max: 100)
      - branch (str): Filter berdasarkan nama cabang
      - sentiment (str): Filter berdasarkan sentimen (positif/negatif/netral)
      - aspect (str): Filter berdasarkan aspek LDA
      - rating (int): Filter berdasarkan rating
      - search (str): Pencarian teks di komentar
      - sort_by (str): Kolom untuk sorting
      - sort_dir (str): Arah sorting (asc/desc)
    """
    df = load_reviews_df()
    if df is None:
        return jsonify({'error': 'Data ulasan belum tersedia'}), 404
    
    # Copy untuk filter
    filtered = df.copy()
    
    # Kolom yang ditampilkan
    display_cols = ['nama_cabang', 'nama_pelanggan', 'tanggal_ulasan', 'rating',
                    'teks_komentar', 'sentimen', 'aspek_lda']
    display_cols = [c for c in display_cols if c in filtered.columns]
    filtered = filtered[display_cols]
    
    # ─── Filters ──────────────────────────────────────────────────────────
    branch = request.args.get('branch', '')
    sentiment = request.args.get('sentiment', '')
    aspect = request.args.get('aspect', '')
    rating = request.args.get('rating', '')
    search = request.args.get('search', '')
    
    if branch:
        filtered = filtered[filtered['nama_cabang'] == branch]
    if sentiment:
        filtered = filtered[filtered['sentimen'] == sentiment]
    if aspect:
        filtered = filtered[filtered['aspek_lda'] == aspect]
    if rating:
        try:
            filtered = filtered[filtered['rating'] == int(rating)]
        except ValueError:
            pass
    if search:
        q = search.lower()
        mask = (
            filtered['teks_komentar'].astype(str).str.lower().str.contains(q, na=False) |
            filtered['nama_pelanggan'].astype(str).str.lower().str.contains(q, na=False)
        )
        filtered = filtered[mask]
    
    # ─── Sorting ──────────────────────────────────────────────────────────
    sort_by = request.args.get('sort_by', '')
    sort_dir = request.args.get('sort_dir', 'asc')
    
    if sort_by and sort_by in filtered.columns:
        ascending = sort_dir.lower() != 'desc'
        filtered = filtered.sort_values(by=sort_by, ascending=ascending)
    
    # ─── Paginasi ─────────────────────────────────────────────────────────
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(100, max(1, int(request.args.get('per_page', 25))))
    
    total = len(filtered)
    total_pages = max(1, (total + per_page - 1) // per_page)
    
    start = (page - 1) * per_page
    end = start + per_page
    page_data = filtered.iloc[start:end]
    
    # Bersihkan NaN
    page_data = page_data.fillna('Tidak Ada Data')
    
    return jsonify({
        'reviews': page_data.to_dict(orient='records'),
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    })


@app.route('/api/branches', methods=['GET'])
def get_branches():
    """Mengembalikan daftar semua cabang beserta statistik sentimen."""
    data = load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data belum tersedia'}), 404
    
    branch_sentiment = data.get('branch_sentiment', {})
    branch_aspect = data.get('branch_aspect', {})
    
    branches = []
    for name, sentiment in branch_sentiment.items():
        total = sum(sentiment.values())
        branches.append({
            'nama_cabang': name,
            'display_name': name.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''),
            'sentiment': sentiment,
            'aspect': branch_aspect.get(name, {}),
            'total_reviews': total,
            'positive_pct': round((sentiment.get('positif', 0) / total * 100), 1) if total > 0 else 0,
            'negative_pct': round((sentiment.get('negatif', 0) / total * 100), 1) if total > 0 else 0,
            'neutral_pct': round((sentiment.get('netral', 0) / total * 100), 1) if total > 0 else 0,
        })
    
    # Sort by total reviews (descending)
    branches.sort(key=lambda x: x['total_reviews'], reverse=True)
    
    return jsonify({
        'branches': branches,
        'total': len(branches)
    })


@app.route('/api/branch/<path:branch_name>', methods=['GET'])
def get_branch_detail(branch_name):
    """Mengembalikan detail satu cabang termasuk sampel ulasan."""
    data = load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data belum tersedia'}), 404
    
    branch_sentiment = data.get('branch_sentiment', {})
    branch_aspect = data.get('branch_aspect', {})
    
    if branch_name not in branch_sentiment:
        return jsonify({'error': f'Cabang "{branch_name}" tidak ditemukan'}), 404
    
    sentiment = branch_sentiment[branch_name]
    aspect = branch_aspect.get(branch_name, {})
    
    # Ambil sampel ulasan cabang ini dari DataFrame
    df = load_reviews_df()
    sample_reviews = {'positif': [], 'negatif': [], 'netral': []}
    
    if df is not None:
        branch_df = df[df['nama_cabang'] == branch_name]
        
        for sent_type in ['positif', 'negatif', 'netral']:
            sent_df = branch_df[branch_df['sentimen'] == sent_type].head(3)
            for _, row in sent_df.iterrows():
                sample_reviews[sent_type].append({
                    'nama_pelanggan': str(row.get('nama_pelanggan', '')),
                    'rating': int(row.get('rating', 0)),
                    'teks_komentar': str(row.get('teks_komentar', '')),
                    'tanggal_ulasan': str(row.get('tanggal_ulasan', '')),
                    'aspek_lda': str(row.get('aspek_lda', '')),
                })
    
    return jsonify({
        'nama_cabang': branch_name,
        'display_name': branch_name.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''),
        'sentiment': sentiment,
        'aspect': aspect,
        'sample_reviews': sample_reviews
    })


@app.route('/api/lda', methods=['GET'])
def get_lda():
    """Mengembalikan hasil LDA (topik, DBI, keywords)."""
    data = load_json(LDA_JSON, 'lda')
    if data is None:
        return jsonify({'error': 'Data LDA belum tersedia. Jalankan scripts/06_lda_aspect.py terlebih dahulu.'}), 404
    return jsonify(data)


@app.route('/api/kfold', methods=['GET'])
def get_kfold():
    """Mengembalikan hasil K-Fold Cross Validation."""
    data = load_json(KFOLD_JSON, 'kfold')
    if data is None:
        return jsonify({'error': 'Data K-Fold belum tersedia. Jalankan scripts/05_classification.py terlebih dahulu.'}), 404
    return jsonify(data)


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Membersihkan cache data untuk memuat ulang dari file terbaru."""
    _cache.clear()
    log.info("Cache telah dibersihkan")
    return jsonify({'message': 'Cache berhasil dibersihkan. Data akan dimuat ulang dari file pada request berikutnya.'})


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint tidak ditemukan'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Terjadi kesalahan internal server'}), 500


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    log.info("=" * 60)
    log.info("  Mie Gacoan ABSA — Flask Backend API")
    log.info("=" * 60)
    log.info(f"  Environment   : {env}")
    log.info(f"  Dashboard JSON: {DASHBOARD_JSON}")
    log.info(f"  Reviews CSV   : {REVIEWS_CSV}")
    log.info(f"  LDA JSON      : {LDA_JSON}")
    log.info(f"  K-Fold JSON   : {KFOLD_JSON}")
    log.info("=" * 60)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config.get('DEBUG', True)
    )
