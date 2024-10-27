import streamlit as st
import uuid
import os
from src.utils import Utils
from streamlit_lottie import st_lottie
import requests

# Initialize Utils
utils = Utils()

# Set the Streamlit page configuration
st.set_page_config(page_title="Smart Q&A", layout="wide", page_icon="🤖")

# Custom CSS to make the UI more attractive and user-friendly with a vibrant theme
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #000000 100%);
        color: #ecf0f1;
    }
    .stButton>button {
        background-color: #e74c3c;
        color: #ecf0f1;
        border-radius: 20px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #c0392b;
        transform: scale(1.05);
    }
    .stTextInput>div>div>input {
        border-radius: 20px;
        border: 2px solid #3498db;
        background-color: #34495e;
        color: #ecf0f1;
        padding: 10px 15px;
    }
    .stSelectbox>div>div>select {
        border-radius: 20px;
        border: 2px solid #3498db;
        background-color: #34495e;
        color: #ecf0f1;
        padding: 10px 15px;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 4px 6px rgba(52, 152, 219, 0.1);
    }
    .chat-message.user {
        background-color: #34495e;
    }
    .chat-message.assistant {
        background-color: #2c3e50;
    }
    .chat-message .avatar {
        width: 15%;
    }
    .chat-message .message {
        width: 85%;
        padding: 0 1.5rem;
        color: #ecf0f1;
    }
    .stMarkdown {
        color: #ecf0f1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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


# Function to load Lottie animation
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def main():
    # Main title with Lottie animation
    col1, col2 = st.columns([1, 3])
    with col1:
        lottie_wizard = load_lottieurl(
            "https://assets9.lottiefiles.com/packages/lf20_xyadoh9h.json"
        )
        st_lottie(lottie_wizard, speed=1, height=150, key="initial")
    with col2:
        st.title("🤖 Smart Q&A")
        st.markdown(
            "<h3 style='color: #f39c12;'>Get intelligent answers from your personal documents!</h3>",
            unsafe_allow_html=True,
        )

    # Sidebar for uploading documents, selecting indexes, and showing past chats
    with st.sidebar:
        st.sidebar.image("https://your-logo-url.com/logo.png", width=200)

        st.header("📚 Document Upload")
        uploaded_file = st.file_uploader(
            "Choose a document to upload", type=["txt", "pdf", "docx"]
        )
        if uploaded_file is not None:
            if st.button("Upload Document 🪄", key="upload_btn"):
                with st.spinner("Uploading document..."):
                    try:
                        temp_file_path = f"temp_{uploaded_file.name}"
                        with open(temp_file_path, "wb") as buffer:
                            buffer.write(uploaded_file.getvalue())
                        result = utils.upload_doc(temp_file_path)
                        os.remove(temp_file_path)
                        st.success("Document successfully uploaded! ✨")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")

        st.header("🔮 Select Document Index")
        try:
            indexes = utils.get_all_indexes()
            indexes.insert(0, "")
            selected_index = st.selectbox(
                "Choose your document index", indexes, key="index_select"
            )
        except Exception as e:
            st.error(f"Failed to fetch indexes: {e}")
            selected_index = ""

        st.header("📜 Chat History")
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄", key="new_chat_btn"):
                start_new_session()
                st.rerun()

        for session_id, messages in st.session_state.past_sessions.items():
            if st.button(f"📜 Chat {session_id[:8]}", key=f"session_{session_id}"):
                st.session_state.session_id = session_id
                st.session_state.messages = messages
                st.rerun()

    # Main content area
    st.header(f"🤖 Chat Session: {st.session_state.session_id[:8]}")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(
                f'<div class="chat-message {message["role"]}"><div class="message">{message["content"]}</div></div>',
                unsafe_allow_html=True,
            )

    # Chat input
    if prompt := st.chat_input("Ask anything about your documents..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(
                f'<div class="chat-message user"><div class="message">{prompt}</div></div>',
                unsafe_allow_html=True,
            )

        query = {
            "id": st.session_state.session_id,
            "query": prompt,
            "index_name": selected_index,
        }

        with st.spinner("🤖 Processing answer..."):
            try:
                new_query = utils.rephrase(query)
                context = utils.similarity_search(new_query, selected_index)
                response = utils.qa(new_query, context)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                with st.chat_message("assistant"):
                    st.markdown(
                        f'<div class="chat-message assistant"><div class="message">{response}</div></div>',
                        unsafe_allow_html=True,
                    )

                st.session_state.past_sessions[st.session_state.session_id] = (
                    st.session_state.messages.copy()
                )
            except Exception as e:
                st.error(f"Failed to process answer: {e}")

    # Footer
    st.markdown("---")


if __name__ == "__main__":
    main()
