from datetime import datetime
from app.extensions import mongo
from bson.objectid import ObjectId


class UserModel:

    @staticmethod
    def create_user(email: str, password_hash: str):
        user = {
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow()
        }
        return mongo.db.users.insert_one(user)

    @staticmethod
    def find_by_email(email: str):
        return mongo.db.users.find_one({"email": email})

    @staticmethod
    def find_by_id(user_id: str):
        return mongo.db.users.find_one({"_id": ObjectId(user_id)})
