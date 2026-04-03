"""
research_synthesizer/pdf_reader.py
Extract and clean text from downloaded research PDFs.
"""
import fitz   # PyMuPDF
import config
from rich.console import Console

console = Console()


def extract_text_from_pdf(filepath: str, max_pages: int | None = None) -> str:
    """Extract clean text from a PDF file."""
    if filepath is None or not __import__("os").path.exists(filepath):
        return ""

    limit = max_pages or config.MAX_PDF_PAGES
    try:
        doc = fitz.open(filepath)
        pages_text = []
        for i, page in enumerate(doc):
            if i >= limit:
                break
            text = page.get_text("text")
            # Basic cleanup
            text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            pages_text.append(text)
        doc.close()
        return "\n\n".join(pages_text)
    except Exception as e:
        console.print(f"  [red]PDF read error:[/red] {e}")
        return ""


def extract_sections(text: str) -> dict:
    """
    Heuristically split a research paper into standard sections.
    Returns a dict: {section_name: text}
    """
    import re
    section_headers = [
        "abstract", "introduction", "related work", "background",
        "methodology", "method", "approach", "experiments", "results",
        "discussion", "conclusion", "future work", "references",
    ]
    pattern = re.compile(
        r"(?i)(?:^|\n)\s*(\d+\.?\s*)?(" + "|".join(section_headers) + r")\s*\n",
        re.MULTILINE,
    )
    sections: dict[str, str] = {}
    matches   = list(pattern.finditer(text))

    if not matches:
        return {"full_text": text}

    for i, match in enumerate(matches):
        name  = match.group(2).strip().lower()
        start = match.end()
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip()

    return sections


def read_papers(papers: list[dict]) -> list[dict]:
    """
    Read all downloaded papers and attach their extracted text.
    Returns the enriched papers list.
    """
    for paper in papers:
        pdf_path = paper.get("local_pdf")
        if pdf_path:
            console.print(f"  [cyan]Reading:[/cyan] {paper['title'][:60]}…")
            raw_text  = extract_text_from_pdf(pdf_path)
            paper["full_text"] = raw_text
            paper["sections"]  = extract_sections(raw_text)
            paper["word_count"] = len(raw_text.split())
        else:
            paper["full_text"] = paper.get("abstract", "")
            paper["sections"]  = {"abstract": paper.get("abstract", "")}
            paper["word_count"] = 0
    return papers
