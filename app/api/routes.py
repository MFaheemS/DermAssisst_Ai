"""
REST API stubs — Week 2 will wire in the ML model.
Week 1: returns 503 with a clear message so the frontend can be built against the contract.
"""
from flask import jsonify, request
from flask_login import current_user
from . import api_bp


@api_bp.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.0.0"})


@api_bp.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400
    return jsonify({
        "error": "Model not yet integrated.",
        "hint": "Available in Week 2.",
    }), 503


@api_bp.route("/analyses")
def analyses():
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required."}), 401
    return jsonify({"analyses": [], "total": 0})
