from flask import Blueprint, request, jsonify
from app.utils.security import hash_api_key
from app.models.api_key_model import APIKeyModel
from app.utils.rate_limiter import check_rate_limit
from datetime import datetime
from functools import wraps

api_bp = Blueprint("api", __name__)


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        raw_key = request.headers.get("x-api-key")

        if not raw_key:
            return jsonify({"error": "API key required"}), 401

        key_hash = hash_api_key(raw_key)

        api_key_doc = APIKeyModel.find_by_hash(key_hash)

        if not api_key_doc:
            return jsonify({"error": "Invalid API key"}), 401

        if not api_key_doc.get("is_active"):
            return jsonify({"error": "API key revoked"}), 403

        if datetime.utcnow() > api_key_doc.get("expires_at"):
            return jsonify({"error": "API key expired"}), 403

        # Rate limit check
        rate_check = check_rate_limit(api_key_doc)

        if not rate_check["allowed"]:
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Update usage
        if rate_check.get("reset"):
            APIKeyModel.update_usage(
                api_key_doc["_id"],
                reset=True,
                new_window_start=rate_check["new_window_start"]
            )
        else:
            APIKeyModel.update_usage(
                api_key_doc["_id"],
                reset=False,
                new_window_start=datetime.utcnow()
            )

                # Log usage
        APIKeyModel.log_request(
            key_id=api_key_doc["_id"],
            user_id=api_key_doc["user_id"],
            endpoint=request.path,
            ip_address=request.remote_addr
        )

        return f(*args, **kwargs)


    return decorated


@api_bp.route("/protected", methods=["GET"])
@require_api_key
def protected():
    return jsonify({
        "message": "Access granted to protected resource"
    }), 200
