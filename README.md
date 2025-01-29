# Delphi Software AI ChatBot 💬

Welcome to the **Delphi Software AI ChatBot**, a smart and efficient chatbot designed to provide intelligent answers based on your organization's data. Built with Streamlit, LangChain, FAISS, and HuggingFace embeddings, this chatbot offers a seamless and user-friendly experience.

## 🚀 Features

- **Intelligent Q&A**: Leverages advanced language models to answer user queries accurately.
- **Efficient Data Retrieval**: Utilizes FAISS vector stores for fast and relevant information retrieval.
- **Customizable Embeddings**: Supports multiple HuggingFace embedding models to suit your needs.
- **User-Friendly Interface**: Features a sleek, floating chat window for easy access without cluttering the main page.
- **Persistent Data Storage**: Saves and loads vector stores to optimize performance and reduce load times.

## 🛠️ Technologies Used

- [Streamlit](https://streamlit.io/) for the interactive web interface.
- [LangChain](https://github.com/hwchase17/langchain) for chaining language models.
- [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search.
- [HuggingFace Embeddings](https://huggingface.co/models) for text embeddings.
- [ChatGPT](https://openai.com/blog/chatgpt) as the language model backend.

## 📥 Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/delphi-ai-chatbot.git
   cd delphi-ai-chatbot
   ```
2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```
3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the root directory and add your OpenAI API key:

   ```plaintext
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Prepare Your Data**

   Ensure your data is chunked and saved in a JSON file, e.g., `./data/content_chunks.json`, following the structure:

   ```json
   [
       {
           "data_link": "#/careers/2207",
           "chunk_id": "1",
           "content": "Your content here..."
       },
       ...
   ]
   ```

## 🎯 Usage

1. **Run the Streamlit App**

   ```bash
   streamlit run app.py
   ```

2. **Interact with the ChatBot**
   - Use the configuration sidebar to set the base URL, path to your JSON data, select embedding and ChatGPT models.
   - Click on the 💬 button at the bottom-right to open the chat window.
   - Ask your questions and receive intelligent answers in real-time.
