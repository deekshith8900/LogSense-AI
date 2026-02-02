import json
import logging
import os
import time

class LogIngestor:
    """
    Handles ingestion of logs from files and simulated streams.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def load_file(self, filepath):
        """
        Reads a static log file and returns a list of log entries (dicts).
        Supports JSON format.
        """
        logs = []
        if not os.path.exists(filepath):
            self.logger.error(f"File not found: {filepath}")
            return logs
        
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            log_entry = json.loads(line)
                            logs.append(log_entry)
                        except json.JSONDecodeError:
                            self.logger.warning(f"Skipping malformed line: {line.strip()}")
        except Exception as e:
            self.logger.error(f"Error reading file {filepath}: {e}")
            
        return logs

    def monitor_stream(self, filepath, poll_interval=1.0):
        """
        Generator that yields new log lines as they are written to the file.
        Simulates 'tail -f'.
        """
        if not os.path.exists(filepath):
            self.logger.error(f"File not found: {filepath}")
            return

        try:
            with open(filepath, 'r') as f:
                # Move to the end of the file
                f.seek(0, os.SEEK_END)
                
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(poll_interval)
                        continue
                    
                    if line.strip():
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            pass # Skip malformed in stream
        except Exception as e:
            self.logger.error(f"Error monitoring stream {filepath}: {e}")
