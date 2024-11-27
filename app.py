import streamlit as st
import base64
import os
import re
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv
import bcrypt
from db_utils import add_question, add_user, get_user, add_feedback, add_message_to_question, count_user_messages
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from datetime import datetime

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
# imagekit_private_key = os.getenv("IMAGEKIT_PRIVATE_KEY")
# imagekit_public_key = os.getenv("IMAGEKIT_PUBLIC_KEY")
# imagekit_url_endpoint = os.getenv("IMAGEKIT_URL_ENDPOINT")

# Create OpenAI client instance
client = OpenAI(api_key=openai_api_key)

# Initialize ImageKit with direct values
imagekit = ImageKit(
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL_ENDPOINT")
)

# print("Private Key:", os.getenv('IMAGEKIT_PRIVATE_KEY'))
# print("Public Key:", os.getenv('IMAGEKIT_PUBLIC_KEY'))
# print("URL Endpoint:", os.getenv('IMAGEKIT_URL_ENDPOINT'))


# Add these constants after the imports
SUBJECTS = ["None", "Physics", "Chemistry", "Mathematics", "Biology"]
QUESTION_TYPES = [
    "None",
    "Single Correct MCQ",
    "More than One Correct",
    "Integer Type",
    "Numerical Value"
]

# Set page configuration
st.set_page_config(page_title="IIT JEE Doubt Solver", layout="wide")

# Add LaTeX support using custom CSS
st.markdown("""
    <style>
        .katex { 
            font-size: 1.1em; 
        }
        .stMarkdown {
            font-size: 1.1em;
        }
    </style>
""", unsafe_allow_html=True)

# Helper functions for encoding image, OpenAI response, and LaTeX formatting
# def encode_image_to_base64(image_file):
#     bytes_data = image_file.getvalue()
#     base64_string = base64.b64encode(bytes_data).decode('utf-8')
#     return base64_string

# Replace the encode_image_to_base64 function with this new function
def upload_image_to_imagekit(image_file, subject):
    try:
        # 1. First, let's see what we get from Streamlit
        # st.write("Debug: Image file details from Streamlit:")
        # st.write(f"File name: {image_file.name}")
        # st.write(f"File type: {image_file.type}")
        # st.write(f"File size: {image_file.size} bytes")

        # 2. Convert Streamlit file to bytes and save temporarily
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            # Write the Streamlit file content to temp file
            tmp_file.write(image_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # 3. Upload using the temporary file
        with open(tmp_file_path, 'rb') as file:
            upload_response = imagekit.upload_file(
                file=file,
                file_name=image_file.name,
                options=UploadFileRequestOptions(
                    folder=f"/{subject.lower()}" if subject and subject != "None" else "/general",
                    is_private_file=False,
                    use_unique_file_name=True,
                    response_fields=["is_private_file", "tags"],
                    tags=[subject.lower() if subject and subject != "None" else "general"]
                )
            )
        
        # 4. Clean up the temporary file
        os.unlink(tmp_file_path)
        
        # 5. Generate transformed URL
        image_url = imagekit.url({
            "path": upload_response.file_path,
            "transformation": [{
                "height": "300",
                "width": "300"
            }]
        })
        
        # st.write("Debug: Generated URL:", image_url)
        return image_url

    except Exception as e:
        st.error(f"Error uploading image: {str(e)}")
        return None
    

def get_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1200,
            temperature=0.7
        )
        # Return both the response content and token usage
        return {
            "content": response.choices[0].message.content,
            "token_usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "model": response.model
            }
        }
    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
        return None


