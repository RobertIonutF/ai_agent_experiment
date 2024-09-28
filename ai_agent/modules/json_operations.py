import json
from ..module import Module

def parse_json(json_string: str) -> str:
    try:
        parsed_data = json.loads(json_string)
        return json.dumps(parsed_data, indent=2)
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {str(e)}"
    except Exception as e:
        return f"Unexpected error while parsing JSON: {str(e)}"

def get_json_value(json_string: str, key: str) -> str:
    try:
        parsed_data = json.loads(json_string)
        if key in parsed_data:
            return str(parsed_data[key])
        else:
            return f"Key '{key}' not found in JSON data"
    except json.JSONDecodeError as e:
        return f"Error parsing JSON: {str(e)}"
    except Exception as e:
        return f"Unexpected error while getting JSON value: {str(e)}"

def create_json(key_value_pairs: str) -> str:
    try:
        pairs = [pair.strip() for pair in key_value_pairs.split(',')]
        data = {}
        for pair in pairs:
            key, value = pair.split(':', 1)
            data[key.strip()] = value.strip()
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error creating JSON: {str(e)}"

def to_json(input_string: str) -> str:
    try:
        # Try to parse the input as JSON first
        json_object = json.loads(input_string)
    except json.JSONDecodeError:
        # If it's not valid JSON, try to convert it to a dictionary
        try:
            # Split the string into key-value pairs
            pairs = [pair.strip() for pair in input_string.split(',')]
            json_object = {}
            for pair in pairs:
                key, value = pair.split(':', 1)
                key = key.strip()
                value = value.strip()
                # Try to convert value to int or float if possible
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        # If it's not a number, keep it as a string
                        pass
                json_object[key] = value
        except Exception as e:
            return f"Error converting to JSON: {str(e)}"

    # Convert the object to a JSON string
    return json.dumps(json_object, indent=2)

json_operations_module = Module("json_operations")
json_operations_module.add_function("parse_json", parse_json)
json_operations_module.add_function("get_json_value", get_json_value)
json_operations_module.add_function("create_json", create_json)
json_operations_module.add_function("to_json", to_json)