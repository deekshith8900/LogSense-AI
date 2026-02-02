import json
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LogProcessor:
    """
    Handles preprocessing of raw log entries: normalization, cleaning, and chunking.
    """
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.logger = logging.getLogger(__name__)

    def normalize(self, log_entry):
        """
        Converts a raw dictionary log entry into a structured text format suitable for embedding.
        Handles stack trace truncation if necessary.
        """
        if isinstance(log_entry, str):
            try:
                log_entry = json.loads(log_entry)
            except json.JSONDecodeError:
                # Treat as raw string log
                return f"RAW LOG: {log_entry}"
        
        timestamp = log_entry.get("timestamp", "UNKNOWN_TIME")
        service = log_entry.get("service", "UNKNOWN_SERVICE")
        level = log_entry.get("level", "INFO")
        message = log_entry.get("message", "")
        stack_trace = log_entry.get("stack_trace", "")
        
        # Format: [TIMESTAMP] [SERVICE] [LEVEL]: MESSAGE
        normalized_text = f"[{timestamp}] [{service}] [{level}]: {message}"
        
        if stack_trace:
            # Append stack trace, potentially truncating if extremely large
            # (Though chunking will handle splitting, it's good to avoid unlimited noise)
            normalized_text += f"\nStack Trace:\n{stack_trace}"
            
        return normalized_text

    def chunk(self, text):
        """
        Splits text into chunks of `chunk_size` characters.
        """
        return self.text_splitter.split_text(text)
    
    def process_logs(self, logs):
        """
        Batch processes valid log dictionaries into chunked text strings.
        Returns a list of chunks.
        """
        all_chunks = []
        for log in logs:
            norm_text = self.normalize(log)
            chunks = self.chunk(norm_text)
            all_chunks.extend(chunks)
        return all_chunks
