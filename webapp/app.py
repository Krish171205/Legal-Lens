import os
from flask import Flask, request, render_template, session
from werkzeug.utils import secure_filename

from extraction.extraction import extract_text, detect_language
from nlp.summarizer import summarize
from nlp.rag import RAG

# Flask setup
app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize RAG retriever
pinecone_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
rag = RAG(
    index_name="legal-lens",
    pinecone_api_key=pinecone_key,
    pinecone_env=pinecone_env
)

@app.route("/", methods=["GET", "POST"])
def home():
    session.setdefault("chat_history", [])
    session.setdefault("simplified_text", "")
    session.setdefault("detected_language", "unknown")

    if request.method == "POST":
        file = request.files.get("file")
        raw = request.form.get("legal_text", "").strip()
        text = ""
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(path)
            text = extract_text(path)
        else:
            text = raw

        if text:
            # Summarize and index
            session["simplified_text"] = summarize(text)
            session["detected_language"] = detect_language(text)
            rag.index_document(doc_id=filename or "raw_input", text=text)
            session["chat_history"] = []
            session.modified = True

    return render_template(
        "index.html",
        simplified_text=session["simplified_text"],
        detected_language=session["detected_language"],
        chat_history=session["chat_history"],
    )

@app.route("/ask", methods=["POST"])
def ask():
    q = request.form.get("question", "").strip()
    if q:
        contexts = rag.query(q)
        ans = rag.generate_answer(q, contexts)
        session["chat_history"].insert(0, {"question": q, "answer": ans})
        session.modified = True

    return render_template(
        "index.html",
        simplified_text=session["simplified_text"],
        detected_language=session["detected_language"],
        chat_history=session["chat_history"],
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))