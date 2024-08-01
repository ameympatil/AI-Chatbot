import streamlit as st
import requests
import json
from typing import List
import uuid

# Set the FastAPI backend URL
BACKEND_URL = "http://localhost:8000"  # Adjust this if your backend is hosted elsewhere

st.set_page_config(page_title="Document Q&A Chatbot", layout="wide")

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "past_sessions" not in st.session_state:
    st.session_state.past_sessions = {}

# Function to start a new session
def start_new_session():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

# Main title
st.title("Document Q&A Chatbot")

# Sidebar for uploading documents, selecting indexes, and showing past chats
with st.sidebar:
    st.header("Document Upload")
    uploaded_file = st.file_uploader("Choose a document to upload", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        if st.button("Upload Document"):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{BACKEND_URL}/upload_doc", files=files)
            if response.status_code == 200:
                st.success("Document uploaded successfully!")
            else:
                st.error(f"Error uploading document: {response.json()['detail']}")

    st.header("Select Index")
    # Fetch available indexes
    response = requests.get(f"{BACKEND_URL}/get_indexes")
    if response.status_code == 200:
        indexes: List[str] = response.json()
        indexes.insert(0, "")  # Add empty option
        selected_index = st.selectbox("Choose an index", indexes)
    else:
        st.error("Failed to fetch indexes")
        selected_index = ""

    # Past Chats header with New Session button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("Past Chats")
    with col2:
        if st.button("🔄", help="Start a new session"):
            start_new_session()
            st.st.rerun()

    for session_id, messages in st.session_state.past_sessions.items():
        if st.button(f"Session {session_id[:8]}"):
            st.session_state.session_id = session_id
            st.session_state.messages = messages
            st.rerun()

# Main content area
st.header(f"Chat (Session ID: {st.session_state.session_id[:8]})")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare the query
    query = {
        "id": st.session_state.session_id,
        "query": prompt,
        "index_name": selected_index
    }

    # Send the question to the backend
    with st.spinner("Thinking..."):
        response = requests.post(f"{BACKEND_URL}/qa", json=query)
    
    if response.status_code == 200:
        result = response.json()
        assistant_response = result["response"]
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        with st.chat_message("assistant"):
            st.markdown(assistant_response)
        
        # Update past sessions
        st.session_state.past_sessions[st.session_state.session_id] = st.session_state.messages.copy()
    else:
        st.error(f"Error: {response.json()['detail']}")

# Footer
st.markdown("---")
# st.markdown("Powered by FastAPI and Streamlit")
