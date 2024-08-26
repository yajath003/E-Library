# database_utils.py

from sqlalchemy.exc import OperationalError
import time

# Retry logic for database operations
def retry_database_operation(session, operation, max_retries=3, delay=0.1):
    retries = 0
    while True:
        try:
            return operation(session)
        except OperationalError as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                time.sleep(delay)
                continue
            else:
                raise
