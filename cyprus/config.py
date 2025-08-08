"""
Centralized configuration for the Cyprus application.
"""

import os

# --- Project Root ---
# Assumes the script is run from the root of the project.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# --- Policy Files ---
# Default policy files to be loaded by the engine.
DEFAULT_POLICY_FILES = [
    os.path.join(PROJECT_ROOT, "cyprus/policies/eu_ai_act.pl"),
    os.path.join(PROJECT_ROOT, "cyprus/policies/governance_rules.pl"),
]

# --- Model Registry ---
# Path to the JSON file containing the model registry.
DEFAULT_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "data/models/registry.json")
