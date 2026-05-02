"""
models/analysis.py — Model Hasil Analisis ML
==============================================
Menyimpan snapshot hasil analisis (K-Fold, LDA, model metrics)
agar bisa dibandingkan antar versi saat model di-retrain.
"""

from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB

from .database import db


class AnalysisResult(db.Model):
    """Model tabel hasil analisis ML (analysis_results)."""
    __tablename__ = 'analysis_results'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ─── Identifikasi Analisis ───────────────────────────────────────────
    analysis_type = db.Column(db.String(50), nullable=False, index=True)
    # Tipe: 'kfold_cv', 'lda_aspect', 'model_training', 'full_pipeline'

    version = db.Column(db.Integer, nullable=False, default=1)
    # Versi increment setiap kali retrain

    # ─── Hasil Analisis (JSON untuk fleksibilitas) ───────────────────────
    results_data = db.Column(JSONB, nullable=False)
    # Untuk kfold_cv: { metrics_per_fold, avg_metrics, best_fold, ... }
    # Untuk lda_aspect: { topics, dbi_scores, optimal_k, keywords, ... }
    # Untuk model_training: { model_type, accuracy, f1_score, ... }

    # ─── Metadata ────────────────────────────────────────────────────────
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total_reviews_used = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationship
    creator = db.relationship('User', backref='analysis_results', lazy=True)

    def to_dict(self) -> dict:
        """Serialize analysis result ke dictionary."""
        return {
            'id': self.id,
            'analysis_type': self.analysis_type,
            'version': self.version,
            'results_data': self.results_data,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_reviews_used': self.total_reviews_used,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<AnalysisResult {self.analysis_type} v{self.version}>'
