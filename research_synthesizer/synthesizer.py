"""
research_synthesizer/synthesizer.py
LLM-powered analysis and synthesis of multiple research papers.
"""
from utils.llm_client import chat
from rich.console import Console

console = Console()

# ── Per-paper analysis ────────────────────────────────────────────────────────

PAPER_ANALYSIS_SYSTEM = """You are an expert academic researcher.
Analyze research papers and extract structured information for a literature review."""

PAPER_ANALYSIS_PROMPT = """Analyze this research paper and provide a structured summary.

Title: {title}
Authors: {authors}
Published: {published}

Paper Content (excerpt):
\"\"\"
{content}
\"\"\"

Provide your analysis in this EXACT format:

PROBLEM_STATEMENT: [What problem does this paper solve? 2-3 sentences]
METHODOLOGY: [What approach/method did they use? 2-3 sentences]
KEY_CONTRIBUTIONS: [3-5 bullet points of main contributions]
RESULTS: [Key results and metrics. 2-3 sentences]
LIMITATIONS: [Weaknesses or limitations mentioned. 1-2 sentences]
FUTURE_WORK: [What future directions do they suggest? 1-2 sentences]
"""


def analyze_paper(paper: dict) -> dict:
    """Use LLM to extract structured analysis from one paper."""
    content = paper.get("full_text", paper.get("abstract", ""))[:4000]  # token guard
    authors = ", ".join(paper.get("authors", ["Unknown"])[:5])

    prompt = PAPER_ANALYSIS_PROMPT.format(
        title     = paper["title"],
        authors   = authors,
        published = paper.get("published", "N/A"),
        content   = content,
    )

    raw = chat(prompt, system=PAPER_ANALYSIS_SYSTEM, temperature=0.2)

    # Parse the structured response
    analysis = {}
    fields = [
        "PROBLEM_STATEMENT", "METHODOLOGY", "KEY_CONTRIBUTIONS",
        "RESULTS", "LIMITATIONS", "FUTURE_WORK",
    ]
    for field in fields:
        import re
        pattern = rf"{field}:\s*(.*?)(?={  '|'.join(fields) }:|$)"
        match   = re.search(pattern, raw, re.DOTALL | re.IGNORECASE)
        analysis[field.lower()] = match.group(1).strip() if match else ""

    paper["analysis"] = analysis
    return paper


# ── Cross-paper synthesis ─────────────────────────────────────────────────────

SYNTHESIS_SYSTEM = """You are a senior academic researcher writing a comprehensive literature review.
Write in formal academic style. Be analytical, not just descriptive.
Identify themes, agreements, disagreements, and gaps across papers."""

SYNTHESIS_PROMPT = """Write a comprehensive literature review section for the topic: "{topic}"

Based on these {n} papers:

{paper_summaries}

Structure your review as follows:

1. INTRODUCTION TO THE FIELD (3-4 sentences overview)
2. COMMON THEMES AND APPROACHES (what do most papers agree on?)
3. KEY METHODOLOGIES (what methods are commonly used?)
4. COMPARATIVE ANALYSIS (how do approaches differ? who does what better?)
5. RESEARCH GAPS (what's missing? what's unexplored?)
6. CONCLUSION AND FUTURE DIRECTIONS

Write in formal academic prose. Be specific with paper references using [Author et al., Year] style.
Aim for 600-800 words."""


def synthesize_literature_review(topic: str, papers: list[dict]) -> str:
    """Generate a cross-paper literature review."""
    summaries = []
    for i, p in enumerate(papers, 1):
        authors = p.get("authors", ["Unknown"])
        author_short = authors[0].split()[-1] if authors else "Unknown"
        year    = p.get("published", "2024")[:4]
        ref     = f"[{author_short} et al., {year}]"

        analysis = p.get("analysis", {})
        summary  = (
            f"Paper {i}: {p['title']} {ref}\n"
            f"  Problem: {analysis.get('problem_statement', p.get('abstract',''))[:200]}\n"
            f"  Method: {analysis.get('methodology', '')[:150]}\n"
            f"  Results: {analysis.get('results', '')[:150]}\n"
        )
        summaries.append(summary)

    prompt = SYNTHESIS_PROMPT.format(
        topic=topic,
        n=len(papers),
        paper_summaries="\n\n".join(summaries),
    )

    return chat(prompt, system=SYNTHESIS_SYSTEM, temperature=0.4)


def run_synthesis_pipeline(topic: str, papers: list[dict]) -> list[dict]:
    """Full pipeline: analyze each paper, then synthesize."""
    console.print(f"\n[bold]📖 Analyzing {len(papers)} papers individually…[/bold]")
    for i, paper in enumerate(papers, 1):
        console.print(f"  [{i}/{len(papers)}] {paper['title'][:60]}…")
        analyze_paper(paper)

    return papers
