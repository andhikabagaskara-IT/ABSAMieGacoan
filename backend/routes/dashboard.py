"""
routes/dashboard.py — Dashboard Data Routes
=============================================
Endpoint untuk mengambil data agregasi dashboard, statistik,
LDA results, dan K-Fold results.

Akses: Semua role yang sudah login (admin, analyst, user)
"""

import json
import os
import logging

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from config import DASHBOARD_JSON, KFOLD_JSON, LDA_JSON

log = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api')

# ─── Simple File Cache ──────────────────────────────────────────────────────
_file_cache = {}


def _load_json(filepath, cache_key):
    """Memuat file JSON dengan caching."""
    if cache_key in _file_cache:
        return _file_cache[cache_key]

    if not os.path.exists(filepath):
        log.warning(f"File tidak ditemukan: {filepath}")
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        _file_cache[cache_key] = data
        log.info(f"Berhasil memuat {cache_key} dari {filepath}")
        return data
    except Exception as e:
        log.error(f"Gagal memuat {filepath}: {e}")
        return None


# ─── GET /api/dashboard ──────────────────────────────────────────────────────

@dashboard_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard():
    """Mengembalikan seluruh data agregasi dashboard (dari dashboard_data.json)."""
    data = _load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({
            'error': 'Data dashboard belum tersedia. Jalankan pipeline terlebih dahulu.'
        }), 404
    return jsonify(data)


# ─── GET /api/stats ──────────────────────────────────────────────────────────

@dashboard_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Mengembalikan ringkasan statistik keseluruhan."""
    data = _load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data belum tersedia'}), 404

    stats = {
        'total_reviews': data.get('total_reviews', 0),
        'sentiment_distribution': data.get('sentiment_distribution', {}),
        'aspect_distribution': data.get('aspect_distribution', {}),
        'total_branches': len(data.get('branch_sentiment', {})),
    }
    return jsonify(stats)


# ─── GET /api/branches ───────────────────────────────────────────────────────

@dashboard_bp.route('/branches', methods=['GET'])
@jwt_required()
def get_branches():
    """Mengembalikan daftar semua cabang beserta statistik sentimen."""
    data = _load_json(DASHBOARD_JSON, 'dashboard')
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

    branches.sort(key=lambda x: x['total_reviews'], reverse=True)

    return jsonify({'branches': branches, 'total': len(branches)})


# ─── GET /api/branch/<name> ──────────────────────────────────────────────────

@dashboard_bp.route('/branch/<path:branch_name>', methods=['GET'])
@jwt_required()
def get_branch_detail(branch_name):
    """Mengembalikan detail satu cabang termasuk statistik sentimen & aspek."""
    data = _load_json(DASHBOARD_JSON, 'dashboard')
    if data is None:
        return jsonify({'error': 'Data belum tersedia'}), 404

    branch_sentiment = data.get('branch_sentiment', {})
    branch_aspect = data.get('branch_aspect', {})

    if branch_name not in branch_sentiment:
        return jsonify({'error': f'Cabang "{branch_name}" tidak ditemukan'}), 404

    sentiment = branch_sentiment[branch_name]
    aspect = branch_aspect.get(branch_name, {})

    return jsonify({
        'nama_cabang': branch_name,
        'display_name': branch_name.replace('Mie Gacoan - ', '').replace('Mie Gacoan ', ''),
        'sentiment': sentiment,
        'aspect': aspect,
    })


# ─── GET /api/lda ────────────────────────────────────────────────────────────

@dashboard_bp.route('/lda', methods=['GET'])
@jwt_required()
def get_lda():
    """Mengembalikan hasil LDA (topik, DBI, keywords)."""
    data = _load_json(LDA_JSON, 'lda')
    if data is None:
        return jsonify({'error': 'Data LDA belum tersedia'}), 404
    return jsonify(data)


# ─── GET /api/kfold ──────────────────────────────────────────────────────────

@dashboard_bp.route('/kfold', methods=['GET'])
@jwt_required()
def get_kfold():
    """Mengembalikan hasil K-Fold Cross Validation."""
    data = _load_json(KFOLD_JSON, 'kfold')
    if data is None:
        return jsonify({'error': 'Data K-Fold belum tersedia'}), 404
    return jsonify(data)


# ─── POST /api/cache/clear ───────────────────────────────────────────────────

@dashboard_bp.route('/cache/clear', methods=['POST'])
@jwt_required()
def clear_cache():
    """Membersihkan cache data untuk memuat ulang dari file terbaru."""
    from routes.auth import role_required
    from models import UserRole
    # Cache clear manual
    _file_cache.clear()
    log.info("File cache telah dibersihkan")
    return jsonify({
        'message': 'Cache berhasil dibersihkan. Data akan dimuat ulang pada request berikutnya.'
    })
