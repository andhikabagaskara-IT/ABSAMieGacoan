"""app.py — Flask Backend Fullstack — Mie Gacoan ABSA Dashboard
==============================================================
Arsitektur modular dengan:
  - PostgreSQL + SQLAlchemy ORM
  - Flask-JWT-Extended (autentikasi 3 role)
  - Blueprint-based routing
  - Token blacklisting (logout)
  - Rate limiting
  - Database migration support

Cara Menjalankan:
  cd backend
  pip install -r requirements.txt
  python app.py

Endpoints Utama:
  POST /api/auth/login          → Login & dapatkan JWT token
  POST /api/auth/register       → Register user baru (admin only)
  POST /api/auth/refresh        → Refresh access token
  POST /api/auth/logout         → Logout & revoke token
  GET  /api/auth/profile        → Profil user yang login
  PUT  /api/auth/profile        → Update profil sendiri
  GET  /api/dashboard           → Data agregasi dashboard
  GET  /api/reviews             → Ulasan (server-side pagination)
  GET  /api/reviews/stats       → Statistik ulasan dari DB
  GET  /api/branches            → Daftar cabang + statistik
  GET  /api/lda                 → Hasil LDA
  GET  /api/kfold               → Hasil K-Fold CV
  POST /api/predict             → Prediksi sentimen real-time
  POST /api/pipeline/start      → Mulai pipeline (admin & analyst)
  GET  /api/pipeline/history    → Riwayat pipeline
  GET  /api/pipeline/export-csv → Export CSV (admin & analyst)
  GET  /api/pipeline/role-permissions → Permissions user
  GET  /api/admin/users         → Daftar semua user (admin only)
  POST /api/admin/migrate-csv   → Migrasi CSV ke PostgreSQL
  GET  /health                  → Health check
"""

import os
import sys
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config_map
from models import db, User, UserRole

# ─── Setup Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout
)
log = logging.getLogger(__name__)

# ─── App Factory ──────────────────────────────────────────────────────────────

def create_app(env_name=None):
    """Factory function untuk membuat Flask app."""
    app = Flask(__name__)

    # Load konfigurasi
    if env_name is None:
        env_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config_map.get(env_name, config_map['default']))

    # ─── Extensions ──────────────────────────────────────────────────────
    # Database
    db.init_app(app)

    # Migrations
    migrate = Migrate(app, db)

    # JWT
    jwt = JWTManager(app)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})

    # Rate Limiter
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per hour"],
        storage_uri="memory://",
    )
    # Rate limit khusus untuk endpoint prediksi (mencegah abuse)
    limiter.limit("30 per minute")(lambda: None)  # Applied per-route below

    # ─── JWT Error Handlers ─────────────────────────────────────────────
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """Callback untuk cek apakah token sudah di-blacklist via logout."""
        from routes.auth import is_token_revoked
        return is_token_revoked(jwt_payload['jti'])

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token telah kedaluwarsa. Silakan login ulang.'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Token tidak valid.'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Token tidak ditemukan. Silakan login terlebih dahulu.'}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token telah dicabut. Silakan login ulang.'}), 401

    # ─── Register Blueprints ─────────────────────────────────────────────
    from routes import auth_bp, dashboard_bp, reviews_bp, predict_bp, pipeline_bp, admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(admin_bp)

    # ─── Health Check ────────────────────────────────────────────────────
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'ok',
            'service': 'Mie Gacoan ABSA Backend',
            'version': '2.1.0',
            'auth': 'JWT (Flask-JWT-Extended)',
            'database': 'PostgreSQL',
            'features': ['token_blacklist', 'rate_limiting', 'role_based_access', 'csv_export'],
        })

    # ─── Error Handlers ──────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint tidak ditemukan'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Terjadi kesalahan internal server'}), 500

    # ─── Database Init + Seeding ─────────────────────────────────────────
    with app.app_context():
        _init_database(app)

    return app


def _init_database(app):
    """Inisialisasi tabel database dan seed admin default."""
    try:
        db.create_all()
        log.info("Database tables created/verified successfully")

        # Seed default admin jika belum ada
        admin_email = os.environ.get('ADMIN_DEFAULT_EMAIL', 'admin@miegacoan.com')
        existing_admin = User.query.filter_by(email=admin_email).first()

        if not existing_admin:
            admin = User(
                email=admin_email,
                full_name=os.environ.get('ADMIN_DEFAULT_NAME', 'Administrator'),
                role=UserRole.ADMIN,
                department='Management',
            )
            admin.set_password(os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123'))
            db.session.add(admin)

            # Seed sample analyst & user
            analyst = User(
                email='analyst@miegacoan.com',
                full_name='Data Analyst',
                role=UserRole.ANALYST,
                department='Marketing',
            )
            analyst.set_password('analyst123')
            db.session.add(analyst)

            staff = User(
                email='staff@miegacoan.com',
                full_name='Staff Operasional',
                role=UserRole.USER,
                department='Operasional',
            )
            staff.set_password('staff123')
            db.session.add(staff)

            db.session.commit()
            log.info("Default users seeded: admin, analyst, staff")
        else:
            log.info(f"Admin user already exists: {admin_email}")

    except Exception as e:
        log.error(f"Database initialization error: {e}")
        log.warning("Pastikan PostgreSQL berjalan dan database 'miegacoan_absa' sudah dibuat.")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app = create_app()

    log.info("=" * 60)
    log.info("  Mie Gacoan ABSA — Flask Backend API v2.1")
    log.info("=" * 60)
    log.info(f"  Database  : PostgreSQL")
    log.info(f"  Auth      : Flask-JWT-Extended + Token Blacklist")
    log.info(f"  Limiter   : 200 req/hour (default)")
    log.info(f"  Roles     : admin, analyst, user")
    log.info("=" * 60)
    log.info("  Default Accounts:")
    log.info("    admin@miegacoan.com    / admin123    (Admin)")
    log.info("    analyst@miegacoan.com  / analyst123  (Analyst)")
    log.info("    staff@miegacoan.com    / staff123    (User)")
    log.info("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=app.config.get('DEBUG', True))
