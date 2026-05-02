"""
routes/pipeline.py — Pipeline Execution Routes (Sync Center)
=============================================================
Endpoint untuk memicu eksekusi pipeline ML secara background.
Akses: admin only (scraping, retrain)
        admin & analyst (retrain model)
"""

import os
import subprocess
import threading
import logging
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from config import BASE_DIR
from models import db, PipelineLog, UserRole
from routes.auth import role_required

log = logging.getLogger(__name__)
pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/api/pipeline')

SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')


def _run_script_async(script_name, pipeline_log_id, app):
    """Jalankan script Python di background thread."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)

    with app.app_context():
        pl = db.session.get(PipelineLog, pipeline_log_id)
        if not pl:
            return

        try:
            pl.progress_message = f"Menjalankan {script_name}..."
            db.session.commit()

            result = subprocess.run(
                ['python', script_path],
                capture_output=True, text=True, cwd=BASE_DIR, timeout=7200
            )

            if result.returncode == 0:
                pl.mark_completed({'stdout_tail': result.stdout[-500:] if result.stdout else ''})
            else:
                pl.mark_failed(result.stderr[-500:] if result.stderr else 'Unknown error')
            db.session.commit()

        except subprocess.TimeoutExpired:
            pl.mark_failed("Script timeout setelah 2 jam")
            db.session.commit()
        except Exception as e:
            pl.mark_failed(str(e))
            db.session.commit()


@pipeline_bp.route('/start', methods=['POST'])
@role_required(UserRole.ADMIN)
def start_pipeline():
    """
    Mulai eksekusi pipeline.
    Body: { "pipeline": "full" | "scraping" | "retrain", "parameters": {...} }
    """
    data = request.get_json() or {}
    pipeline_type = data.get('pipeline', 'full')
    params = data.get('parameters', {})
    user_id = int(get_jwt_identity())

    script_map = {
        'scraping': '01_scraping.py',
        'quality_check': '02_quality_check.py',
        'labeling': '03_labeling.py',
        'preprocessing': '04_preprocessing.py',
        'classification': '05_classification.py',
        'lda': '06_lda_aspect.py',
        'export': '07_export_dashboard.py',
    }

    if pipeline_type == 'full':
        scripts = list(script_map.values())
    elif pipeline_type == 'retrain':
        scripts = ['05_classification.py', '06_lda_aspect.py', '07_export_dashboard.py']
    elif pipeline_type in script_map:
        scripts = [script_map[pipeline_type]]
    else:
        return jsonify({'error': f'Pipeline "{pipeline_type}" tidak valid'}), 400

    pl = PipelineLog(
        pipeline_name=pipeline_type,
        status='running',
        parameters=params,
        started_by=user_id,
    )
    db.session.add(pl)
    db.session.commit()

    from flask import current_app
    app = current_app._get_current_object()
    thread = threading.Thread(target=_run_script_async, args=(scripts[0], pl.id, app))
    thread.daemon = True
    thread.start()

    return jsonify({'message': f'Pipeline "{pipeline_type}" dimulai', 'log_id': pl.id}), 202


@pipeline_bp.route('/status/<int:log_id>', methods=['GET'])
@jwt_required()
def pipeline_status(log_id):
    """Cek status pipeline berdasarkan log ID."""
    pl = db.session.get(PipelineLog, log_id)
    if not pl:
        return jsonify({'error': 'Log tidak ditemukan'}), 404
    return jsonify(pl.to_dict())


@pipeline_bp.route('/history', methods=['GET'])
@jwt_required()
def pipeline_history():
    """Riwayat eksekusi pipeline (terbaru dulu)."""
    page = max(1, int(request.args.get('page', 1)))
    per_page = min(50, max(1, int(request.args.get('per_page', 10))))
    pagination = PipelineLog.query.order_by(PipelineLog.started_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'logs': [l.to_dict() for l in pagination.items],
        'total': pagination.total,
    })
