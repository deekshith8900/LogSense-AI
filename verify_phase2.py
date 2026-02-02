import os
import shutil
from logsense_ai.src.pipeline import run_pipeline
from logsense_ai.src.models.vector_store import LogVectorStore
from dotenv import load_dotenv

# Load env if present
load_dotenv()

def verify_phase2():
    print("\nVerifying Phase 2: Preprocessing & Vector Storage...")
    
    log_file = "logsense_ai/data/raw/app.log"
    index_path = "logsense_ai/data/processed/faiss_index"

    # Ensure log file exists (from phase 1)
    if not os.path.exists(log_file):
        print(f"ERROR: {log_file} missing. Run generate_logs.py first.")
        return

    # Run Pipeline
    print("Running Pipeline...")
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not set. Pipeline will fail to embed.")
        # Create dummy index for structure verification if needed, or just let it fail.
        # For this verification, we really want to see it try.
    
    try:
        run_pipeline(log_file, index_path)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        return

    # Check if index exists
    if os.path.exists(index_path):
        print("SUCCESS: FAISS index created.")
        
        # Try loading and searching
        if os.getenv("OPENAI_API_KEY"):
            print("Testing Similarity Search...")
            vs = LogVectorStore(index_path=index_path)
            vs.load()
            results = vs.similarity_search("payment error", k=1)
            print(f"Search Result: {results}")
    else:
        print("ERROR: FAISS index not found.")

if __name__ == "__main__":
    verify_phase2()
