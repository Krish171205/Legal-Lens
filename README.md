# 📄 LegalLens – AI-Powered Legal Document Assistant

**LegalLens** is an intelligent legal document assistant that extracts, summarizes, and provides contextual legal assistance using **LLMs via Ollama**, **BigBird Pegasus**, and **RAG-based chatbot** powered by **Mistral** and **Pinecone**. The system is designed to handle multilingual legal documents from various formats including PDF, DOCX, DOC, TXT, and images.

---

## 🔧 Project Structure
```
Legal-lens/
├── extraction/
│   └── extraction.py
├── nlp/
│   ├── summarizer.py
│   └── rag.py
├── webapp/
│   ├── app.py
│   └── templates/
│       └── index.html
├── requirements.txt
└── readme.md
```

---

## 🌐 Features

- **Multi-format Document Extraction**:
  - PDF, DOCX, DOC, TXT, and common image formats
  - OCR support using `pytesseract` and `pdfplumber`
  
- **Multilingual Support**:
  - 17+ languages including Hindi, Marathi, Gujarati, Tamil, Bengali, etc.
  
- **Summarization**:
  - Legal text summarization using **BigBird Pegasus** for better long-text compression

- **RAG-based Legal Chatbot**:
  - Semantic search using **Pinecone**
  - Local query embedding and response generation using **Mistral 7B via Ollama**

- **Fully Modular Architecture**:
  - Clean codebase with `services/` for text extraction, summarization, and chatbot logic

- **Frontend in Flask**:
  - User uploads documents or enters raw legal text
  - Chat interface for legal Q&A powered by local models

---

## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/legallens.git
cd legallens
```

### 2. Create Virtual Environment & Install Dependencies
```
python3 -m venv venv
source venv/bin/activate  # on Windows use venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Install Ollama & Pull Required Models
Install Ollama: https://ollama.com/download
Then pull models:
```
ollama pull mistral
ollama pull bigbird-pegasus
```

### 4. Set Environment Variables
Create a .env file in the root:
```
PINECONE_API_KEY=your_key
PINECONE_ENV=your_env
PINECONE_INDEX_NAME=your_index
```

### 5. Run the Application
```
python backend/app.py
```
Then visit http://localhost:5000 in your browser.

---
# 📥 Input Formats Supported
---
| Format           | Support | Notes                                |
|------------------|---------|--------------------------------------|
| ``` .pdf ```             | ✅      | OCR fallback for scanned pages      |
| ``` .docx ```            | ✅      | Parsed via ``` python-docx ```              |
| ```.doc```             | ✅      | Extracted via ```catdoc```                |
| ```.txt```             | ✅      | Direct text read                    |
| ```.jpg```, ```.png```, ```.tiff```, etc. | ✅ | OCR via ```pytesseract```                 |

---
# 💡 How it Works

1. **User Uploads File** → Text is extracted using format-aware logic.
2. **Summarizer (BigBird Pegasus)** simplifies legal jargon to easy language.
3. **RAG Workflow** embeds text and queries using Ollama and Pinecone.
4. **Mistral LLM** generates accurate and contextual legal answers.


---
# 🚀 Technologies Used

| Component         | Technology                   |
|-------------------|------------------------------|
| Backend           | Python + Flask               |
| LLM               | Mistral 7B (Ollama)          |
| Summarizer        | BigBird Pegasus              |
| Embedding Store   | Pinecone Vector DB           |
| OCR               | Tesseract                    |
| File Handling     | PyMuPDF, python-docx         |
| Language Detection| langdetect                   |

---
# 🌍 Customization

To switch to other local models (e.g., Mixtral, LLaMA), just change the model name inside `ollama_wrapper.py`:

```python
# Edit this line to switch models
model = "mistral"  # replace with Ollama model tag like mixtral, llama3, etc.
```
---
# 🤝 Contributing
Pull requests and feedback are welcome! If you find bugs or want features, raise an issue.

