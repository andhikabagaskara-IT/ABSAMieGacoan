"""
routes/predict.py — Live Prediction API (Algorithm Lab)
========================================================
Akses: admin & analyst
"""

import os
import re
import logging
import pickle

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from config import MODELS_DIR
from models import UserRole
from routes.auth import role_required

log = logging.getLogger(__name__)
predict_bp = Blueprint('predict', __name__, url_prefix='/api')

_model_cache = {}
_slang_dict = {
    "yg": "yang", "gak": "tidak", "ga": "tidak", "nggak": "tidak",
    "gk": "tidak", "bgt": "banget", "udh": "sudah", "udah": "sudah",
    "dgn": "dengan", "krn": "karena", "kalo": "kalau", "klo": "kalau",
    "tp": "tapi", "tpi": "tapi", "sm": "sama", "jd": "jadi",
    "pake": "pakai", "utk": "untuk", "bgs": "bagus", "tdk": "tidak", "blm": "belum",
}
_stopwords = None
_stemmer = None


def _load_model(filename, cache_key):
    if cache_key in _model_cache:
        return _model_cache[cache_key]
    filepath = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'rb') as f:
            model = pickle.load(f)
        _model_cache[cache_key] = model
        return model
    except Exception as e:
        log.error(f"Gagal memuat model {filepath}: {e}")
        return None


def _get_stopwords():
    global _stopwords
    if _stopwords is None:
        try:
            import nltk
            from nltk.corpus import stopwords
            try:
                nltk.data.find('corpora/stopwords')
            except LookupError:
                nltk.download('stopwords', quiet=True)
            _stopwords = set(stopwords.words('indonesian'))
        except Exception:
            _stopwords = set()
        _stopwords.update({'nya','sih','ya','aja','kok','deh','kan','dong','mah','buat','yang','di','ke','dari','dan','atau','yg','ga'})
    return _stopwords


def _get_stemmer():
    global _stemmer
    if _stemmer is None:
        try:
            from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
            _stemmer = StemmerFactory().create_stemmer()
        except Exception as e:
            log.error(f"Gagal memuat stemmer: {e}")
    return _stemmer


def preprocess_text(text: str) -> str:
    if not text: return ""
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\@\w+|\#\w+', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    words = [_slang_dict.get(w, w) for w in text.split()]
    sw = _get_stopwords()
    words = [w for w in words if w not in sw]
    stemmer = _get_stemmer()
    return stemmer.stem(' '.join(words)) if stemmer else ' '.join(words)


@predict_bp.route('/predict', methods=['POST'])
@role_required(UserRole.ADMIN, UserRole.ANALYST)
def predict_sentiment():
    """Prediksi sentimen teks ulasan menggunakan SVM & NB."""
    data = request.get_json()
    if not data or not data.get('text'):
        return jsonify({'error': 'Field "text" wajib diisi'}), 400

    raw_text = data['text'].strip()
    if len(raw_text) < 3:
        return jsonify({'error': 'Teks terlalu pendek'}), 400

    svm = _load_model('svm_model.pkl', 'svm')
    nb = _load_model('nb_model.pkl', 'nb')
    tfidf = _load_model('tfidf_vectorizer.pkl', 'tfidf')

    if not tfidf:
        return jsonify({'error': 'Model belum tersedia'}), 503

    preprocessed = preprocess_text(raw_text)
    if not preprocessed:
        return jsonify({'error': 'Teks kosong setelah preprocessing'}), 400

    vec = tfidf.transform([preprocessed])
    result = {'input_text': raw_text, 'preprocessed_text': preprocessed, 'predictions': {}}

    if svm:
        try:
            pred = svm.predict(vec)[0]
            conf = {}
            if hasattr(svm, 'decision_function'):
                scores = svm.decision_function(vec)[0]
                if hasattr(scores, '__len__'):
                    for i, lbl in enumerate(svm.classes_):
                        conf[lbl] = round(float(scores[i]), 4)
            result['predictions']['svm'] = {'label': pred, 'confidence': conf}
        except Exception as e:
            result['predictions']['svm'] = {'error': str(e)}

    if nb:
        try:
            pred = nb.predict(vec)[0]
            proba = nb.predict_proba(vec)[0]
            conf = {lbl: round(float(proba[i]), 4) for i, lbl in enumerate(nb.classes_)}
            result['predictions']['nb'] = {'label': pred, 'confidence': conf}
        except Exception as e:
            result['predictions']['nb'] = {'error': str(e)}

    return jsonify(result)


@predict_bp.route('/predict/status', methods=['GET'])
@jwt_required()
def predict_status():
    """Cek ketersediaan model prediksi."""
    checks = {
        'svm_model': os.path.exists(os.path.join(MODELS_DIR, 'svm_model.pkl')),
        'nb_model': os.path.exists(os.path.join(MODELS_DIR, 'nb_model.pkl')),
        'tfidf_vectorizer': os.path.exists(os.path.join(MODELS_DIR, 'tfidf_vectorizer.pkl')),
    }
    checks['models_ready'] = all(checks.values())
    return jsonify(checks)
