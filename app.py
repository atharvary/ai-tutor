from openai import OpenAI
import streamlit as st
from PIL import Image
import base64
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

# Access the API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client instance
client = OpenAI(api_key=openai_api_key)

# Set page configuration
st.set_page_config(page_title="IIT JEE Doubt Solver", layout="wide")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful tutor specializing in IIT JEE preparation. Provide clear, step-by-step explanations for questions related to Physics, Chemistry, and Mathematics."}
    ]

def encode_image_to_base64(image_file):
    """Convert uploaded image to base64 string"""
    # Read the file content
    bytes_data = image_file.getvalue()
    
    # Convert to base64
    base64_string = base64.b64encode(bytes_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_string}"

def get_response(messages):
    """Get response from OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",  # Using GPT-4 Vision model
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error getting response: {str(e)}")
        return None

# Main app interface
st.title("🎓 IIT JEE Doubt Solver Chatbot")
st.write("Ask your doubts with text or images, and get step-by-step solutions!")

# Create two columns for input methods
col1, col2 = st.columns(2)

with col1:
    text_question = st.text_area("Enter your question", height=100)

with col2:
    image_question = st.file_uploader(
        "Or upload an image of your question", 
        type=["jpg", "png", "jpeg"],
        help="Upload a clear image of your question or problem"
    )

# Preview uploaded image
if image_question:
    st.image(image_question, caption="Uploaded Question", use_column_width=True)

# Submit button
if st.button("Get Solution", type="primary"):
    if text_question or image_question:
        if image_question:
            # If there's an image, create a message with both text and image
            base64_image = encode_image_to_base64(image_question)
            
            content = [
                {
                    "type": "text", 
                    "text": text_question if text_question else "Please analyze this question and provide a step-by-step solution."
                },
                {
                    "type": "image_url",
                    "image_url": base64_image
                }
            ]
            user_message = {"role": "user", "content": content}
        else:
            # Text-only message
            user_message = {"role": "user", "content": text_question}

        # Add user message to history
        st.session_state["messages"].append(user_message)

        # Get AI response
        with st.spinner("Thinking..."):
            ai_response = get_response(st.session_state["messages"])

        if ai_response:
            # Add AI response to history
            st.session_state["messages"].append({"role": "assistant", "content": ai_response})

    else:
        st.warning("Please enter a question or upload an image.")

# Display chat history
st.subheader("Solution and Discussion")
for message in st.session_state["messages"]:
    if message["role"] == "user":
        if isinstance(message["content"], list):
            # For messages with images, only show the text part
            text_content = next((item["text"] for item in message["content"] if item["type"] == "text"), "")
            st.info(f"📝 Your Question: {text_content}")
        else:
            st.info(f"📝 Your Question: {message['content']}")
    elif message["role"] == "assistant":
        st.success(f"🤖 Solution: {message['content']}")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful tutor specializing in IIT JEE preparation. Provide clear, step-by-step explanations for questions related to Physics, Chemistry, and Mathematics."}
    ]
    st.rerun()
