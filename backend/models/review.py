"""
models/review.py — Model Review (Ulasan)
==========================================
Menyimpan data ulasan pelanggan beserta hasil analisis sentimen dan aspek.
Menggunakan kolom JSON PostgreSQL untuk menyimpan data preprocessing
yang bersifat semi-structured.
"""

from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB

from .database import db


class Review(db.Model):
    """Model tabel ulasan pelanggan (reviews)."""
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ─── Data Mentah dari Scraping ───────────────────────────────────────
    nama_cabang = db.Column(db.String(255), nullable=False, index=True)
    nama_pelanggan = db.Column(db.String(255), nullable=True)
    tanggal_ulasan = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=True)
    teks_komentar = db.Column(db.Text, nullable=True)

    # ─── Hasil Analisis ──────────────────────────────────────────────────
    sentimen = db.Column(db.String(20), nullable=True, index=True)      # positif / negatif / netral
    aspek_lda = db.Column(db.String(100), nullable=True, index=True)    # Topik hasil LDA

    # ─── Data Preprocessing (disimpan sebagai JSON untuk fleksibilitas) ─
    preprocessing_data = db.Column(JSONB, nullable=True)
    # Berisi: {
    #   "text_clean": "...",
    #   "text_casefold": "...",
    #   "text_normalized": "...",
    #   "text_tokenized": [...],
    #   "text_stopword_removed": [...],
    #   "text_preprocessed": "..."
    # }

    # ─── Metadata ────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    batch_id = db.Column(db.String(50), nullable=True, index=True)  # ID batch scraping

    def to_dict(self, include_preprocessing=False) -> dict:
        """Serialize review ke dictionary."""
        result = {
            'id': self.id,
            'nama_cabang': self.nama_cabang,
            'nama_pelanggan': self.nama_pelanggan,
            'tanggal_ulasan': self.tanggal_ulasan,
            'rating': self.rating,
            'teks_komentar': self.teks_komentar,
            'sentimen': self.sentimen,
            'aspek_lda': self.aspek_lda,
        }
        if include_preprocessing and self.preprocessing_data:
            result['preprocessing'] = self.preprocessing_data
        return result

    def __repr__(self):
        return f'<Review #{self.id} — {self.nama_cabang} ({self.sentimen})>'
