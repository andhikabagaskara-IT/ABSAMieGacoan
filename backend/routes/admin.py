"""
routes/admin.py — Admin Management Routes
===========================================
Endpoint untuk manajemen user, migrasi data, dan operasi admin.
Akses: admin only
"""

import os
import logging

import pandas as pd
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from config import REVIEWS_CSV
from models import db, User, UserRole, Review
from routes.auth import role_required

log = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@role_required(UserRole.ADMIN)
def list_users():
    """Daftar semua user."""
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({'users': [u.to_dict() for u in users], 'total': len(users)})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@role_required(UserRole.ADMIN)
def update_user(user_id):
    """Update user (role, status, department) oleh admin."""
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    data = request.get_json() or {}

    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
        except ValueError:
            return jsonify({'error': 'Role tidak valid'}), 400
    if 'is_active' in data:
        user.is_active = bool(data['is_active'])
    if 'full_name' in data:
        user.full_name = data['full_name'].strip()
    if 'department' in data:
        user.department = data['department'].strip() or None

    db.session.commit()
    return jsonify({'message': 'User diperbarui', 'user': user.to_dict()})


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@role_required(UserRole.ADMIN)
def delete_user(user_id):
    """Hapus user (tidak bisa hapus diri sendiri)."""
    current_id = int(get_jwt_identity())
    if user_id == current_id:
        return jsonify({'error': 'Tidak bisa menghapus akun sendiri'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User "{user.full_name}" berhasil dihapus'})


@admin_bp.route('/migrate-csv', methods=['POST'])
@role_required(UserRole.ADMIN)
def migrate_csv_to_db():
    """
    Migrasi data dari CSV (reviews_with_aspects.csv) ke tabel PostgreSQL.
    Ini adalah one-time operation untuk memindahkan data lama ke database.
    """
    if not os.path.exists(REVIEWS_CSV):
        return jsonify({'error': f'File CSV tidak ditemukan: {REVIEWS_CSV}'}), 404

    try:
        df = pd.read_csv(REVIEWS_CSV, low_memory=False)
        log.info(f"Membaca {len(df)} baris dari CSV")

        existing = db.session.query(db.func.count(Review.id)).scalar() or 0
        if existing > 0:
            return jsonify({
                'error': f'Database sudah berisi {existing} ulasan. Kosongkan dulu jika ingin migrasi ulang.',
                'existing_count': existing,
            }), 409

        batch_size = 1000
        total = len(df)
        imported = 0

        for start in range(0, total, batch_size):
            batch = df.iloc[start:start + batch_size]
            reviews = []
            for _, row in batch.iterrows():
                preprocessing = {}
                for col in ['text_clean', 'text_casefold', 'text_normalized',
                            'text_tokenized', 'text_stopword_removed', 'text_preprocessed']:
                    if col in row and pd.notna(row[col]):
                        preprocessing[col] = str(row[col])

                review = Review(
                    nama_cabang=str(row.get('nama_cabang', '')),
                    nama_pelanggan=str(row.get('nama_pelanggan', '')),
                    tanggal_ulasan=str(row.get('tanggal_ulasan', '')),
                    rating=int(row['rating']) if pd.notna(row.get('rating')) else None,
                    teks_komentar=str(row.get('teks_komentar', '')),
                    sentimen=str(row.get('sentimen', '')) if pd.notna(row.get('sentimen')) else None,
                    aspek_lda=str(row.get('aspek_lda', '')) if pd.notna(row.get('aspek_lda')) else None,
                    preprocessing_data=preprocessing if preprocessing else None,
                )
                reviews.append(review)

            db.session.bulk_save_objects(reviews)
            db.session.commit()
            imported += len(reviews)
            log.info(f"Migrasi: {imported}/{total} ({imported/total*100:.1f}%)")

        return jsonify({
            'message': f'Berhasil migrasi {imported} ulasan ke database',
            'total_imported': imported,
        })

    except Exception as e:
        db.session.rollback()
        log.error(f"Gagal migrasi CSV: {e}")
        return jsonify({'error': f'Gagal migrasi: {str(e)}'}), 500


@admin_bp.route('/db-stats', methods=['GET'])
@role_required(UserRole.ADMIN)
def db_stats():
    """Statistik database (jumlah record per tabel)."""
    from models import AnalysisResult, PipelineLog
    return jsonify({
        'users': db.session.query(db.func.count(User.id)).scalar() or 0,
        'reviews': db.session.query(db.func.count(Review.id)).scalar() or 0,
        'analysis_results': db.session.query(db.func.count(AnalysisResult.id)).scalar() or 0,
        'pipeline_logs': db.session.query(db.func.count(PipelineLog.id)).scalar() or 0,
    })
