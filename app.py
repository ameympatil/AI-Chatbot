import streamlit as st
import uuid
import os
from src.utils import Utils  # Import Utils directly from your utils.py

# Initialize Utils
utils = Utils()

# Set the Streamlit page configuration
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
            try:
                # Save uploaded file temporarily
                temp_file_path = f"temp_{uploaded_file.name}"
                with open(temp_file_path, "wb") as buffer:
                    buffer.write(uploaded_file.getvalue())
                
                # Upload the document using Utils
                result = utils.upload_doc(temp_file_path)
                os.remove(temp_file_path)  # Clean up temporary file
                st.success("Document uploaded successfully!")
            except Exception as e:
                st.error(f"Error uploading document: {e}")

    st.header("Select Index")
    # Fetch available indexes
    try:
        indexes = utils.get_all_indexes()
        indexes.insert(0, "")  # Add empty option
        selected_index = st.selectbox("Choose an index", indexes)
    except Exception as e:
        st.error(f"Failed to fetch indexes: {e}")
        selected_index = ""

    # Past Chats header with New Session button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.header("Past Chats")
    with col2:
        if st.button("🔄", help="Start a new session"):
            start_new_session()
            st.rerun()

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

    # Send the question to the backend using Utils methods
    with st.spinner("Thinking..."):
        try:
            context = utils.similarity_search(prompt, selected_index)
            new_query = utils.rephrase(query)
            response = utils.qa(new_query, context)
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Update past sessions
            st.session_state.past_sessions[st.session_state.session_id] = st.session_state.messages.copy()
        except Exception as e:
            st.error(f"Error: {e}")

# Footer
st.markdown("---")
# st.markdown("Powered by FastAPI and Streamlit")
