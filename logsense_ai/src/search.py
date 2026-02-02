import argparse
import logging
import os
from logsense_ai.src.models.rag_engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(message)s') # Keep clean output
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="LogSense-AI Semantic Search")
    parser.add_argument("query", type=str, help="Natural language query (e.g., 'Why did payment fail?')")
    parser.add_argument("--k", type=int, default=3, help="Number of log chunks to retrieve")
    parser.add_argument("--index_path", type=str, default="logsense_ai/data/processed/faiss_index", help="Path to FAISS index")
    
    args = parser.parse_args()
    
    print(f"\n--- Analyzing Incident: '{args.query}' ---\n")
    
    if not os.path.exists(args.index_path):
        print(f"Error: Index not found at {args.index_path}. Run pipeline first.")
        return

    rag = RAGEngine(index_path=args.index_path)
    
    result = rag.analyze_incident(args.query, k=args.k)
    
    print("### Root Cause Analysis:\n")
    print(result["answer"])
    print("\n" + "="*40 + "\n")
    print("### Supporting Log Evidence:\n")
    for i, log in enumerate(result["source_logs"], 1):
        print(f"--- Log Chunk {i} ---")
        print(log.strip())
        print()

if __name__ == "__main__":
    main()
