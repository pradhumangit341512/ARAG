#!/bin/bash
echo "============================================"
echo "   Agentic RAG - Mac/Linux Setup Script"
echo "============================================"
echo ""

echo "[Step 1] Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo ""
echo "[Step 2] Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "[Step 3] Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env from template."
    echo "Please open .env and add your API keys before running!"
else
    echo ".env already exists."
fi

echo ""
echo "============================================"
echo "   Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENAI_API_KEY"
echo "  2. Start Neo4j (see README.md)"
echo "  3. Run: python main.py"
echo ""
