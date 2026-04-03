# 🤖 Agentic RAG — Advanced Data Retrieval System
### College Project | Moving beyond simple PDF search to *Reasoning* over data

---

## 📌 What This Project Does

This project contains **two AI agents**:

| Agent | Description | Technologies |
|-------|-------------|--------------|
| **🕸 GraphRAG Agent** | Builds a Knowledge Graph from technical docs and answers impact-analysis questions like *"If I change this Java module, what else breaks?"* | Neo4j, LangChain, OpenAI GPT |
| **📚 Research Synthesizer** | Autonomously searches ArXiv, downloads research papers, reads them, and writes a LaTeX literature review | ArXiv API, PyMuPDF, Serper API, LaTeX |

---

## 🗂️ Project Structure

```
agentic_rag/
├── main.py                          ← Main entry point (run this!)
├── config.py                        ← All configuration
├── requirements.txt                 ← Python dependencies
├── .env.example                     ← Copy to .env and add your keys
│
├── graph_rag/
│   ├── document_parser.py           ← PDF/TXT → text chunks
│   ├── graph_builder.py             ← LLM extracts entities & relationships
│   ├── knowledge_graph.py           ← Neo4j connection + queries
│   └── query_engine.py              ← Natural language → graph traversal → answer
│
├── research_synthesizer/
│   ├── paper_fetcher.py             ← Search ArXiv + Google Scholar, download PDFs
│   ├── pdf_reader.py                ← PyMuPDF reads papers
│   ├── synthesizer.py               ← LLM analyzes and synthesizes papers
│   └── latex_writer.py              ← Generates LaTeX literature review
│
├── utils/
│   └── llm_client.py                ← OpenAI API client
│
├── sample_docs/
│   └── spring_boot_manual.txt       ← Sample technical doc for GraphRAG demo
│
└── output/                          ← Generated files appear here
    ├── papers/                      ← Downloaded PDFs
    └── literature_review_*.tex      ← Generated LaTeX reviews
```

---

## ⚡ Quick Setup (Step-by-Step CMD Commands)

### Step 1 — Clone / Download and enter the project folder
```bash
cd agentic_rag
```

### Step 2 — Create a Python virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install all dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure your API keys
```bash
# Copy the example env file
cp .env.example .env

# Open .env in any text editor and fill in:
# OPENAI_API_KEY = your OpenAI key (get from https://platform.openai.com)
# NEO4J_PASSWORD = your Neo4j password
# SERPER_API_KEY = your Serper key (optional, for Google Scholar)
```

### Step 5 — Start Neo4j (for GraphRAG agent)
```bash
# Option A: Docker (recommended)
docker run \
  --name neo4j-agentic \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -d neo4j:latest

# Option B: Neo4j Desktop — download from https://neo4j.com/download/

# Option C: Neo4j AuraDB (free cloud) — https://neo4j.com/cloud/aura-graph-database/
```

### Step 6 — Run the project!
```bash
python main.py
```

---

## 🎮 How to Use

### Agent 1 — GraphRAG (Technical Documentation)
1. Select **option 1** from the menu
2. The agent loads `sample_docs/spring_boot_manual.txt`
3. It builds a Knowledge Graph in Neo4j (LLM extracts entities + relationships)
4. Ask questions like:
   - *"If I change UserAuthModule, what is affected?"*
   - *"What modules depend on DatabaseConnectionPool?"*
   - *"What does TokenService call?"*
   - *"What uses RedisCacheService?"*

**You can add your own docs** — just drop `.pdf` or `.txt` files into `sample_docs/`

### Agent 2 — Research Paper Synthesizer
1. Select **option 2** from the menu
2. Enter a research topic, e.g.:
   - `Retrieval Augmented Generation 2024`
   - `Transformer Architecture advancements`
   - `Quantum Computing algorithms`
3. The agent searches ArXiv, downloads top 5 papers, reads them
4. Generates a LaTeX `.tex` file in `output/`
5. To compile to PDF:
   ```bash
   cd output
   pdflatex literature_review_*.tex
   ```
   Or upload the `.tex` file to **[Overleaf](https://www.overleaf.com)** (free online LaTeX editor)

---

## 🔑 Getting Free API Keys

| Service | Where to Get | Free Tier |
|---------|-------------|-----------|
| **OpenAI** | https://platform.openai.com/api-keys | $5 free credit |
| **Serper** | https://serper.dev | 2,500 searches/month FREE |
| **Neo4j AuraDB** | https://neo4j.com/cloud/aura-graph-database/ | Free instance |
| **ArXiv** | No key needed! | Unlimited |

---

## 🏗️ Architecture Diagram

```
                    ┌─────────────────────────────────┐
                    │         main.py (CLI)           │
                    └──────────┬──────────────┬───────┘
                               │              │
              ┌────────────────┘              └─────────────────┐
              ▼                                                  ▼
   ┌──────────────────────┐                      ┌──────────────────────────┐
   │   AGENT 1: GraphRAG  │                      │  AGENT 2: Research       │
   │                      │                      │  Synthesizer             │
   │  document_parser.py  │                      │                          │
   │     ↓ text chunks    │                      │  paper_fetcher.py        │
   │  graph_builder.py    │                      │    ↓ ArXiv + Serper      │
   │     ↓ LLM extracts   │                      │  pdf_reader.py           │
   │     entities/rels    │                      │    ↓ PyMuPDF             │
   │  knowledge_graph.py  │                      │  synthesizer.py          │
   │     ↓ Neo4j store    │                      │    ↓ LLM analysis        │
   │  query_engine.py     │                      │  latex_writer.py         │
   │     ↓ NL → Cypher    │                      │    ↓ .tex file           │
   │     ↓ LLM answer     │                      └──────────────────────────┘
   └──────────────────────┘
              │                                              │
              ▼                                              ▼
         [Neo4j DB]                                    [output/*.tex]
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| `OPENAI_API_KEY not set` | Edit `.env` file and add your key |
| `Neo4j connection failed` | Start Neo4j with Docker (Step 5) |
| `No papers found` | Check internet connection; ArXiv is free |
| `pip install fails` | Use `pip install -r requirements.txt --upgrade` |
| LaTeX won't compile | Upload `.tex` to Overleaf.com instead |

---

## 📚 Technologies Used

- **Python 3.10+**
- **OpenAI GPT-4o-mini** — LLM for reasoning and extraction
- **Neo4j** — Graph database for Knowledge Graph
- **LangChain** — Orchestration framework
- **ArXiv API** — Free research paper search
- **PyMuPDF** — Fast PDF text extraction
- **Serper API** — Google Scholar search
- **Jinja2** — LaTeX template rendering
- **Rich** — Beautiful terminal output

---

*Agentic RAG — College Project*
# ARAG
