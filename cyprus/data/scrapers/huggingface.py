import requests
import re
from typing import Dict, Any, Optional, List
import yaml

def parse_huggingface_model_card(model_id: str) -> Optional[Dict[str, Any]]:
    """
    Scrapes and parses the model card (README.md) for a given model ID on Hugging Face.
    It extracts structured data from the YAML front matter and falls back to
    regex parsing for key details in the Markdown body.

    Args:
        model_id: The model identifier (e.g., "meta-llama/Meta-Llama-3-8B").

    Returns:
        A dictionary with scraped and parsed data, or None if the page cannot be fetched.
    """
    # Construct the URL to the raw README.md file
    url = f"https://huggingface.co/{model_id}/raw/main/README.md"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        card_content = response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Hugging Face model card for {model_id}: {e}")
        return None

    # --- Parse YAML Front Matter ---
    parsed_data = {}
    try:
        # The YAML block is typically at the top, enclosed by '---'
        yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', card_content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            card_yaml = yaml.safe_load(yaml_content)
            
            # Extract key fields from YAML
            parsed_data['license'] = card_yaml.get('license', 'unknown')
            parsed_data['tags'] = card_yaml.get('tags', [])
            # The model card format can be inconsistent, so we check multiple keys
            if 'model-index' in card_yaml:
                for item in card_yaml['model-index']:
                    if item.get('name', '').lower() == model_id.split('/')[-1].lower():
                        parsed_data['results'] = item.get('results', [])
            
    except yaml.YAMLError as e:
        print(f"Error parsing YAML for {model_id}: {e}")

    # --- Fallback/Regex Parsing for other details ---
    
    # Organization and Model Name
    org_and_model = model_id.split('/')
    parsed_data['organization'] = org_and_model[0] if len(org_and_model) > 1 else "unknown"
    
    # Infer capabilities from tags
    if 'tags' in parsed_data:
        caps = [tag for tag in parsed_data['tags'] if tag in ['text-generation', 'code', 'multimodal', 'reasoning']]
        parsed_data['capabilities'] = caps

    # A real implementation would have more sophisticated regex for every field.
    # For this example, we'll focus on what we can get from YAML.
    
    return {
        "model_id": model_id.replace('/', '_'),
        "organization": parsed_data.get('organization'),
        "source": "huggingface",
        "license": parsed_data.get('license'),
        "tags": parsed_data.get('tags', []),
        "capabilities": parsed_data.get('capabilities', []),
        "benchmark_results": parsed_data.get('results', [])
    }