from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user_model import UserModel
from app.utils.security import hash_password, verify_password
from bson.objectid import ObjectId
from flask import render_template


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login-page", methods=["GET"])
def login_page():
    return render_template("login.html")



@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    existing_user = UserModel.find_by_email(email)
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    password_hash = hash_password(password)

    UserModel.create_user(email, password_hash)

    return jsonify({"message": "User registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = UserModel.find_by_email(email)

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user["_id"]))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token
    }), 200


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()

    user = UserModel.find_by_id(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user["email"],
        "created_at": user["created_at"]
    }), 200


@auth_bp.route("/register-page", methods=["GET"])
def register_page():
    return render_template("register.html")
