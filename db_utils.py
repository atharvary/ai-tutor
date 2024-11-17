# db_utils.py
import os
import pymongo
from dotenv import load_dotenv
from bson import ObjectId
from datetime import datetime
import streamlit as st

load_dotenv()
client = pymongo.MongoClient(st.secrets["MONGODB_URI"])
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

def add_question(user_id, question_text, image_base64):
    # Add initial question as the first message in the chat history
    question_id = questions_collection.insert_one({
        "user_id": ObjectId(user_id),
        "question_text": question_text,
        "image_base64": image_base64,
        "messages": [{"role": "user", "content": question_text}],
        "timestamp": datetime.now()
    }).inserted_id
    return str(question_id)  # Return the question ID for future updates

def add_message_to_question(question_id, role, content):
    questions_collection.update_one(
        {"_id": ObjectId(question_id)},
        {"$push": {"messages": {"role": role, "content": content}}}
    )

def add_feedback(user_id, question_id, feedback_text, rating):
    feedback_collection.insert_one({
        "user_id": ObjectId(user_id),
        "question_id": ObjectId(question_id),
        "feedback_text": feedback_text,
        "rating": rating,
        "timestamp": datetime.now()
    })
