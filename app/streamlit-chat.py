import os
import json
import streamlit as st
from streamlit_chat import message  # Import the streamlit-chat component
import hashlib

# LangChain imports
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

# Define the base URL
BASE_URL = "https://www.udelphi.com"

# Directory to store FAISS indices
FAISS_INDEX_DIR = "./faiss_indices"

def get_index_name(json_file_path: str, embedding_model_name: str) -> str:
    """
    Generates a unique index name based on the JSON file path and embedding model name.
    """
    # Create a unique hash based on file path and embedding model
    unique_string = f"{json_file_path}_{embedding_model_name}"
    unique_hash = hashlib.md5(unique_string.encode()).hexdigest()
    return f"faiss_index_{unique_hash}"

# --------------------------------------------------
# 1. Load Chunked Data from JSON
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def load_chunks(json_file_path: str, base_url: str = "https://www.udelphi.com"):
    """
    Loads chunked data from a JSON file.
    Each item must have fields like: {"data_link": str, "chunk_id": str, "content": str}
    Ensures that each data_link is a complete URL.
    """
    if not os.path.exists(json_file_path):
        st.error(f"File not found: {json_file_path}")
        return []
    with open(json_file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    # Ensure each data_link is a complete URL
    for chunk in data:
        data_link = chunk.get("data_link", "")
        if data_link.startswith("#"):
            chunk["data_link"] = f"{base_url}{data_link}"
        elif not data_link.startswith("http"):
            # Handle cases where data_link is a relative URL without '#'
            chunk["data_link"] = f"{base_url}/{data_link.lstrip('/')}"
    
    return data

# --------------------------------------------------
# 2. Create FAISS Vector Store using Local Hugging Face Embeddings
# --------------------------------------------------
@st.cache_resource(show_spinner=True)
def create_vector_store(chunks, embedding_model_name="sentence-transformers/all-MiniLM-L6-v2", json_file_path="./data/content_chunks.json"):
    """
    Creates a FAISS vector store from chunk dictionaries using a local Hugging Face embeddings model.
    Saves the vector store to disk for future use.
    """
    # Initialize local Hugging Face embeddings
    embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # Separate the content and metadata from chunks
    texts = [chunk["content"] for chunk in chunks]
    metadatas = [
        {"data_link": chunk["data_link"], "chunk_id": chunk["chunk_id"]}
        for chunk in chunks
    ]

    # Create the FAISS index from texts
    vector_store = FAISS.from_texts(
        texts=texts,
        embedding=embedder,
        metadatas=metadatas
    )
    
    # Generate a unique index name
    index_name = get_index_name(json_file_path, embedding_model_name)
    index_path = os.path.join(FAISS_INDEX_DIR, index_name)
    
    # Ensure the directory exists
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)
    
    # Save the FAISS index to disk
    vector_store.save_local(index_path)
    
    return vector_store, index_path

@st.cache_resource(show_spinner=True)
def load_or_create_vector_store(chunks, embedding_model_name, json_file_path):
    """
    Loads the FAISS vector store from disk if available.
    Otherwise, creates a new one and saves it.
    """
    # Generate a unique index name
    index_name = get_index_name(json_file_path, embedding_model_name)
    index_path = os.path.join(FAISS_INDEX_DIR, index_name)
    
    if os.path.exists(index_path):
        st.info("Loading existing FAISS vector store from disk...")
        embedder = HuggingFaceEmbeddings(model_name=embedding_model_name)
        
        # Set allow_dangerous_deserialization to True
        vector_store = FAISS.load_local(index_path, embedder, allow_dangerous_deserialization=True)
        
        st.success("Vector store loaded successfully.")
    else:
        st.info("FAISS vector store not found. Creating a new one...")
        vector_store, index_path = create_vector_store(chunks, embedding_model_name, json_file_path)
        st.success("Vector store created and saved successfully.")
    
    return vector_store

