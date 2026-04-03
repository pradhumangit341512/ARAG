"""
app.py — Agentic RAG: Web Interface
Upload a PDF and ask questions about it.
"""
import os
from flask import Flask, render_template, request, jsonify
from graph_rag.document_parser import parse_pdf
from utils.llm_client import chat

import config

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20 MB max upload

UPLOAD_DIR = os.path.join(config.BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store parsed PDF text in memory for the current session
pdf_context: dict = {"filename": "", "text": ""}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file provided."})

    file = request.files["file"]
    if not file.filename.endswith(".pdf"):
        return jsonify({"success": False, "error": "Only PDF files are supported."})

    # Save the file
    filepath = os.path.join(UPLOAD_DIR, file.filename)
    file.save(filepath)

    # Parse PDF into text chunks
    try:
        chunks = parse_pdf(filepath, max_pages=50)
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to read PDF: {e}"})

    if not chunks:
        return jsonify({"success": False, "error": "Could not extract text from this PDF."})

    # Combine all chunks into one context string
    full_text = "\n\n".join(chunk["text"] for chunk in chunks)

    # Truncate to stay within Groq free tier token limits (~6000 tokens)
    words = full_text.split()
    if len(words) > 4000:
        full_text = " ".join(words[:4000])

    pdf_context["filename"] = file.filename
    pdf_context["text"] = full_text

    return jsonify({
        "success": True,
        "message": f"PDF processed: {len(chunks)} pages extracted, {len(words)} words loaded."
    })


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"success": False, "error": "Please enter a question."})

    if not pdf_context["text"]:
        return jsonify({"success": False, "error": "No PDF uploaded yet. Please upload a PDF first."})

    if not config.GROQ_API_KEY:
        return jsonify({"success": False, "error": "GROQ_API_KEY not set in .env file."})

    system_prompt = (
        "You are an expert document analyst. Answer the user's question based ONLY on the "
        "document content provided below. If the answer is not found in the document, say so clearly.\n\n"
        f"--- DOCUMENT: {pdf_context['filename']} ---\n"
        f"{pdf_context['text']}\n"
        "--- END DOCUMENT ---"
    )

    try:
        answer = chat(prompt=question, system=system_prompt, temperature=0.2)
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        return jsonify({"success": False, "error": f"LLM error: {e}"})


if __name__ == "__main__":
    print("\n  Agentic RAG — Web Interface")
    print("  Open http://127.0.0.1:5000 in your browser\n")
    app.run(debug=True, port=5000)
