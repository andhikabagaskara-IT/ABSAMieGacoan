"""
models/database.py — SQLAlchemy Database Instance
===================================================
Inisialisasi instance SQLAlchemy yang digunakan di seluruh aplikasi.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