# --------------------------------------------------
# 3. Build QA Chain using ChatGPT (gpt-3.5-turbo)
# --------------------------------------------------
@st.cache_resource(show_spinner=True)
def build_qa_chain(
    _vector_store,  # Leading underscore so Streamlit doesn't try to hash the FAISS object
    openai_api_key: str,
    model_name: str = "gpt-4o-mini-2024-07-18"  # Changed model name to an accessible one
):
    """
    Builds a RetrievalQA chain using FAISS as the retriever and
    ChatGPT as the LLM for question answering.
    """
    # Initialize ChatGPT LLM
    chat_llm = ChatOpenAI(
        openai_api_key=openai_api_key,
        model_name=model_name,
        temperature=0.7
    )

    # Use the vector store
    retriever = _vector_store.as_retriever(search_kwargs={"k": 3})

    # Build a "stuff"-type chain for Q&A
    qa_chain = RetrievalQA.from_chain_type(
        llm=chat_llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

# --------------------------------------------------
# 4. Streamlit Application
# --------------------------------------------------
def main():
    # Set page configuration
    st.set_page_config(
        page_title="DelphiLinkAI ChatBot",
        page_icon="💬",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    # Custom CSS for better styling (optional)
    st.markdown("""
        <style>
            .css-1d391kg {
                padding: 0;
            }
            /* Adjust chat container */
            .chat-container {
                max-width: 100%;
                height: 100%;
                padding: 10px;
                box-sizing: border-box;
            }
            /* Hide footer */
            .footer {
                display: none;
            }
            /* Adjust message bubbles */
            .streamlit-chat {
                height: 90%;
                overflow-y: auto;
            }
            .title {
                text-align: center;
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 0;
            }
            .subtitle {
                text-align: center;
                font-size: 1.2em;
                color: gray;
                margin-top: 0;
            }
            .footer {
                position: fixed;
                bottom: 0;
                width: 100%;
                text-align: center;
                font-size: 0.8em;
                color: gray;
            }
            .chat-container {
                max-width: 800px;
                margin: 0 auto;
            }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("<div class='title'>DelphiLinkAI ChatBot</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Ask your questions and get intelligent answers</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # 4.1 Check for OPENAI_API_KEY in environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("OPENAI_API_KEY not found. Please set it as an environment variable.")
        st.stop()

    # 4.2 Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Base URL input
        base_url = st.text_input(
            "Base URL",
            value="https://www.udelphi.com",
            help="Enter the base URL to prepend to data links starting with '#'."
        )
        
        # Path to chunked JSON
        json_file_path = st.text_input(
            "Path to Chunked JSON",
            value="./data/content_chunks.json"
        )

        # Embedding model selection
        embedding_model_name = st.selectbox(
            "Hugging Face Embedding Model",
            options=[
                "sentence-transformers/all-MiniLM-L6-v2",
                "sentence-transformers/all-distilroberta-v1",
                "sentence-transformers/paraphrase-MiniLM-L6-v2",
            ],
            index=0
        )

        # Model selection for ChatGPT
        model_name = st.selectbox(
            "ChatGPT Model",
            options=[
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4o-mini-2024-07-18"
            ],
            index=0
        )

        # Button to load data and build/load vector store
        if st.button("Load Data & Create/Load Vector Store"):
            with st.spinner("Loading chunked data..."):
                chunks = load_chunks(json_file_path, base_url=base_url)
                if not chunks:
                    st.error("No chunks loaded. Check the JSON file content or path.")
                    st.stop()
                st.success(f"Loaded {len(chunks)} chunks.")

            with st.spinner("Loading or creating FAISS index from local embeddings..."):
                vector_store = load_or_create_vector_store(chunks, embedding_model_name, json_file_path)

            with st.spinner("Building QA Chain with ChatGPT..."):
                qa_chain = build_qa_chain(vector_store, openai_api_key, model_name)
                st.success("QA Chain is ready!")

            # Save references in session state
            st.session_state["qa_chain"] = qa_chain

        # Option to delete existing FAISS index
        if st.button("Delete Existing Vector Store"):
            index_name = get_index_name(json_file_path, embedding_model_name)
            index_path = os.path.join(FAISS_INDEX_DIR, index_name)
            if os.path.exists(index_path):
                os.remove(index_path)
                st.success("Existing FAISS vector store deleted.")
            else:
                st.info("No existing FAISS vector store found to delete.")

        st.markdown("---")

        # ------------------------------
        # Added Reset Chat History Button
        # ------------------------------
        if st.button("Reset Chat History"):
            st.session_state["messages"] = []
            st.success("Chat history has been reset.")
        # ------------------------------

    # 4.3 Chat Interface
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    if "qa_chain" in st.session_state:
        # Input box for user question
        user_input = st.text_input("You:", key="input")

        if user_input:
            # Append user message
            st.session_state["messages"].append({"role": "user", "content": user_input})

            with st.spinner("Generating response..."):
                # Get the QA chain
                qa_chain = st.session_state["qa_chain"]
                # Get the response
                response = qa_chain({"query": user_input})

                answer = response["result"]
                source_docs = response.get("source_documents", [])

                # Append assistant message
                st.session_state["messages"].append({"role": "assistant", "content": answer})

            # Display chat messages with unique keys
            for idx, msg in enumerate(st.session_state["messages"]):
                if msg["role"] == "user":
                    message(msg["content"], is_user=True, key=f"user_{idx}")
                else:
                    message(msg["content"], is_user=False, key=f"assistant_{idx}")

            # Optionally, display source documents
            if source_docs:
                with st.expander("🔍 Source Documents"):
                    for i, doc in enumerate(source_docs, start=1):
                        st.markdown(
                            f"**Chunk {i}** (Data Link: [{doc.metadata.get('data_link')}]({doc.metadata.get('data_link')}))"
                        )
                        st.write(doc.page_content)
                        st.markdown("---")
    else:
        st.info("Use the sidebar to load data and create/load the vector store first.")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

if __name__ == "__main__":
    main()
