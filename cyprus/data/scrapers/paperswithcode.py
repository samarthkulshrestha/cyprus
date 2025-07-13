import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

def scrape_paperswithcode_model(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Scrapes a model's page on Papers with Code.
    Note: This is a simplified example. The actual site structure is complex.

    Args:
        model_name: The name of the model as it appears in the URL
                    (e.g., "gemma" for paperswithcode.com/model/gemma).

    Returns:
        A dictionary with scraped data, or None if fetching fails.
    """
    # The URL format is typically paperswithcode.com/model/{model-name}
    url = f"https://paperswithcode.com/model/{model_name}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Papers with Code page for {model_name}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # For this example, we'll extract the title as the model_id
    # and make a placeholder for the organization.
    title_element = soup.find("h1")
    title = title_element.get_text(strip=True) if title_element else model_name

    return {
        "model_id": title.lower().replace(' ', '_'),
        "organization": "unknown", # This info is not always clear on the site
        "source": "paperswithcode"
    }
