"""
config.py — Konfigurasi Backend Flask (Fullstack)
===================================================
Mengatur koneksi PostgreSQL, JWT, CORS, dan path data.
"""

import os
from datetime import timedelta

from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

# ─── Basis Direktori Proyek ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Path Data Penting ──────────────────────────────────────────────────────
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORT_DIR = os.path.join(DATA_DIR, 'export')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
MODELS_DIR = os.path.join(BASE_DIR, 'models')
PREPROCESSED_DIR = os.path.join(DATA_DIR, 'preprocessed')

# File utama
DASHBOARD_JSON = os.path.join(EXPORT_DIR, 'dashboard_data.json')
REVIEWS_CSV = os.path.join(PREPROCESSED_DIR, 'reviews_with_aspects.csv')
KFOLD_JSON = os.path.join(RESULTS_DIR, 'kfold_results.json')
LDA_JSON = os.path.join(RESULTS_DIR, 'lda_results.json')

# ─── Default Environment Variables ───────────────────────────────────────────
DEFAULT_DB_URL = 'postgresql://postgres:postgres@localhost:5432/miegacoan_absa'


class Config:
    """Konfigurasi dasar Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'miegacoan-absa-secret-key-2026')
    DEBUG = False
    TESTING = False

    # ─── Database PostgreSQL ─────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', DEFAULT_DB_URL)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
    }

    # ─── JWT Configuration ──────────────────────────────────────────────
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-miegacoan-secret-2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # ─── CORS ────────────────────────────────────────────────────────────
    CORS_ORIGINS = [
        'http://localhost:5173',   # Vite default
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000',
    ]


class DevelopmentConfig(Config):
    """Konfigurasi untuk development."""
    DEBUG = True


class TestingConfig(Config):
    """Konfigurasi untuk testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Konfigurasi untuk production."""
    DEBUG = False


# Map konfigurasi berdasarkan environment
config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
