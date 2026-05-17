#!/bin/bash
echo "Checking ChromaDB..."
python src/embedding.py

echo "Starting Wuduh..."
streamlit run src/app.py --server.port=8501 --server.address=0.0.0.0