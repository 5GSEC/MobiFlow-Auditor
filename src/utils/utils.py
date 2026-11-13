import time
from datetime import datetime, timezone
from typing import Optional

NTP_UNIX_OFFSET = 2208988800  # seconds from 1900-01-01 to 1970-01-01

def get_time_ms():
    return round(time.time() * 1000)

def get_time_sec():
    return round(time.time())

def ntp_to_datetime(ntp_hex: str) -> Optional[datetime]:
    """NTP timestamp (hex) -> UTC datetime: 64 bits (seconds and fraction), or
    only the 32-bit seconds part (E2SM-KPM TimeStamp)."""
    try:
        digits = "".join(ntp_hex.split())
        ntp = int(digits, 16)
    except (AttributeError, TypeError, ValueError):
        return None
    if len(digits) <= 8:
        ntp <<= 32
    seconds = (ntp >> 32) - NTP_UNIX_OFFSET + (ntp & 0xFFFFFFFF) / 2 ** 32
    try:
        return datetime.fromtimestamp(seconds, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return None

def format_time(t: Optional[datetime]) -> str:
    return t.isoformat(timespec="microseconds").replace("+00:00", "Z") if t else "-"

def find_all_values(d, target_key):
    """
    Traverse a dictionary recursively to find all corresponding values given a key.

    Parameters:
        d (dict): The dictionary to traverse.
        target_key: The key to search for.

    Returns:
        A list of all corresponding values found for the target key.
    """
    # Initialize an empty list to store values
    values = []

    # Check if the dictionary is empty
    if not d:
        return values

    # Iterate through the dictionary keys
    for key, value in d.items():
        # Check if the current key matches the target key
        if key == target_key:
            # Add the value to the list
            values.append(value)

        if isinstance(value, dict):
            # If the value is another dictionary, recursively search it
            nested_values = find_all_values(value, target_key)
            if nested_values:
                # Extend the list with values found in the nested dictionary
                values.extend(nested_values)
        elif isinstance(value, list):
            # If the value is a list, search each element
            for v in value:
                nested_values = find_all_values(v, target_key)
                if nested_values:
                    # Extend the list with values found in the nested dictionary
                    values.extend(nested_values)
    return values
