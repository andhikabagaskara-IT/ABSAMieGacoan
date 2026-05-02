"""
routes/__init__.py — Blueprint Registration
=============================================
Export semua blueprints agar dapat didaftarkan di app factory.
"""

from .auth import auth_bp
from .dashboard import dashboard_bp
from .reviews import reviews_bp
from .predict import predict_bp
from .pipeline import pipeline_bp
from .admin import admin_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'reviews_bp',
    'predict_bp',
    'pipeline_bp',
    'admin_bp',
]
