import os
from logsense_ai.src.models.rag_engine import RAGEngine

def verify_phase3():
    print("\nVerifying Phase 3: RAG & Semantic Search...")
    
    index_path = "logsense_ai/data/processed/faiss_index"
    
    if not os.path.exists(index_path):
        print("ERROR: FAISS index missing. Cannot verify Search.")
        return

    print("Initializing RAG Engine...")
    rag = RAGEngine(index_path=index_path)
    
    query = "payment error"
    print(f"\nTesting Search (Query: '{query}')...")
    
    # 1. Test Retrieval
    logs = rag.search(query, k=1)
    if logs:
        print(f"SUCCESS: Retrieved {len(logs)} log chunk.")
        print(f"Preview: {logs[0][:100]}...")
    else:
        print("WARNING: No logs retrieved (Index might be empty or query mismatch).")

    # 2. Test LLM Analysis (Requires Key)
    if os.getenv("OPENAI_API_KEY"):
        print("\nTesting LLM Analysis...")
        result = rag.analyze_incident(query, k=1)
        print("SUCCESS: Analysis generated.")
        print(f"Answer: {result['answer'][:100]}...")
    else:
        print("\nSKIPPING LLM Analysis (No API Key).")

if __name__ == "__main__":
    verify_phase3()
