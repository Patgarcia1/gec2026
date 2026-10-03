import os
import json
import pandas as pd

def load_project(source):
    if hasattr(source, "read"):
        raw = json.load(source)
    else:
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        with open(source, "r", encoding="utf-8") as f:
            raw = json.load(f)

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