def format_latex_response(response):
    if response is None:
        return ""
    
    # Step 1: Fix LaTeX delimiters
    response = response.replace(r'\(', '$')
    response = response.replace(r'\)', '$')
    response = response.replace(r'\[', '$$')
    response = response.replace(r'\]', '$$')
    
    # Step 2: Fix common LaTeX commands
    latex_commands = {
        r'(?<!\\)alpha': r'\\alpha',
        r'(?<!\\)beta': r'\\beta',
        r'(?<!\\)gamma': r'\\gamma',
        r'(?<!\\)delta': r'\\delta',
        r'(?<!\\)pi': r'\\pi',
        r'(?<!\\)theta': r'\\theta',
        r'(?<!\\)mu': r'\\mu',
        r'(?<!\\)quad': r'\\quad',
        r'(?<!\\)text': r'\\text',
        r'(?<!\\)mod': r'\\mod',
        r'(?<!\\)div': r'\\div'
    }
    
    for pattern, replacement in latex_commands.items():
        response = re.sub(pattern, replacement, response)
    
    # Step 3: Handle display equations
    # Split into lines while preserving empty lines
    lines = response.splitlines()
    formatted_lines = []
    
    for line in lines:
        # If line contains only a display equation
        if line.strip().startswith('$$') and line.strip().endswith('$$'):
            formatted_lines.extend(['', line.strip(), ''])
        else:
            formatted_lines.append(line)
    
    # Rejoin lines
    response = '\n'.join(formatted_lines)
    
    # Step 4: Clean up spacing
    # Remove multiple blank lines
    response = re.sub(r'\n{3,}', '\n\n', response)
    # Fix spacing around inline equations
    response = re.sub(r'(?<!\$)\$(?!\$)([^\$]+?)\$(?!\$)', r' $\1$ ', response)
    # Remove extra spaces
    response = re.sub(r' +', ' ', response)
    
    return response.strip()

# Add this new function after the format_latex_response function
def update_system_message(subject, question_type):
    return {
        "role": "system",
        "content": f"""You are a helpful tutor specializing in IIT JEE preparation. 
        Current Subject: {subject if subject else 'Not Specified'}
        Question Type: {question_type if question_type else 'Not Specified'}
        
        Follow these strict rules for mathematical expressions:
        1. For display/block equations (equations on their own line), ONLY use $$...$$
        2. For inline equations (equations within text), ONLY use $...$
        3. Never use [] or () as math delimiters
        4. Always use \\text{{}} for units
        5. Add proper spacing with \\, between numbers and units
        
        Structure your responses as:
        - **Question Analysis:** (Brief overview)
        - **Solution Steps:** (Step-by-step solution, try to stick to the point)
        - **Final Answer:** (Clear conclusion, matching the question type format)"""
    }

# Authentication flow
st.sidebar.title("Login / Signup")
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = ""

if st.session_state["authenticated"]:
    st.sidebar.write(f"Welcome, {st.session_state['username']}!")
    if st.sidebar.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = ""
else:
    # Signup/Login Form
    option = st.sidebar.selectbox("Choose Option", ["Login", "Signup"])
    username = st.sidebar.text_input("Phone Number")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button(option):
        if option == "Signup":
            if not get_user(username):
                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                add_user(username, hashed_password)
                # st.success("Signup successful. Please log in.")
                st.sidebar.success("Signup successful. Please log in.")
            else:
                # st.error("Username already exists. Please choose another.")
                st.sidebar.error("Username already exists. Please choose another.")
        elif option == "Login":
            user = get_user(username)
            if user and bcrypt.checkpw(password.encode(), user["password_hash"]):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["user_id"] = user["_id"]
                # st.success("Logged in successfully.")
                st.sidebar.success("Logged in successfully.")
                
            else:
                # st.error("Invalid username or password.")
                st.sidebar.error("Invalid username or password.")


