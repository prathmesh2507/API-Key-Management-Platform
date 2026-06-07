from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.key_generator import generate_api_key
from app.utils.security import hash_api_key
from app.models.api_key_model import APIKeyModel
from bson import ObjectId
from datetime import datetime

key_bp = Blueprint("keys", __name__)


@key_bp.route("/", methods=["POST"])
@jwt_required()
def create_key():
    user_id = get_jwt_identity()
    data = request.get_json()

    name = data.get("name", "Default Key")
    expires_in_days = data.get("expires_in_days", 30)
    rate_limit = data.get("rate_limit", 60)

    raw_key = generate_api_key()
    key_hash = hash_api_key(raw_key)

    APIKeyModel.create_key(
        user_id=user_id,
        name=name,
        key_hash=key_hash,
        expires_in_days=expires_in_days,
        rate_limit=rate_limit
    )

    return jsonify({
        "message": "API key created successfully",
        "api_key": raw_key  # show only once
    }), 201


@key_bp.route("/", methods=["GET"])
@jwt_required()
def list_keys():
    user_id = get_jwt_identity()

    keys = APIKeyModel.get_user_keys(user_id)

    for key in keys:
        key["_id"] = str(key["_id"])
        key["user_id"] = str(key["user_id"])

        if key.get("created_at"):
            key["created_at"] = key["created_at"].isoformat()

        if key.get("expires_at"):
            key["expires_at"] = key["expires_at"].isoformat()


    return jsonify(keys), 200


@key_bp.route("/<key_id>/revoke", methods=["PATCH"])
@jwt_required()
def revoke_key(key_id):
    user_id = get_jwt_identity()

    result = APIKeyModel.revoke_key(key_id, user_id)

    if result.modified_count == 0:
        return jsonify({"error": "Key not found"}), 404

    return jsonify({"message": "Key revoked"}), 200


@key_bp.route("/<key_id>", methods=["DELETE"])
@jwt_required()
def delete_key(key_id):
    user_id = get_jwt_identity()

    result = APIKeyModel.delete_key(key_id, user_id)

    if result.deleted_count == 0:
        return jsonify({"error": "Key not found"}), 404

    return jsonify({"message": "Key deleted"}), 200


@key_bp.route("/logs", methods=["GET"])
@jwt_required()
def get_logs():
    user_id = get_jwt_identity()

    logs = APIKeyModel.get_logs_for_user(user_id)

    for log in logs:
        log["_id"] = str(log["_id"])
        log["key_id"] = str(log["key_id"])
        log["user_id"] = str(log["user_id"])

    return jsonify(logs), 200


@key_bp.route("/analytics", methods=["GET"])
@jwt_required()
def analytics():
    user_id = get_jwt_identity()

    total_calls = APIKeyModel.get_total_calls(user_id)
    calls_last_24h = APIKeyModel.get_calls_last_24h(user_id)
    calls_per_key = APIKeyModel.get_calls_per_key(user_id)
    most_used_endpoint = APIKeyModel.get_most_used_endpoint(user_id)

    return jsonify({
        "total_calls": total_calls,
        "calls_last_24h": calls_last_24h,
        "calls_per_key": calls_per_key,
        "most_used_endpoint": most_used_endpoint
    }), 200


