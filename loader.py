import os
import json
import pandas as pd
from parse import get_meta, parse_val

def load_project(source):
    if hasattr(source, "read"):
        filename = getattr(source, "name", "dataset.json")
        raw = json.load(source)
    else:
        filename = str(source)
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            raw = json.load(f)

    if isinstance(raw, list):
        base = os.path.splitext(os.path.basename(filename))[0]
        meta_key = "biolog" if "biolog" in base.lower() else ("cow" if "cow" in base.lower() else "biogeochem")
        meta = get_meta(meta_key)
        cleaned_records = []
        for r in raw:
            if isinstance(r, dict):
                cleaned_row = {k: parse_val(v) for k, v in r.items()}
                cleaned_records.append(cleaned_row)

        all_vars = meta.get("variables", {}).copy()
        if cleaned_records:
            for k in cleaned_records[0].keys():
                if k not in all_vars:
                    all_vars[k] = {"description": k, "unit": ""}

        raw = {
            "metadata": {
                "title": meta.get("title", base),
                "authors": meta.get("authors", []),
                "doi": meta.get("doi", ""),
                "license": meta.get("license", ""),
                "dates": meta.get("dates", ""),
                "location": meta.get("location", ""),
                "description": meta.get("description", "")
            },
            "variables": all_vars,
            "datasets": {
                base: {
                    "row_count": len(cleaned_records),
                    "col_count": len(cleaned_records[0]) if cleaned_records else 0,
                    "records": cleaned_records
                }
            },
            "warnings": ["Dataset was loaded from flat record list and formatted with metadata"]
        }

    if not isinstance(raw, dict):
        raise ValueError("Invalid format: Root JSON must be an object")

    if "metadata" not in raw or "datasets" not in raw:
        raise ValueError("Malformed project JSON: Missing 'metadata' or 'datasets'")

    return raw

def get_datasets(project):
    return project.get("datasets", {})

def get_dataset_names(project):
    return list(get_datasets(project).keys())

def get_dataframe(project, dataset_name):
    datasets = get_datasets(project)
    if dataset_name not in datasets:
        return pd.DataFrame()
    records = datasets[dataset_name].get("records", [])
    df = pd.DataFrame(records)
    return df

def get_variable_details(project, column_name):
    variables = project.get("variables", {})
    var_info = variables.get(column_name, {})
    desc = var_info.get("description", "No description available")
    unit = var_info.get("unit", "")
    return desc, unit
