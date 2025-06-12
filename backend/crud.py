from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional, Dict, Any
from datetime import datetime # For date filtering

from .config import POSTS_COLLECTION, PROFILES_COLLECTION, USERS_COLLECTION # Added USERS_COLLECTION
from . import schemas # Import schemas for type hinting and data validation
from .auth import get_password_hash # For hashing password during user creation

# --- User CRUD ---
def get_user_by_username(db: Database, username: str) -> Optional[schemas.UserInDB]:
    user_data = db[USERS_COLLECTION].find_one({"username": username})
    if user_data:
        return schemas.UserInDB(**user_data)
    return None

def create_user(db: Database, user: schemas.UserCreate) -> schemas.UserInDB:
    hashed_password = get_password_hash(user.password)
    user_db_data = user.dict(exclude={"password"}) # Pydantic v1 way, or user.model_dump() for v2
    user_db_data["hashed_password"] = hashed_password

    # Insert into database
    inserted_result = db[USERS_COLLECTION].insert_one(user_db_data)

    # Fetch the inserted user to return it including its DB-generated ID
    created_user_data = db[USERS_COLLECTION].find_one({"_id": inserted_result.inserted_id})
    if created_user_data:
        return schemas.UserInDB(**created_user_data)
    # This part should ideally not be reached if insert was successful
    raise Exception("Failed to create user or retrieve after creation.")


# --- Post CRUD ---
def get_posts_from_db(
    db: Database,
    skip: int = 0,
    limit: int = 20,
    keyword: Optional[str] = None,
    min_risk_score: Optional[int] = None,
    language: Optional[str] = None,
    source_type: Optional[str] = None,
    group_url: Optional[str] = None,
    page_url: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    entity_text: Optional[str] = None,
    entity_label: Optional[str] = None,
    sort_by: str = "post_time",
    sort_order: int = -1
) -> List[schemas.Post]: # Return list of Pydantic models

    query: Dict[str, Any] = {}

    if keyword:
        query["$or"] = [
            {"post_text": {"$regex": keyword, "$options": "i"}},
            {"keyword_search_term": {"$regex": keyword, "$options": "i"}},
            {"page_name": {"$regex": keyword, "$options": "i"}},
            {"group_name": {"$regex": keyword, "$options": "i"}},
            {"user_name": {"$regex": keyword, "$options": "i"}}
        ]
    if min_risk_score is not None:
        query["risk_score"] = {"$gte": min_risk_score}
    if language:
        query["language"] = language
    if source_type:
        query["source_type"] = source_type
    if group_url:
        query["group_url"] = group_url
    if page_url:
        query["page_url"] = page_url

    if date_from or date_to:
        query["post_time"] = {}
        if date_from:
            query["post_time"]["$gte"] = date_from
        if date_to:
            query["post_time"]["$lte"] = date_to

    if entity_text and entity_label:
        query["ner_entities"] = {
            "$elemMatch": {"text": {"$regex": entity_text, "$options": "i"}, "label": entity_label.upper()}
        }
    elif entity_text: # Search by entity text only, across any label
         query["ner_entities"] = {"$elemMatch": {"text": {"$regex": entity_text, "$options": "i"}}}


    valid_sort_fields = ["post_time", "risk_score", "scraped_timestamp", "analysis_timestamp"]
    if sort_by not in valid_sort_fields:
        sort_by = "post_time"
    if sort_order not in [-1, 1]:
        sort_order = -1

    posts_cursor = db[POSTS_COLLECTION].find(query).sort(sort_by, sort_order).skip(skip).limit(limit)

    return [schemas.Post(**post) for post in posts_cursor]


def get_post_by_id_from_db(db: Database, post_id: str) -> Optional[schemas.Post]:
    try:
        obj_id = ObjectId(post_id)
    except Exception:
        return None

    post_data = db[POSTS_COLLECTION].find_one({"_id": obj_id})
    if post_data:
        return schemas.Post(**post_data)
    return None

# --- Profile CRUD ---
def get_profiles_from_db(
    db: Database,
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None
) -> List[schemas.Profile]:
    query = {}
    if keyword:
        query["user_name"] = {"$regex": keyword, "$options": "i"}

    profiles_cursor = db[PROFILES_COLLECTION].find(query).skip(skip).limit(limit)
    return [schemas.Profile(**profile) for profile in profiles_cursor]

def get_profile_by_id_from_db(db: Database, profile_id: str) -> Optional[schemas.Profile]:
    try:
        obj_id = ObjectId(profile_id)
    except Exception:
        return None

    profile_data = db[PROFILES_COLLECTION].find_one({"_id": obj_id})
    if profile_data:
        return schemas.Profile(**profile_data)
    return None

# --- Analytics CRUD (Aggregation Functions) ---

