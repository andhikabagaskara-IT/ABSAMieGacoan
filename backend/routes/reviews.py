"""
routes/reviews.py — Reviews Data Routes (Server-side Pagination)
=================================================================
Endpoint untuk mengambil data ulasan dengan server-side pagination,
filtering, sorting, dan search — agar browser tidak terbebani.

Akses: Semua role yang sudah login (admin, analyst, user)
"""

import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func, or_

from models import db, Review

log = logging.getLogger(__name__)

reviews_bp = Blueprint('reviews', __name__, url_prefix='/api')


# ─── GET /api/reviews ────────────────────────────────────────────────────────

@reviews_bp.route('/reviews', methods=['GET'])
@jwt_required()
def get_reviews():
    """
    Mengembalikan data ulasan dengan server-side pagination dan filter.
    Data diambil dari database PostgreSQL — bukan lagi dari file CSV.
    
    Query Parameters:
      - page (int): Nomor halaman (default: 1)
      - per_page (int): Jumlah per halaman (default: 25, max: 100)
      - branch (str): Filter berdasarkan nama cabang
      - sentiment (str): Filter berdasarkan sentimen (positif/negatif/netral)
      - aspect (str): Filter berdasarkan aspek LDA
      - rating (int): Filter berdasarkan rating
      - search (str): Pencarian teks di komentar atau nama pelanggan
      - sort_by (str): Kolom untuk sorting (default: id)
      - sort_dir (str): Arah sorting — asc/desc (default: desc)
    """
    # Build query
    query = Review.query

    # ─── Filters ─────────────────────────────────────────────────────────
    branch = request.args.get('branch', '').strip()
    sentiment = request.args.get('sentiment', '').strip()
    aspect = request.args.get('aspect', '').strip()
    rating = request.args.get('rating', '').strip()
    search = request.args.get('search', '').strip()

    if branch:
        query = query.filter(Review.nama_cabang == branch)
    if sentiment:
        query = query.filter(Review.sentimen == sentiment)
    if aspect:
        query = query.filter(Review.aspek_lda == aspect)
    if rating:
        try:
            query = query.filter(Review.rating == int(rating))
        except ValueError:
            pass
    if search:
        q = f'%{search.lower()}%'
        query = query.filter(
            or_(
                func.lower(Review.teks_komentar).like(q),
                func.lower(Review.nama_pelanggan).like(q),
            )
        )

    # ─── Sorting ─────────────────────────────────────────────────────────
    sort_by = request.args.get('sort_by', 'id').strip()
    sort_dir = request.args.get('sort_dir', 'desc').strip().lower()

    # Map kolom yang diizinkan untuk sorting
    allowed_sort_cols = {
        'id': Review.id,
        'nama_cabang': Review.nama_cabang,
        'rating': Review.rating,
        'sentimen': Review.sentimen,
        'aspek_lda': Review.aspek_lda,
        'tanggal_ulasan': Review.tanggal_ulasan,
    }

    sort_column = allowed_sort_cols.get(sort_by, Review.id)
    if sort_dir == 'desc':
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # ─── Paginasi ────────────────────────────────────────────────────────
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(100, max(1, int(request.args.get('per_page', 25))))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    reviews = [r.to_dict() for r in pagination.items]

    return jsonify({
        'reviews': reviews,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
        }
    })


# ─── GET /api/reviews/<id> ───────────────────────────────────────────────────

@reviews_bp.route('/reviews/<int:review_id>', methods=['GET'])
@jwt_required()
def get_review_detail(review_id):
    """Mengembalikan detail satu ulasan termasuk data preprocessing."""
    review = db.session.get(Review, review_id)
    if not review:
        return jsonify({'error': 'Ulasan tidak ditemukan'}), 404

    return jsonify({'review': review.to_dict(include_preprocessing=True)})


# ─── GET /api/reviews/stats ──────────────────────────────────────────────────

@reviews_bp.route('/reviews/stats', methods=['GET'])
@jwt_required()
def get_reviews_stats():
    """Mengembalikan statistik ringkasan ulasan dari database."""
    total = db.session.query(func.count(Review.id)).scalar() or 0

    # Distribusi sentimen
    sentiment_query = (
        db.session.query(Review.sentimen, func.count(Review.id))
        .group_by(Review.sentimen)
        .all()
    )
    sentiment_dist = {s: c for s, c in sentiment_query if s}

    # Distribusi cabang
    branch_query = (
        db.session.query(Review.nama_cabang, func.count(Review.id))
        .group_by(Review.nama_cabang)
        .all()
    )
    branch_dist = {b: c for b, c in branch_query if b}

    # Distribusi aspek
    aspect_query = (
        db.session.query(Review.aspek_lda, func.count(Review.id))
        .group_by(Review.aspek_lda)
        .all()
    )
    aspect_dist = {a: c for a, c in aspect_query if a}

    # Distribusi rating
    rating_query = (
        db.session.query(Review.rating, func.count(Review.id))
        .group_by(Review.rating)
        .all()
    )
    rating_dist = {str(r): c for r, c in rating_query if r is not None}

    return jsonify({
        'total_reviews': total,
        'sentiment_distribution': sentiment_dist,
        'branch_distribution': branch_dist,
        'aspect_distribution': aspect_dist,
        'rating_distribution': rating_dist,
    })
