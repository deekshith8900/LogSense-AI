import os
import logging
import argparse
from logsense_ai.src.ingestion.ingestor import LogIngestor
from logsense_ai.src.processing.processor import LogProcessor
from logsense_ai.src.models.vector_store import LogVectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline(log_file, index_path):
    """
    Runs the full ingestion pipeline: Load -> Process -> Embed -> Store.
    """
    logger.info("Starting Ingestion Pipeline...")
    
    # 1. Ingestion
    ingestor = LogIngestor()
    logs = ingestor.load_file(log_file)
    if not logs:
        logger.warning("No logs found. Exiting pipeline.")
        return
    logger.info(f"Loaded {len(logs)} log entries.")

    # 2. Processing
    processor = LogProcessor()
    # Normalize first to get full text, then chunk. 
    # NOTE: processing/processor.py process_logs does both.
    chunks = processor.process_logs(logs)
    logger.info(f"Generated {len(chunks)} text chunks.")
    
    # 3. Vector Storage
    vector_store = LogVectorStore(index_path=index_path)
    
    # Check for OpenAI Key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found. Cannot generate embeddings.")
        return

    vector_store.add_texts(chunks)
    vector_store.save()
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LogSense-AI Ingestion Pipeline")
    parser.add_argument("--log_file", type=str, default="logsense_ai/data/raw/app.log", help="Path to raw log file")
    parser.add_argument("--index_path", type=str, default="logsense_ai/data/processed/faiss_index", help="Path to save FAISS index")
    
    args = parser.parse_args()
    
    # Ensure processed directory exists
    os.makedirs(os.path.dirname(args.index_path), exist_ok=True)
    
    run_pipeline(args.log_file, args.index_path)