# Main app content
if st.session_state["authenticated"]:
    st.title("🎓 IIT JEE Doubt Solver Chatbot")
    st.write("Ask your doubts with text or images, and get step-by-step solutions!")

    # Modify the subject and question type selection part
    col1, col2 = st.columns(2)
    with col1:
        selected_subject = st.selectbox("Select Subject", SUBJECTS, key="subject_selector")
        if "prev_subject" not in st.session_state:
            st.session_state["prev_subject"] = selected_subject
    with col2:
        selected_question_type = st.selectbox("Select Question Type", QUESTION_TYPES, key="type_selector")
        if "prev_type" not in st.session_state:
            st.session_state["prev_type"] = selected_question_type

    # Initialize or update messages
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    
    # Always update the system message when rendering
    system_msg = update_system_message(selected_subject, selected_question_type)
    
    # Update the messages list
    if not st.session_state["messages"]:
        st.session_state["messages"] = [system_msg]
    else:
        st.session_state["messages"][0] = system_msg

    # Store current selections for next comparison
    st.session_state["prev_subject"] = selected_subject
    st.session_state["prev_type"] = selected_question_type

    # Add this line after updating the system message
    # st.write("Current System Message:", st.session_state["messages"][0]["content"])

    # Chatbot functionality
    col1, col2 = st.columns(2)
    with col1:
        text_question = st.text_area("Enter your question", height=100)
    with col2:
        image_question = st.file_uploader("Or upload an image of your question", type=["jpg", "png", "jpeg"])
        
    # Image preview and upload handling
    if image_question:
        # Check if this image has already been uploaded
        file_hash = hash(image_question.getvalue())
        
        if "current_image_hash" not in st.session_state or st.session_state.current_image_hash != file_hash:
            # New image uploaded
            st.session_state.current_image_hash = file_hash
            image_url = upload_image_to_imagekit(image_question, selected_subject)
            if image_url:
                st.session_state.current_image_url = image_url
        
        # Display preview
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(
            image_question,
            caption="Uploaded Question",
            # use_column_width=False,
            width=200
        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Get Solution"):
        if text_question or image_question:
            # Check if we're continuing an existing question
            current_question_id = st.session_state.get("question_id")
            can_proceed = True
            
            if current_question_id:
                # Check message limit
                user_message_count = count_user_messages(current_question_id)
                if user_message_count >= 3:
                    st.error("You've reached the maximum number of follow-up questions (3) for this topic. Please click 'New Question' to start a new topic.")
                    can_proceed = False
            
            if can_proceed:
                # Initialize user_message
                user_message = None

                # Handle image upload and prepare user message
                if image_question:
                    image_url = upload_image_to_imagekit(image_question, selected_subject)
                    if not image_url:
                        st.error("Failed to upload image")
                        can_proceed = False  # Set flag to prevent further processing
                    else:
                        # Create new question document
                        question_id = add_question(
                            st.session_state["user_id"], 
                            text_question, 
                            image_url,
                            selected_subject, 
                            selected_question_type
                        )
                        st.session_state["question_id"] = question_id

                        # Prepare user message with ImageKit URL
                        content = [
                            {"type": "text", "text": text_question if text_question else "Please analyze this question and provide a step-by-step solution. Use LaTeX notation for all mathematical expressions."},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                        user_message = {"role": "user", "content": content}
                else:
                    # Text-only question
                    if not current_question_id:
                        question_id = add_question(
                            st.session_state["user_id"], 
                            text_question, 
                            None,
                            selected_subject, 
                            selected_question_type
                        )
                        st.session_state["question_id"] = question_id
                    else:
                        question_id = current_question_id
                    
                    user_message = {"role": "user", "content": text_question}

                # Ensure user_message is defined before using it
                if user_message:
                    # Add the user message to session state and database
                    st.session_state["messages"].append(user_message)
                    add_message_to_question(question_id, "user", user_message["content"])

                    # Get AI response
                    with st.spinner("Thinking..."):
                        ai_response = get_response(st.session_state["messages"])
                        print("\n\n\n")
                        print(st.session_state["messages"])
                        print("\n\n\n")
                        print(ai_response)

                    if ai_response:
                        formatted_response = format_latex_response(ai_response["content"])
                        response_message = {"role": "assistant", "content": formatted_response}
                        st.session_state["messages"].append(response_message)
                        
                        # Add message to database with token usage information
                        add_message_to_question(
                            question_id, 
                            "assistant", 
                            formatted_response,
                            token_info=ai_response.get("token_usage")
                        )
        else:
            st.warning("Please enter a question or upload an image.")
    
    # Display chat history
    st.subheader("Solution and Discussion")
    for message in st.session_state["messages"]:
        if message["role"] == "user":
            st.info(f"📝 Your Question: {message['content'] if isinstance(message['content'], str) else 'Image uploaded'}")
        elif message["role"] == "assistant":
            st.markdown(f"🤖 **Solution:**\n{message['content']}", unsafe_allow_html=True)

    # Feedback section
    st.subheader("Feedback")
    feedback_text = st.text_area("Leave your feedback", height=70)
    if st.button("Submit Feedback"):
        add_feedback(st.session_state["user_id"], question_id=st.session_state["question_id"], feedback_text=feedback_text, rating=None)
        st.success("Thank you for your feedback!")

    # Modify the New Question button to clear the question_id
    if st.button("New Question 🆕"):
        # Clear the question ID to start fresh
        if "question_id" in st.session_state:
            del st.session_state["question_id"]
        
        # Reset messages with the stored selections
        st.session_state["messages"] = [update_system_message(selected_subject, selected_question_type)]
        
        # Store the selections in session state for persistence
        st.session_state["prev_subject"] = selected_subject
        st.session_state["prev_type"] = selected_question_type
            
        st.rerun()

else:
    st.warning("Please log in to access the app.")
