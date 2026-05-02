"""
routes/auth.py — Authentication Routes (JWT)
==============================================
Endpoint untuk login, register, refresh token, dan profil user.
Menggunakan Flask-JWT-Extended.

Kebijakan Akses Role:
  - admin    : Full access — kelola user, scraping, retrain, hapus data
  - analyst  : Analisis, prediksi, export — tidak bisa kelola user/scraping
  - user     : Read-only — dashboard, data explorer, lihat profil sendiri
"""

from datetime import datetime, timezone
from functools import wraps

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt,
)

from models import db, User, UserRole

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# ─── Decorator: Role-Based Access Control ────────────────────────────────────

def role_required(*allowed_roles):
    """
    Decorator untuk membatasi akses berdasarkan role.
    Penggunaan: @role_required(UserRole.ADMIN, UserRole.ANALYST)
    """
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = db.session.get(User, int(current_user_id))

            if not user:
                return jsonify({'error': 'User tidak ditemukan'}), 404
            if not user.is_active:
                return jsonify({'error': 'Akun tidak aktif. Hubungi admin.'}), 403
            if user.role not in allowed_roles:
                return jsonify({
                    'error': 'Akses ditolak. Role Anda tidak memiliki izin untuk fitur ini.',
                    'required_roles': [r.value for r in allowed_roles],
                    'your_role': user.role.value,
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ─── POST /api/auth/login ────────────────────────────────────────────────────

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user dan mendapatkan JWT token.
    
    Body JSON:
      { "email": "...", "password": "..." }
    
    Response:
      { "access_token": "...", "refresh_token": "...", "user": {...} }
    """
    data = request.get_json()

    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email dan password wajib diisi'}), 400

    email = data['email'].strip().lower()
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Email atau password salah'}), 401

    if not user.is_active:
        return jsonify({'error': 'Akun Anda tidak aktif. Hubungi admin.'}), 403

    # Update last login
    user.update_last_login()

    # Generate tokens dengan identity = user.id (string)
    additional_claims = {'role': user.role.value, 'name': user.full_name}
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    return jsonify({
        'message': f'Selamat datang, {user.full_name}!',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict(),
    }), 200


# ─── POST /api/auth/register ─────────────────────────────────────────────────

@auth_bp.route('/register', methods=['POST'])
@role_required(UserRole.ADMIN)
def register():
    """
    Register user baru (hanya admin yang bisa).
    
    Body JSON:
      {
        "email": "...",
        "password": "...",
        "full_name": "...",
        "role": "admin" | "analyst" | "user",
        "department": "..." (opsional)
      }
    """
    data = request.get_json()

    required_fields = ['email', 'password', 'full_name', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Field "{field}" wajib diisi'}), 400

    email = data['email'].strip().lower()
    password = data['password']
    full_name = data['full_name'].strip()
    role_str = data['role'].strip().lower()

    # Validasi role
    try:
        role = UserRole(role_str)
    except ValueError:
        return jsonify({
            'error': f'Role "{role_str}" tidak valid. Pilihan: admin, analyst, user'
        }), 400

    # Cek duplikat email
    if User.query.filter_by(email=email).first():
        return jsonify({'error': f'Email "{email}" sudah terdaftar'}), 409

    # Validasi password minimal
    if len(password) < 6:
        return jsonify({'error': 'Password minimal 6 karakter'}), 400

    # Buat user baru
    new_user = User(
        email=email,
        full_name=full_name,
        role=role,
        department=data.get('department', '').strip() or None,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': f'User "{full_name}" berhasil didaftarkan sebagai {role.value}.',
        'user': new_user.to_dict(),
    }), 201


# ─── POST /api/auth/refresh ──────────────────────────────────────────────────

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token menggunakan refresh token."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user or not user.is_active:
        return jsonify({'error': 'Token tidak valid atau akun tidak aktif'}), 401

    additional_claims = {'role': user.role.value, 'name': user.full_name}
    new_access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    return jsonify({
        'access_token': new_access_token,
        'user': user.to_dict(),
    }), 200


# ─── GET /api/auth/profile ───────────────────────────────────────────────────

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Mendapatkan profil user yang sedang login."""
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    return jsonify({'user': user.to_dict()}), 200


# ─── PUT /api/auth/profile ───────────────────────────────────────────────────

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update profil sendiri (nama, department, avatar).
    User tidak bisa mengubah role/email sendiri.
    """
    current_user_id = get_jwt_identity()
    user = db.session.get(User, int(current_user_id))

    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    data = request.get_json()

    if data.get('full_name'):
        user.full_name = data['full_name'].strip()
    if data.get('department') is not None:
        user.department = data['department'].strip() or None
    if data.get('avatar_url') is not None:
        user.avatar_url = data['avatar_url'].strip() or None

    # Ganti password (opsional)
    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'error': 'Masukkan password lama untuk mengganti password'}), 400
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Password lama salah'}), 401
        if len(data['new_password']) < 6:
            return jsonify({'error': 'Password baru minimal 6 karakter'}), 400
        user.set_password(data['new_password'])

    user.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'message': 'Profil berhasil diperbarui',
        'user': user.to_dict(),
    }), 200
