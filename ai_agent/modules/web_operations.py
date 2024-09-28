import requests
from urllib.parse import urlparse, urljoin
from ..module import Module

def make_get_request(url: str) -> str:
    try:
        # Check if the URL has a scheme, if not, add 'https://'
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = urljoin('https://', url)

        response = requests.get(url)
        response.raise_for_status()
        return f"GET request to {url} successful. Response:\n{response.text[:500]}..."
    except requests.RequestException as e:
        return f"Error making GET request to {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error during GET request to {url}: {str(e)}"

def make_post_request(url: str, data: str) -> str:
    try:
        # Check if the URL has a scheme, if not, add 'https://'
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = urljoin('https://', url)

        # Safely evaluate the data string to a dictionary
        try:
            data_dict = eval(data)
            if not isinstance(data_dict, dict):
                raise ValueError("Data must evaluate to a dictionary")
        except:
            return f"Error: Invalid data format. Expected a dictionary-like string, got: {data}"

        response = requests.post(url, json=data_dict)
        response.raise_for_status()
        return f"POST request to {url} successful. Response:\n{response.text[:500]}..."
    except requests.RequestException as e:
        return f"Error making POST request to {url}: {str(e)}"
    except Exception as e:
        return f"Unexpected error during POST request to {url}: {str(e)}"

web_operations_module = Module("web_operations")
web_operations_module.add_function("make_get_request", make_get_request)
web_operations_module.add_function("make_post_request", make_post_request)