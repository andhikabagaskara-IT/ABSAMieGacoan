"""
models/pipeline_log.py — Model Log Pipeline Execution
=======================================================
Mencatat log eksekusi pipeline (scraping, preprocessing, training, dll.)
untuk monitoring dan audit trail.
"""

from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB

from .database import db


class PipelineLog(db.Model):
    """Model tabel log eksekusi pipeline (pipeline_logs)."""
    __tablename__ = 'pipeline_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ─── Identifikasi Pipeline ───────────────────────────────────────────
    pipeline_name = db.Column(db.String(100), nullable=False, index=True)
    # Contoh: 'scraping', 'quality_check', 'labeling', 'preprocessing',
    #         'classification', 'lda_aspect', 'export_dashboard', 'full_pipeline'

    status = db.Column(db.String(20), nullable=False, default='running')
    # Status: 'running', 'completed', 'failed', 'cancelled'

    # ─── Detail Eksekusi ────────────────────────────────────────────────
    parameters = db.Column(JSONB, nullable=True)
    # Parameter yang digunakan saat eksekusi, misal:
    # { "branches": ["Ambengan", "Darmo"], "limit": 5000, "year_filter": 2025 }

    progress = db.Column(db.Float, default=0.0)  # 0.0 - 100.0
    progress_message = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)

    output_summary = db.Column(JSONB, nullable=True)
    # Ringkasan hasil, misal:
    # { "total_scraped": 5000, "total_processed": 4800, "duration_seconds": 120 }

    # ─── Metadata ────────────────────────────────────────────────────────
    started_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationship
    starter = db.relationship('User', backref='pipeline_logs', lazy=True)

    def mark_completed(self, summary: dict = None):
        """Tandai pipeline selesai."""
        self.status = 'completed'
        self.progress = 100.0
        self.completed_at = datetime.now(timezone.utc)
        if summary:
            self.output_summary = summary

    def mark_failed(self, error: str):
        """Tandai pipeline gagal."""
        self.status = 'failed'
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = error

    def to_dict(self) -> dict:
        """Serialize pipeline log ke dictionary."""
        return {
            'id': self.id,
            'pipeline_name': self.pipeline_name,
            'status': self.status,
            'parameters': self.parameters,
            'progress': self.progress,
            'progress_message': self.progress_message,
            'error_message': self.error_message,
            'output_summary': self.output_summary,
            'started_by': self.started_by,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

    def __repr__(self):
        return f'<PipelineLog {self.pipeline_name} ({self.status})>'
