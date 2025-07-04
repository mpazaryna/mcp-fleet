"""
Utility functions for storage operations
"""

import random
import time
from collections.abc import Callable
from datetime import datetime


def default_id_generator() -> str:
    """Generate a default entity ID using timestamp and random number"""
    timestamp = int(time.time())
    random_part = random.randint(100000, 999999)
    return f"entity_{timestamp}_{random_part}"


def timestamp_id_generator(prefix: str = "entity") -> Callable[[], str]:
    """Create an ID generator with a custom prefix"""

    def generator() -> str:
        timestamp = int(time.time())
        random_part = random.randint(100000, 999999)
        return f"{prefix}_{timestamp}_{random_part}"

    return generator


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def safe_filename(name: str) -> str:
    """Convert a string to a safe filename"""
    import re

    # Replace any character that's not alphanumeric, dash, or underscore
    safe = re.sub(r"[^a-zA-Z0-9\-_]", "_", name)
    # Replace multiple underscores with single underscore
    safe = re.sub(r"_+", "_", safe)
    # Remove leading/trailing underscores
    return safe.strip("_")
