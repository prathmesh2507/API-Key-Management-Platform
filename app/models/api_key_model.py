from datetime import datetime, timedelta
from app.extensions import mongo
from bson.objectid import ObjectId


class APIKeyModel:

    @staticmethod
    def create_key(user_id, name, key_hash, expires_in_days=30, rate_limit=60):
        now = datetime.utcnow()

        api_key = {
            "user_id": ObjectId(user_id),
            "name": name,
            "key_hash": key_hash,
            "created_at": now,
            "expires_at": now + timedelta(days=expires_in_days),
            "is_active": True,
            "rate_limit_per_minute": rate_limit,
            "request_count": 0,
            "window_start": now,
            "last_used": None
        }

        return mongo.db.api_keys.insert_one(api_key)

    @staticmethod
    def get_user_keys(user_id):
        return list(mongo.db.api_keys.find(
            {"user_id": ObjectId(user_id)},
            {"key_hash": 0}  # hide hash
        ))

    @staticmethod
    def revoke_key(key_id, user_id):
        return mongo.db.api_keys.update_one(
            {"_id": ObjectId(key_id), "user_id": ObjectId(user_id)},
            {"$set": {"is_active": False}}
        )

    @staticmethod
    def delete_key(key_id, user_id):
        return mongo.db.api_keys.delete_one(
            {"_id": ObjectId(key_id), "user_id": ObjectId(user_id)}
        )
    
    @staticmethod
    def find_by_hash(key_hash):
        return mongo.db.api_keys.find_one({"key_hash": key_hash})

    @staticmethod
    def update_usage(key_id, reset=False, new_window_start=None):
        if reset:
            mongo.db.api_keys.update_one(
                {"_id": key_id},
                {
                    "$set": {
                        "request_count": 1,
                        "window_start": new_window_start,
                        "last_used": new_window_start
                    }
                }
            )
        else:
            mongo.db.api_keys.update_one(
                {"_id": key_id},
                {
                    "$inc": {"request_count": 1},
                    "$set": {"last_used": new_window_start}
                }
            )

    @staticmethod
    def log_request(key_id, user_id, endpoint, ip_address):
        log_entry = {
            "key_id": key_id,
            "user_id": user_id,
            "endpoint": endpoint,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow()
        }

        mongo.db.api_logs.insert_one(log_entry)

    @staticmethod
    def get_logs_for_user(user_id):
        return list(mongo.db.api_logs.find(
            {"user_id": ObjectId(user_id)}
        ).sort("timestamp", -1))
    
    @staticmethod
    def get_total_calls(user_id):
        return mongo.db.api_logs.count_documents({
            "user_id": ObjectId(user_id)
        })

    @staticmethod
    def get_calls_last_24h(user_id):
        from datetime import datetime, timedelta

        last_24h = datetime.utcnow() - timedelta(hours=24)

        return mongo.db.api_logs.count_documents({
            "user_id": ObjectId(user_id),
            "timestamp": {"$gte": last_24h}
        })

    @staticmethod
    def get_calls_per_key(user_id):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": "$key_id",
                    "count": {"$sum": 1}
                }
            }
        ]

        results = list(mongo.db.api_logs.aggregate(pipeline))

        for r in results:
            r["_id"] = str(r["_id"])

        return results

    @staticmethod
    def get_most_used_endpoint(user_id):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": "$endpoint",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]

        result = list(mongo.db.api_logs.aggregate(pipeline))

        if result:
            return {
                "endpoint": result[0]["_id"],
                "count": result[0]["count"]
            }

        return None
    
    @staticmethod
    def get_total_calls(user_id):
        return mongo.db.api_logs.count_documents({
            "user_id": ObjectId(user_id)
        })

    @staticmethod
    def get_calls_last_24h(user_id):
        from datetime import datetime, timedelta

        last_24h = datetime.utcnow() - timedelta(hours=24)

        return mongo.db.api_logs.count_documents({
            "user_id": ObjectId(user_id),
            "timestamp": {"$gte": last_24h}
        })

    @staticmethod
    def get_calls_per_key(user_id):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": "$key_id",
                    "count": {"$sum": 1}
                }
            }
        ]

        results = list(mongo.db.api_logs.aggregate(pipeline))

        for r in results:
            r["_id"] = str(r["_id"])

        return results

    @staticmethod
    def get_most_used_endpoint(user_id):
        pipeline = [
            {"$match": {"user_id": ObjectId(user_id)}},
            {
                "$group": {
                    "_id": "$endpoint",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]

        result = list(mongo.db.api_logs.aggregate(pipeline))

        if result:
            return {
                "endpoint": result[0]["_id"],
                "count": result[0]["count"]
            }

        return None