def get_posts_count_by_risk_category(db: Database) -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$bucket": {
                "groupBy": "$risk_score",
                "boundaries": [0, 31, 71, 101], # 0-30 (Low), 31-70 (Medium), 71-100 (High)
                "default": "Other", # For any scores outside boundaries, though risk_score is capped at 100
                "output": {
                    "count": {"$sum": 1}
                }
            }
        },
        {
            "$project": {
                "_id": 0, # Exclude the default _id from $bucket
                "category": {
                    "$switch": {
                        "branches": [
                            {"case": {"$eq": ["$_id", 0]}, "then": "Low"}, # risk_score >= 0 and < 31
                            {"case": {"$eq": ["$_id", 31]}, "then": "Medium"},# risk_score >= 31 and < 71
                            {"case": {"$eq": ["$_id", 71]}, "then": "High"}  # risk_score >= 71 and < 101
                        ],
                        "default": "Unknown" # Should ideally not be hit if boundaries cover all scores
                    }
                },
                "count": 1
            }
        }
    ]
    results = list(db[POSTS_COLLECTION].aggregate(pipeline))
    # Ensure all defined categories are present, even if count is 0
    categories = ["Low", "Medium", "High"]
    existing_categories = {item['category'] for item in results}
    for cat_name in categories:
        if cat_name not in existing_categories:
            results.append({"category": cat_name, "count": 0})
    return results


def get_top_n_entities(db: Database, entity_label: Optional[str] = None, n: int = 10) -> List[Dict[str, Any]]:
    pipeline: List[Dict[str, Any]] = [
        {"$unwind": "$ner_entities"}
    ]

    match_stage: Dict[str, Any] = {}
    if entity_label:
        match_stage["ner_entities.label"] = entity_label.upper() # Match specific label if provided

    if match_stage: # Add $match stage only if there are conditions
        pipeline.append({"$match": match_stage})

    pipeline.extend([
        {
            "$group": {
                "_id": {
                    "text": "$ner_entities.text",
                    "label": "$ner_entities.label"
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": n},
        {
            "$project": {
                "_id": 0,
                "entity": "$_id.text",
                "label": "$_id.label",
                "count": 1
            }
        }
    ])
    return list(db[POSTS_COLLECTION].aggregate(pipeline))


def get_posts_count_by_language(db: Database) -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$match": { # Only include posts where language is detected and not undetermined
                "language": {"$exists": True, "$ne": None, "$nin": ["undetermined_no_text", "undetermined_detection_failed"]}
            }
        },
        {
            "$group": {
                "_id": "$language",
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}},
        {
            "$project": {
                "_id": 0,
                "language": "$_id",
                "count": 1
            }
        }
    ]
    return list(db[POSTS_COLLECTION].aggregate(pipeline))


def get_posts_time_series(db: Database, interval: str = "day") -> List[Dict[str, Any]]:
    group_id: Dict[str, Any]
    date_format: str

    if interval == "month":
        group_id = {
            "year": {"$year": "$post_time"},
            "month": {"$month": "$post_time"}
        }
        date_format = "%Y-%m" # For formatting the date string later
    elif interval == "week":
        group_id = {
            "year": {"$year": "$post_time"},
            "week": {"$week": "$post_time"}
        }
        # Formatting week as YYYY-WW might require careful construction or using ISODateFromParts later
        # For simplicity, we might just return year and week number
    else: # Default to day
        group_id = {
            "year": {"$year": "$post_time"},
            "month": {"$month": "$post_time"},
            "day": {"$dayOfMonth": "$post_time"}
        }
        date_format = "%Y-%m-%d"

    pipeline = [
        {
            "$match": {"post_time": {"$exists": True, "$ne": None}} # Ensure post_time exists
        },
        {
            "$group": {
                "_id": group_id,
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}} # Sort by the _id object (year, month, day/week)
    ]

    results = list(db[POSTS_COLLECTION].aggregate(pipeline))

    # Format the date string based on interval for easier consumption
    formatted_results = []
    for item in results:
        date_str = ""
        if interval == "day":
            try:
                # Construct date ensuring components are integers
                dt_obj = datetime(int(item['_id']['year']), int(item['_id']['month']), int(item['_id']['day']))
                date_str = dt_obj.strftime(date_format)
            except (ValueError, TypeError) as e:
                print(f"Error formatting date for item {item['_id']}: {e}")
                date_str = f"{item['_id'].get('year')}-{item['_id'].get('month',0):02d}-{item['_id'].get('day',0):02d} (raw)"

        elif interval == "month":
            try:
                dt_obj = datetime(int(item['_id']['year']), int(item['_id']['month']), 1)
                date_str = dt_obj.strftime(date_format)
            except (ValueError, TypeError) as e:
                 print(f"Error formatting date for item {item['_id']}: {e}")
                 date_str = f"{item['_id'].get('year')}-{item['_id'].get('month',0):02d} (raw)"
        elif interval == "week":
             # For week, MongoDB's $week starts from 0. strftime %U (week number, Sunday as first day) or %W (Monday as first day)
             # This requires careful alignment if specific week numbering standards are needed.
             # A simple representation:
            date_str = f"{item['_id']['year']}-W{item['_id']['week']:02d}"

        formatted_results.append({"date": date_str, "count": item["count"]})

    return formatted_results
