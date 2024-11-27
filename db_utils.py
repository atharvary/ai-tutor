# db_utils.py
import os
import pymongo
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime

load_dotenv()
client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
db = client["doubt_solver_app"]

# Access specific collections
users_collection = db["users"]
questions_collection = db["questions"]
feedback_collection = db["feedback"]

def login(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return str(user["_id"])  # Return ObjectId as a string
    return None

def add_user(username, password_hash):
    users_collection.insert_one({"username": username, "password_hash": password_hash})

def get_user(username):
    return users_collection.find_one({"username": username})

def count_user_messages(question_id):
    """Count the number of user messages for a specific question"""
    question = questions_collection.find_one({"_id": ObjectId(question_id)})
    if not question or "messages" not in question:
        return 0
    
    # Count messages where role is "user"
    user_messages = sum(1 for msg in question["messages"] if msg["role"] == "user")
    return user_messages

def get_question(question_id):
    """Retrieve a question document by its ID"""
    return questions_collection.find_one({"_id": ObjectId(question_id)})

# Modify the add_question function in db_utils.py
def add_question(user_id, question_text, image_base64, subject, question_type):
    question_id = questions_collection.insert_one({
        "user_id": ObjectId(user_id),
        "question_text": question_text,
        "image_base64": image_base64,
        "subject": subject,
        "question_type": question_type,
        "messages": [{"role": "user", "content": question_text}],
        "timestamp": datetime.now()
    }).inserted_id
    return str(question_id)

def add_message_to_question(question_id, role, content, token_info=None):
    """Add a message to a question with optional token usage information"""
    message_data = {
        "role": role,
        "content": content,
        "timestamp": datetime.now()
    }
    
    # Add token info if provided (for assistant messages)
    if token_info:
        message_data["token_usage"] = token_info
        
    questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$push": {"messages": message_data}}
    )

def add_feedback(user_id, question_id, feedback_text, rating):
    feedback_collection.insert_one({
        "user_id": ObjectId(user_id),
        "question_id": ObjectId(question_id),
        "feedback_text": feedback_text,
        "rating": rating,
        "timestamp": datetime.now()
    })
