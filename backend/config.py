"""
config.py — Konfigurasi Backend Flask
======================================
Mengatur path data, konfigurasi CORS, dan pengaturan umum.
"""

import os

# Basis Direktori Proyek
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path data-data penting
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


class Config:
    """Konfigurasi dasar Flask."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'miegacoan-absa-secret-key-2026')
    DEBUG = False
    TESTING = False
    
    # CORS - Izinkan akses dari VueJS dev server
    CORS_ORIGINS = [
        'http://localhost:5173',  # Vite default
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000',
    ]


class DevelopmentConfig(Config):
    """Konfigurasi untuk development."""
    DEBUG = True
    

class ProductionConfig(Config):
    """Konfigurasi untuk production."""
    DEBUG = False


# Map konfigurasi berdasarkan environment
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
