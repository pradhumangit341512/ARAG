"""
graph_rag/document_parser.py
Parse technical documents (PDF / TXT) into raw text chunks.
"""
import os
import fitz          # PyMuPDF
from rich.console import Console

console = Console()


def parse_pdf(filepath: str, max_pages: int = 50) -> list[dict]:
    """Extract text from a PDF page by page."""
    doc = fitz.open(filepath)
    chunks = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text = page.get_text("text").strip()
        if text:
            chunks.append({"page": i + 1, "text": text, "source": os.path.basename(filepath)})
    doc.close()
    return chunks


def parse_txt(filepath: str) -> list[dict]:
    """Split a plain-text file into ~500-word chunks."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    words   = content.split()
    size    = 500
    chunks  = []
    for i in range(0, len(words), size):
        chunk_text = " ".join(words[i : i + size])
        chunks.append({"page": i // size + 1, "text": chunk_text,
                        "source": os.path.basename(filepath)})
    return chunks


def load_documents(folder: str) -> list[dict]:
    """Load all PDF and TXT files from a folder."""
    all_chunks = []
    for filename in os.listdir(folder):
        path = os.path.join(folder, filename)
        if filename.lower().endswith(".pdf"):
            console.print(f"  [cyan]Parsing PDF:[/cyan] {filename}")
            all_chunks.extend(parse_pdf(path))
        elif filename.lower().endswith(".txt"):
            console.print(f"  [cyan]Parsing TXT:[/cyan] {filename}")
            all_chunks.extend(parse_txt(path))
    return all_chunks
