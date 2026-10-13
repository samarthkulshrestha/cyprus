from pathlib import Path

import yaml

from cyprus.registry.schema import ModelEntry


def load_models(path: Path) -> list[ModelEntry]:
    """
    Load and validate model data from a file or directory.

    Args:
        path: Path to a single YAML/JSON file, or a directory of model files.
              If directory, loads all .yaml and .json files recursively.

    Returns:
        List of validated ModelEntry objects.

    Raises:
        FileNotFoundError: If path doesn't exist
        pydantic.ValidationError: If any model fails schema validation
    """
    if path.is_file():
        return _load_file(path)
    elif path.is_dir():
        models = []
        for ext in ("*.yaml", "*.yml", "*.json"):
            for f in sorted(path.rglob(ext)):
                models.extend(_load_file(f))
        return models
    else:
        raise FileNotFoundError(f"Path not found: {path}")


def _load_file(path: Path) -> list[ModelEntry]:
    """
    Load models from a single file.

    Supports two formats:
    1. Single model: YAML/JSON object with model_id at top level
    2. Multiple models: YAML/JSON with a top-level "models" list
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    if isinstance(data, dict) and "models" in data:
        return [ModelEntry(**m) for m in data["models"]]
    elif isinstance(data, dict) and "model_id" in data:
        return [ModelEntry(**data)]
    elif isinstance(data, list):
        return [ModelEntry(**m) for m in data]
    else:
        raise ValueError(
            f"Unrecognized format in {path}. Expected model object, list, or {{models: [...]}}."
        )
