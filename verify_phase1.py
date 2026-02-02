import threading
import time
import os
from logsense_ai.src.ingestion.ingestor import LogIngestor
import subprocess
import sys

# Define paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(PROJECT_ROOT, "logsense_ai/data/raw/app.log")

def run_generator():
    """Runs the log generator in a subprocess for 10 seconds."""
    print("Starting Log Generator...")
    # Ensure directory exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    # Run the generator script
    proc = subprocess.Popen([sys.executable, "logsense_ai/generate_logs.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    proc.terminate()
    print("Log Generator stopped.")

def verify_ingestion_static():
    print("\nVerifying Static Ingestion...")
    ingestor = LogIngestor()
    logs = ingestor.load_file(LOG_FILE)
    print(f"Loaded {len(logs)} logs from {LOG_FILE}")
    if len(logs) > 0:
        print("Sample Log:", logs[0])
    else:
        print("ALERT: No logs found!")

def verify_ingestion_stream():
    print("\nVerifying Streaming Ingestion (monitoring for 5 seconds)...")
    ingestor = LogIngestor()
    
    # Create a temporary file for streaming test
    stream_file = os.path.join(PROJECT_ROOT, "logsense_ai/data/raw/stream_test.log")
    with open(stream_file, 'w') as f:
        f.write("")

    # Start a writer thread
    def writer():
        time.sleep(1)
        with open(stream_file, 'a') as f:
            f.write('{"message": "Stream Test 1"}\n')
            f.flush()
        time.sleep(1)
        with open(stream_file, 'a') as f:
            f.write('{"message": "Stream Test 2"}\n')
            f.flush()

    t = threading.Thread(target=writer)
    t.start()
    
    # Monitor
    stream = ingestor.monitor_stream(stream_file, poll_interval=0.5)
    count = 0
    start_time = time.time()
    
    for log in stream:
        print(f"Stream received: {log}")
        count += 1
        if count >= 2:
            break
        if time.time() - start_time > 5:
            print("Timeout waiting for stream logs")
            break
            
    t.join()
    print(f"Stream verification completed. Received {count} logs.")

if __name__ == "__main__":
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    run_generator()
    verify_ingestion_static()
    verify_ingestion_stream()
