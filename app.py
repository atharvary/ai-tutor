# from openai import OpenAI
# import streamlit as st
# from PIL import Image
# import base64
# import os
# from dotenv import load_dotenv
# import io
# import re

# # Load environment variables
# load_dotenv()

# # Access the API key
# openai_api_key = os.getenv("OPENAI_API_KEY")

# # Create OpenAI client instance
# client = OpenAI(api_key=openai_api_key)

# # Set page configuration
# st.set_page_config(page_title="IIT JEE Doubt Solver", layout="wide")

# # Add LaTeX support using custom CSS
# st.markdown("""
#     <style>
#         .katex { 
#             font-size: 1.1em; 
#         }
#         .stMarkdown {
#             font-size: 1.1em;
#         }
#     </style>
# """, unsafe_allow_html=True)

# # Initialize session state for chat history
# if "messages" not in st.session_state:
#     st.session_state["messages"] = [
#         {"role": "system", "content": """You are a helpful tutor specializing in IIT JEE preparation. 
#          Follow these strict rules for mathematical expressions:
#          1. For display/block equations (equations on their own line), ONLY use $$...$$
#          2. For inline equations (equations within text), ONLY use $...$
#          3. Never use [] or () as math delimiters
#          4. Always use \\text{} for units
#          5. Add proper spacing with \\, between numbers and units
         
#          Examples:
#          - Inline: The force is $F = ma$
#          - Display: The quadratic formula is:
#          $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
#          - Units: The mass is $10 \\, \\text{kg}$
         
#          Structure your responses as:
#          - **Question Analysis:** (Brief overview)
#          - **Solution Steps:** (Step-by-step solution)
#          - **Final Answer:** (Clear conclusion)
#          """}
#     ]

# def encode_image_to_base64(image_file):
#     """Convert uploaded image to base64 string"""
#     bytes_data = image_file.getvalue()
#     base64_string = base64.b64encode(bytes_data).decode('utf-8')
#     return base64_string

# def get_response(messages):
#     """Get response from OpenAI API"""
#     try:
#         response = client.chat.completions.create(
#             model="gpt-4-vision-preview",
#             messages=messages,
#             max_tokens=200,
#             temperature=0.7
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         st.error(f"Error getting response: {str(e)}")
#         return None

# def format_latex_response(response):
#     """Format the response to properly display LaTeX equations"""
#     if response is None:
#         return ""
    
#     # Step 1: Preserve existing correct LaTeX formatting
#     # Create a placeholder for existing correct LaTeX
#     preserved_latex = []
    
#     def preserve_latex(match):
#         preserved_latex.append(match.group(0))
#         return f"PRESERVED_LATEX_{len(preserved_latex)-1}"
    
#     # Preserve existing correct $$...$$ and $...$ formatting
#     response = re.sub(r'\$\$(.*?)\$\$', preserve_latex, response, flags=re.DOTALL)
#     response = re.sub(r'\$(.*?)\$', preserve_latex, response)
    
#     # Step 2: Fix incorrect LaTeX delimiters
#     # Convert [[...]] or ((...)) to $$...$$
#     response = re.sub(r'\[\[(.*?)\]\]|\(\((.*?)\)\)', lambda m: f"$${m.group(1) or m.group(2)}$$", response)
    
#     # Convert [...] to $...$ but only if not already properly formatted
#     response = re.sub(r'\[(.*?)\]', r'$\1$', response)
    
#     # Step 3: Restore preserved LaTeX
#     for i, latex in enumerate(preserved_latex):
#         response = response.replace(f"PRESERVED_LATEX_{i}", latex)
    
#     return response

# # Main app interface
# st.title("🎓 IIT JEE Doubt Solver Chatbot")
# st.write("Ask your doubts with text or images, and get step-by-step solutions!")

# # Create two columns for input methods
# col1, col2 = st.columns(2)

# with col1:
#     text_question = st.text_area("Enter your question", height=100)

# with col2:
#     image_question = st.file_uploader(
#         "Or upload an image of your question", 
#         type=["jpg", "png", "jpeg"],
#         help="Upload a clear image of your question or problem"
#     )

# # Preview uploaded image
# if image_question:
#     st.image(image_question, caption="Uploaded Question", use_column_width=True)

# # Submit button
# if st.button("Get Solution", type="primary"):
#     if text_question or image_question:
#         if image_question:
#             base64_image = encode_image_to_base64(image_question)
            
#             content = [
#                 {"type": "text", "text": text_question if text_question else "Please analyze this question and provide a step-by-step solution. Use LaTeX notation for all mathematical expressions."},
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         "url": f"data:image/jpeg;base64,{base64_image}"
#                     }
#                 }
#             ]
#             user_message = {"role": "user", "content": content}
#         else:
#             user_message = {"role": "user", "content": text_question}

#         st.session_state["messages"].append(user_message)

#         with st.spinner("Thinking..."):
#             ai_response = get_response(st.session_state["messages"])

#         if ai_response:
#             # Format the response for proper LaTeX rendering
#             formatted_response = format_latex_response(ai_response)
#             st.session_state["messages"].append({"role": "assistant", "content": formatted_response})

#     else:
#         st.warning("Please enter a question or upload an image.")

# # Display chat history
# st.subheader("Solution and Discussion")
# for message in st.session_state["messages"]:
#     if message["role"] == "user":
#         if isinstance(message["content"], list):
#             text_content = next((item["text"] for item in message["content"] if item["type"] == "text"), "")
#             st.info(f"📝 Your Question: {text_content}")
#         else:
#             st.info(f"📝 Your Question: {message['content']}")
#     elif message["role"] == "assistant" and message["role"] != "system":
#         st.markdown(f"🤖 **Solution:**\n{message['content']}", unsafe_allow_html=True)

