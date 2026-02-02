import time
import random
import json
import logging
import os
from faker import Faker
from datetime import datetime

# Configure Local Logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data/raw")
os.makedirs(DATA_DIR, exist_ok=True)
LOG_FILE = os.path.join(DATA_DIR, "app.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(message)s',
)

fake = Faker()

SERVICES = [
    "checkout-service",
    "auth-service",
    "payment-gateway",
    "inventory-db",
    "recommendation-engine"
]

LOG_LEVELS = ["INFO", "WARN", "ERROR"]

def generate_log_entry():
    service = random.choice(SERVICES)
    timestamp = datetime.now().isoformat()
    level = random.choices(LOG_LEVELS, weights=[70, 20, 10], k=1)[0]
    
    correlation_id = fake.uuid4()
    
    log_data = {
        "timestamp": timestamp,
        "service": service,
        "level": level,
        "correlation_id": correlation_id,
        "message": ""
    }

    if level == "INFO":
        if service == "checkout-service":
            log_data["message"] = f"Cart updated for user {fake.user_name()}"
        elif service == "auth-service":
            log_data["message"] = f"User login successful: {fake.email()}"
        elif service == "payment-gateway":
            log_data["message"] = f"Payment processed transaction_id={fake.uuid4()}"
        else:
            log_data["message"] = "Health check OK"

    elif level == "WARN":
        log_data["message"] = f"High latency detected: {random.randint(200, 2000)}ms"

    elif level == "ERROR":
        if service == "payment-gateway":
            log_data["message"] = "Payment declined: Gateway Timeout (504)"
        elif service == "inventory-db":
            log_data["message"] = "ConnectionRefusedError: max connections reached"
            log_data["stack_trace"] = "Traceback (most recent call last)...\n  File 'db.py', line 42, in connect"
        else:
            log_data["message"] = f"Exception: {fake.sentence()}"

    return json.dumps(log_data)

if __name__ == "__main__":
    print(f"Starting log generator. Writing to {LOG_FILE}...")
    print("Press Ctrl+C to stop.")
    try:
        while True:
            log_entry = generate_log_entry()
            logging.info(log_entry)
            print(log_entry)
            time.sleep(random.uniform(0.1, 1.0))
    except KeyboardInterrupt:
        print("\nLog generation stopped.")
