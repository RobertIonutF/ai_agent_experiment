import requests
from bs4 import BeautifulSoup
from ..module import Module

def google_search(query: str, num_results: int = 5) -> str:
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('div', class_='g')
        
        results = []
        for i, result in enumerate(search_results[:num_results], 1):
            title_element = result.find('h3')
            link_element = result.find('a')
            
            if title_element and link_element:
                title = title_element.text
                link = link_element.get('href')
                if link.startswith('/url?q='):
                    link = link.split('/url?q=')[1].split('&')[0]
                results.append(f"{i}. {title}\n   {link}\n")
            
            if len(results) >= num_results:
                break

        if not results:
            return "No search results found."
        
        return "\n".join(results)
    except requests.RequestException as e:
        return f"Error performing Google search: {str(e)}"
    except Exception as e:
        return f"Unexpected error during Google search: {str(e)}"

google_search_module = Module("google_search")
google_search_module.add_function("google_search", google_search)