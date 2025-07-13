import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

def scrape_huggingface_model_card(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Scrapes the model card page for a given model ID on Hugging Face.

    Args:
        model_id: The model identifier (e.g., "gpt2" or "meta-llama/Meta-Llama-3-8B").

    Returns:
        A dictionary with scraped data, or None if the page cannot be fetched.
    """
    url = f"https://huggingface.co/{model_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hugging Face page for {model_id}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # For this example, we'll just extract the model ID and organization
    # A real implementation would parse the model card YAML for more details

    org_and_model = model_id.split('/')
    organization = org_and_model[0] if len(org_and_model) > 1 else "N/A"

    return {
        "model_id": model_id.replace('/', '_'), # Sanitize for Prolog atom
        "organization": organization,
        "source": "huggingface"
    }
