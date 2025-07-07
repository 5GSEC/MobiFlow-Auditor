import time

def get_time_ms():
    return time.time() * 1000

def get_time_sec():
    return time.time()

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
