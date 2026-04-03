"""
config.py - Central configuration for Agentic RAG
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM (Groq – OpenAI-compatible API) ───────────────────────
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL    = "https://api.groq.com/openai/v1"
LLM_MODEL        = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

# ── Neo4j ─────────────────────────────────────────────────────
NEO4J_URI        = os.getenv("NEO4J_URI",      "bolt://localhost:7687")
NEO4J_USERNAME   = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD   = os.getenv("NEO4J_PASSWORD", "password")

# ── Search ────────────────────────────────────────────────────
SERPER_API_KEY   = os.getenv("SERPER_API_KEY", "")

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR       = os.path.join(BASE_DIR, "output")
SAMPLE_DOCS_DIR  = os.path.join(BASE_DIR, "sample_docs")

# ── Research Synthesizer ──────────────────────────────────────
MAX_PAPERS            = 5       # How many papers to download & analyze
ARXIV_SEARCH_RESULTS  = 10      # Candidate papers from ArXiv
MAX_PDF_PAGES         = 20      # Max pages to read per paper
