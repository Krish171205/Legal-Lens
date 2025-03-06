from flask import Flask, request, render_template, session
import requests
import os
import re
from pdf_to_text import extract_text  # Import text extraction function
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generates a random secret key for session management
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Set your Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

def decode_legal_text(legal_text):
    """Send legal text to Gemini for plain language simplification."""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [{
            "parts": [{
                "text": f"""
Simplify the following legal text into plain, easy-to-understand language while preserving its original meaning.

If the input text is in English, return the output in English.

If the input text is in another language, return the output in both English and the original language.

If the input text is in another language, format the output as follows:

ENGLISH:
(Simplified English version)

(Leave an empty line)

Language of input text:
(Simplified version in the original language)

Additionally, extract and mention any key details (such as names, dates, monetary amounts, or locations) found in the text. It should be displayed before the summary, but after language is mentioned.

Now, simplify this legal text:

{legal_text}
"""
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        simplified_output = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()

        # Formatting fixes
        simplified_output = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", simplified_output)  # Convert **bold** to <b>bold</b>
        simplified_output = re.sub(r"<br\s*/?>", "\n", simplified_output, flags=re.IGNORECASE)

        detected_language = "Multilingual (Original + English)" if "ENGLISH:" in simplified_output else "English"

        return simplified_output, detected_language
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}", "Unknown"
    except Exception:
        return "Error: Unexpected response format.", "Unknown"

def ask_gemini(question, context):
    """Ask questions based on the legal text and previous Q&A."""
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    data = {
        "contents": [{
            "parts": [{
                "text": f"""
Based on the following simplified legal text and previous Q&A, answer the user's question concisely:

Simplified Legal Text:
{context}

Previous Q&A:
{session.get('chat_history', '')}

Question: {question}
"""
            }]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        return response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Error: Unexpected response.").strip()
    except requests.exceptions.RequestException as e:
        return f"Error: {str(e)}"
    except Exception:
        return "Error: Unexpected response format."

@app.route("/", methods=["GET", "POST"])
def home():
    session.setdefault("chat_history", [])
    session.setdefault("simplified_text", None)
    session.setdefault("detected_language", "Unknown")

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        legal_text = request.form.get("legal_text", "").strip()

        extracted_text = ""
        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            uploaded_file.save(file_path)
            extracted_text = extract_text(file_path) or "Error extracting text."

        if legal_text or extracted_text:
            input_text = extracted_text if extracted_text else legal_text
            simplified_text, detected_language = decode_legal_text(input_text)
            session["simplified_text"] = simplified_text
            session["detected_language"] = detected_language
            session["chat_history"] = []  # Reset Q&A history when new text is submitted
            session.modified = True

    return render_template(
        "index.html",
        simplified_text=session.get("simplified_text", ""),
        detected_language=session.get("detected_language", "Unknown"),
        chat_history=session.get("chat_history", []),
    )

@app.route("/ask", methods=["POST"])
def ask():
    session.setdefault("chat_history", [])
    question = request.form.get("question", "").strip()
    simplified_text = session.get("simplified_text", "")

    if question and simplified_text:
        answer = ask_gemini(question, simplified_text)  # Pass legal text as context
        session["chat_history"].insert(0, {"question": question, "answer": answer})  # Insert at top
        session.modified = True

    return render_template(
        "index.html",
        simplified_text=session.get("simplified_text", ""),
        detected_language=session.get("detected_language", "Unknown"),
        chat_history=session.get("chat_history", []),
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

