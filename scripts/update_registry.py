import argparse
import json
from typing import Any

def update_field(registry_path: str, model_id: str, field: str, value: Any):
    """
    Updates a specific field for a model in the registry.
    """
    try:
        with open(registry_path, 'r+') as f:
            registry_data = json.load(f)

            model_found = False
            for model in registry_data:
                if model.get("model_id") == model_id:
                    print(f"Updating model '{model_id}': Set '{field}' to '{value}'")
                    model[field] = value
                    model_found = True
                    break

            if not model_found:
                print(f"Error: Model ID '{model_id}' not found in registry.")
                return

            # Write the updated data back to the file
            f.seek(0)
            json.dump(registry_data, f, indent=2)
            f.truncate()
            print("Registry updated successfully.")

    except FileNotFoundError:
        print(f"Error: Registry file not found at '{registry_path}'.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {registry_path}.")

def str_to_bool(val: str) -> bool:
    """Converts common string representations to boolean."""
    return val.lower() in ['true', '1', 't', 'y', 'yes']

def main():
    parser = argparse.ArgumentParser(description="Manually update a model's entry in the registry.")
    parser.add_argument("model_id", type=str, help="The ID of the model to update.")
    parser.add_argument("--set", required=True, help="The field and value to set, e.g., 'red_teamed=true' or 'risk_score=0.9'.")
    parser.add_argument("--registry", default="data/models/registry.json", help="Path to the model registry JSON file.")
    args = parser.parse_args()

    # Parse the field and value
    try:
        field, value_str = args.set.split('=', 1)
    except ValueError:
        print("Error: The --set argument must be in the format 'field=value'.")
        return

    # Attempt to convert value to bool or float if appropriate
    value: Any
    if value_str.lower() in ['true', 'false']:
        value = str_to_bool(value_str)
    else:
        try:
            value = float(value_str)
        except ValueError:
            value = value_str # Keep as string if it's not a number

    update_field(args.registry, args.model_id, field, value)

if __name__ == "__main__":
    main()
