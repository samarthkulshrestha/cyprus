import argparse
import json
from cyprus.data.scrapers.huggingface import scrape_huggingface_model_card
from cyprus.data.scrapers.paperswithcode import scrape_paperswithcode_model
from cyprus.data.scrapers.model_cards import parse_model_card_md
from cyprus.data.processors.compute_estimator import estimate_compute
from cyprus.data.processors.risk_scorer import score_risk

def main():
    """
    CLI tool to scrape model data from various sources, process it,
    and update the model registry.
    """
    parser = argparse.ArgumentParser(description="Scrape model data and update the registry.")
    parser.add_argument("source", choices=['huggingface', 'pwc', 'local_card'], help="The data source to use.")
    parser.add_argument("identifier", type=str, help="The model identifier (e.g., 'meta-llama/Meta-Llama-3-8B' for huggingface, 'gemma' for pwc, or a file path for local_card).")
    parser.add_argument("--registry-path", type=str, default="data/models/registry.json", help="Path to the model registry JSON file.")
    args = parser.parse_args()

    print(f"Fetching data for '{args.identifier}' from source '{args.source}'...")

    scraped_data = None
    if args.source == 'huggingface':
        scraped_data = scrape_huggingface_model_card(args.identifier)
    elif args.source == 'pwc':
        scraped_data = scrape_paperswithcode_model(args.identifier)
    elif args.source == 'local_card':
        scraped_data = parse_model_card_md(args.identifier)

    if not scraped_data:
        print("Failed to fetch or parse data. Exiting.")
        return

    print("Processing scraped data...")
    # Add estimated compute and risk score
    scraped_data["compute_flops"] = estimate_compute(scraped_data)
    scraped_data["risk_score"] = score_risk(scraped_data)
    # Assume not red-teamed by default when scraping
    scraped_data["red_teamed"] = False

    # Sanitize model_id for JSON and Prolog
    if args.source == 'huggingface':
        scraped_data["model_id"] = args.identifier.replace('/', '_')

    print(f"Updating registry at '{args.registry_path}'...")
    try:
        with open(args.registry_path, 'r+') as f:
            registry_data = json.load(f)
            # Avoid duplicates by model_id
            registry_data = [m for m in registry_data if m.get("model_id") != scraped_data["model_id"]]
            registry_data.append(scraped_data)
            f.seek(0)
            json.dump(registry_data, f, indent=2)
            f.truncate()
        print("Registry updated successfully.")
    except FileNotFoundError:
        with open(args.registry_path, 'w') as f:
            json.dump([scraped_data], f, indent=2)
        print(f"Created new registry at '{args.registry_path}'.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {args.registry_path}. Check the file for corruption.")

if __name__ == "__main__":
    main()