# # Add a clear chat button
# if st.button("Clear Chat"):
#     st.session_state["messages"] = [
#         {"role": "system", "content": """You are a helpful tutor specializing in IIT JEE preparation. 
#          Provide clear, step-by-step explanations for questions related to Physics, Chemistry, and Mathematics.
#          Please use proper LaTeX notation for mathematical expressions, using $...$ for inline equations and $$....$$ for block equations."""}
#     ]
#     st.rerun()



import streamlit as st
import sqlite3
from openai import OpenAI
from PIL import Image
import base64
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client instance
client = OpenAI(api_key=openai_api_key)

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

# Database setup
conn = sqlite3.connect("users_feedback.db")
c = conn.cursor()

# Create tables for users and feedback if they don't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY, 
        password TEXT NOT NULL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        username TEXT, 
        feedback TEXT, 
        FOREIGN KEY(username) REFERENCES users(username)
    )
''')
conn.commit()

# Utility functions for user authentication
def signup(username, password):
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()

def login(username, password):
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    return c.fetchone()

def save_feedback(username, feedback):
    c.execute("INSERT INTO feedback (username, feedback) VALUES (?, ?)", (username, feedback))
    conn.commit()

# Helper functions for encoding image, OpenAI response, and LaTeX formatting
def encode_image_to_base64(image_file):
    bytes_data = image_file.getvalue()
    base64_string = base64.b64encode(bytes_data).decode('utf-8')
    return base64_string

def get_response(messages):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
        return None

def format_latex_response(response):
    """Format the response to properly display LaTeX equations"""
    if response is None:
        return ""
    
    # Step 1: Preserve existing correct LaTeX formatting
    # Create a placeholder for existing correct LaTeX
    preserved_latex = []
    
    def preserve_latex(match):
        preserved_latex.append(match.group(0))
        return f"PRESERVED_LATEX_{len(preserved_latex)-1}"
    
    # Preserve existing correct $$...$$ and $...$ formatting
    response = re.sub(r'\$\$(.*?)\$\$', preserve_latex, response, flags=re.DOTALL)
    response = re.sub(r'\$(.*?)\$', preserve_latex, response)
    
    # Step 2: Fix incorrect LaTeX delimiters
    # Convert [[...]] or ((...)) to $$...$$
    response = re.sub(r'\[\[(.*?)\]\]|\(\((.*?)\)\)', lambda m: f"$${m.group(1) or m.group(2)}$$", response)
    
    # Convert [...] to $...$ but only if not already properly formatted
    response = re.sub(r'\[(.*?)\]', r'$\1$', response)
    
    # Step 3: Restore preserved LaTeX
    for i, latex in enumerate(preserved_latex):
        response = response.replace(f"PRESERVED_LATEX_{i}", latex)
    
    return response

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
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button(option):
        if option == "Signup":
            try:
                signup(username, password)
                st.success("Signup successful. Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose another.")
        elif option == "Login":
            if login(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Logged in successfully.")
            else:
                st.error("Invalid username or password.")

# Main app content
if st.session_state["authenticated"]:
    st.title("🎓 IIT JEE Doubt Solver Chatbot")
    st.write("Ask your doubts with text or images, and get step-by-step solutions!")
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": """You are a helpful tutor specializing in IIT JEE preparation. 
            Follow these strict rules for mathematical expressions:
            1. For display/block equations (equations on their own line), ONLY use $$...$$
            2. For inline equations (equations within text), ONLY use $...$
            3. Never use [] or () as math delimiters
            4. Always use \\text{} for units
            5. Add proper spacing with \\, between numbers and units
            
            Examples:
            - Inline: The force is $F = ma$
            - Display: The quadratic formula is:
            $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
            - Units: The mass is $10 \\, \\text{kg}$
            
            Structure your responses as:
            - **Question Analysis:** (Brief overview)
            - **Solution Steps:** (Step-by-step solution)
            - **Final Answer:** (Clear conclusion)
            """}
        ]

    # Chatbot functionality
    col1, col2 = st.columns(2)
    with col1:
        text_question = st.text_area("Enter your question", height=100)
    with col2:
        image_question = st.file_uploader("Or upload an image of your question", type=["jpg", "png", "jpeg"])

    if image_question:
        st.image(image_question, caption="Uploaded Question", use_column_width=True)

    if st.button("Get Solution"):
        if text_question or image_question:
            if image_question:
                base64_image = encode_image_to_base64(image_question)
                content = [
                    {"type": "text", "text": text_question or "Please analyze this question and provide a solution."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
                user_message = {"role": "user", "content": content}
            else:
                user_message = {"role": "user", "content": text_question}

            st.session_state["messages"].append(user_message)
            with st.spinner("Thinking..."):
                ai_response = get_response(st.session_state["messages"])

            if ai_response:
                formatted_response = format_latex_response(ai_response)
                st.session_state["messages"].append({"role": "assistant", "content": formatted_response})

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
    feedback_text = st.text_area("Leave your feedback")
    if st.button("Submit Feedback"):
        save_feedback(st.session_state["username"], feedback_text)
        st.success("Thank you for your feedback!")

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state["messages"] = [
            {"role": "system", "content": """You are a helpful tutor specializing in IIT JEE preparation. 
            Provide clear, step-by-step explanations for questions related to Physics, Chemistry, and Mathematics.
            Please use proper LaTeX notation for mathematical expressions, using $...$ for inline equations and $$....$$ for block equations."""}
        ]
        st.rerun()

else:
    st.warning("Please log in to access the app.")
