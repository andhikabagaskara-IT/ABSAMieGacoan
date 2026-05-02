"""
models/user.py — Model User & Role
====================================
Menyimpan data pengguna dengan 3 role:
  - admin    : Manajemen (full access)
  - analyst  : Marketing / Data Scientist (analisis & prediksi)
  - user     : Pegawai / Staf biasa (read-only)
"""

import enum
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import Enum as SQLEnum

from .database import db


class UserRole(enum.Enum):
    """Enum untuk 3 role pengguna sistem."""
    ADMIN = 'admin'        # Manajemen — full access (CRUD user, retrain, scraping, hapus data)
    ANALYST = 'analyst'    # Marketing/Data Scientist — analisis, prediksi, export
    USER = 'user'          # Pegawai/Staf biasa — read-only dashboard & data explorer


class User(db.Model):
    """Model tabel pengguna (users)."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role = db.Column(SQLEnum(UserRole), nullable=False, default=UserRole.USER)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

    # Profil tambahan
    avatar_url = db.Column(db.String(500), nullable=True)
    department = db.Column(db.String(100), nullable=True)  # e.g., "Marketing", "IT", "Operasional"

    def set_password(self, password: str):
        """Hash password menggunakan bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verifikasi password terhadap hash yang tersimpan."""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def update_last_login(self):
        """Catat waktu login terakhir."""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def to_dict(self) -> dict:
        """Serialize user ke dictionary (tanpa password)."""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'department': self.department,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }

    def __repr__(self):
        return f'<User {self.email} ({self.role.value})>'
