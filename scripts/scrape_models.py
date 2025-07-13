import argparse
import json
from cyprus.data.scrapers.huggingface import parse_huggingface_model_card
from cyprus.data.processors.compute_estimator import estimate_compute
from cyprus.data.processors.risk_scorer import score_risk

def main():
    """
    CLI tool to scrape rich model data from Hugging Face, process it,
    and create a comprehensive entry in the model registry.
    """
    parser = argparse.ArgumentParser(description="Scrape Hugging Face model data and update the registry.")
    parser.add_argument("model_id", type=str, help="The Hugging Face model ID (e.g., 'meta-llama/Meta-Llama-3-8B').")
    parser.add_argument("--registry-path", type=str, default="data/models/registry.json", help="Path to the model registry JSON file.")
    args = parser.parse_args()

    print(f"Fetching and parsing model card for '{args.model_id}'...")
    scraped_data = parse_huggingface_model_card(args.model_id)

    if not scraped_data:
        print("Failed to fetch or parse data. Exiting.")
        return

    print("Processing scraped data to generate governance attributes...")
    
    # Use new processors to generate core governance scores
    compute_flops = estimate_compute(scraped_data)
    risk_score = score_risk(scraped_data)

    # --- Assemble the full registry entry ---
    # This structure matches the new comprehensive format.
    new_entry = {
        "model_id": scraped_data['model_id'],
        "organization": scraped_data['organization'],
        "compute_flops": compute_flops,
        "risk_score": round(risk_score, 2),
        "risk_confidence": 0.85, # Default confidence for now
        "deployment_region": ["us", "eu"], # Default
        "alignment_methodology": ["rlhf"], # Default
        "capabilities": scraped_data.get('capabilities', []),
        "red_teaming_status": "pending", # Default
        "governance_facts": {
            "training_data": {
                "data_source": "web_crawl", # Placeholder
                "data_size": "unknown",
                "data_date_range": "unknown",
                "data_quality_score": 0.8 # Placeholder
            },
            "bias_assessment": {
                "test_date": "unknown",
                "bias_metrics": "unknown",
                "affected_groups": [],
                "mitigation_status": "pending"
            },
            "performance_metrics": {
                "accuracy": 0.0, "precision": 0.0, "recall": 0.0, "f1_score": 0.0, "evaluation_date": "unknown"
            },
            "security_measures": {
                "encryption_at_rest": "unknown", "encryption_in_transit": "unknown", "access_controls": "unknown"
            }
        }
    }

    print(f"Updating registry at '{args.registry_path}'...")
    try:
        with open(args.registry_path, 'r+') as f:
            registry_data = json.load(f)
            # Remove old entry if it exists
            registry_data = [m for m in registry_data if m.get("model_id") != new_entry["model_id"]]
            registry_data.append(new_entry)
            f.seek(0)
            json.dump(registry_data, f, indent=2)
            f.truncate()
        print("Registry updated successfully.")
    except FileNotFoundError:
        with open(args.registry_path, 'w') as f:
            json.dump([new_entry], f, indent=2)
        print(f"Created new registry at '{args.registry_path}'.")

if __name__ == "__main__":
    main()
