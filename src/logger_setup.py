import logging
import sys
from datetime import datetime
import os

class PrintToLogger:
    def __init__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        
    def write(self, text):
        # Skip empty writes
        if text.strip() == '':
            # Handle newline writes
            if '\n' in text:
                self._stdout.write(text)
            return
            
        # Parse the log level and message for the file logger
        message = text.strip()
        if '[ERROR]' in text:
            logging.error(message[message.index(']')+1:].strip())
        elif '[WARNING]' in text:
            logging.warning(message[message.index(']')+1:].strip())
        elif '[INFO]' in text:
            logging.info(message[message.index(']')+1:].strip())
        else:
            # Default to INFO for prints without level
            logging.info(message)
            
        # Write original text to console exactly as it was
        self._stdout.write(text)
        # if not text.endswith('\n'):
        #     self._stdout.write('\n')
        
    def flush(self):
        self._stdout.flush()

def setup_logging():
    # Create logs directory if needed
    logs_dir = "../logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    timestamp = datetime.now().strftime('%Y-%m-%dT_%H-%M-%S')  # Changed this line
    log_file = os.path.join(logs_dir, f"app_{timestamp}.log")
    
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler with dates - only file handler gets the formatter
    file_handler = logging.FileHandler(log_file)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                     datefmt='%Y-%m-%dT%H:%M:%S')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Redirect stdout to our custom logger
    sys.stdout = PrintToLogger()