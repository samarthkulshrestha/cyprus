import re
from typing import Dict, Any, Optional

def parse_model_card_md(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parses a local Markdown file that follows a simple model card format.

    Args:
        file_path: The local path to the .md model card.

    Returns:
        A dictionary with parsed data, or None if the file cannot be read.
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Model card file not found at {file_path}")
        return None

    def _extract_field(pattern):
        match = re.search(pattern, content, re.IGNORECASE)
        return match.group(1).strip() if match else "unknown"

    model_id = _extract_field(r"#\s*(.*)")
    organization = _extract_field(r"Organization:\s*(.*)")

    return {
        "model_id": model_id.lower().replace(' ', '_'),
        "organization": organization.lower(),
        "source": "local_model_card"
    }
