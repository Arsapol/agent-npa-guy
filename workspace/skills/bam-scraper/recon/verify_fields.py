"""Verify all API fields are captured in Pydantic models."""
import json
import sys

sys.path.insert(0, "../scripts")
from models import BamAssetDetail, BamAssetSearch


def check_coverage(api_keys: set[str], model_cls, model_name: str) -> list[str]:
    """Check which API keys are NOT captured by the model."""
    # Get all field names and aliases
    model_fields = set()
    for name, field in model_cls.model_fields.items():
        model_fields.add(name)
        if field.alias:
            model_fields.add(field.alias)

    missing = sorted(api_keys - model_fields - {"raw_json"})
    captured = sorted(api_keys & model_fields)

    print(f"\n=== {model_name} ===")
    print(f"API fields: {len(api_keys)}")
    print(f"Model captures: {len(captured)}")
    print(f"Missing: {len(missing)}")
    if missing:
        print(f"\nMISSING FIELDS:")
        for f in missing:
            print(f"  - {f}")
    return missing


# Load search response
with open("search_bangkok.json") as f:
    search_data = json.load(f)

# Collect all keys across both search items
search_keys = set()
for item in search_data["data"]:
    search_keys.update(item.keys())

search_missing = check_coverage(search_keys, BamAssetSearch, "Search Endpoint")

# Load detail responses
with open("detail_responses.json") as f:
    detail_data = json.load(f)

detail_keys = set()
for item in detail_data:
    detail_keys.update(item["data"].keys())

detail_missing = check_coverage(detail_keys, BamAssetDetail, "Detail Endpoint")

# Summary
print(f"\n=== SUMMARY ===")
total_missing = len(search_missing) + len(detail_missing)
if total_missing == 0:
    print("ALL FIELDS CAPTURED!")
else:
    print(f"{total_missing} total missing fields across both endpoints")
