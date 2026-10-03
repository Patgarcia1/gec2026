import csv
import re
from pathlib import Path

def parse_val(raw):
    if raw is None:
        return None
    val = str(raw).strip()
    if val in ("", "NA", "na", ".", "null", "NULL", "None", "nan", "NaN"):
        return None
    try:
        if "." not in val and "e" not in val.lower():
            return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        return val

def _readme_line(line):
    """Remove presentation quotes and numbered field prefixes."""
    return re.sub(r"^\d+\.\s*", "", line.strip().strip('"').strip())


def _readme_field(lines, *labels):
    """Read an inline field or the paragraph immediately beneath its label."""
    for index, line in enumerate(lines):
        label, separator, value = line.partition(":")
        if separator and label.strip().casefold() in labels:
            if value.strip():
                return value.strip()
            paragraph = []
            for following in lines[index + 1:]:
                if not following:
                    if paragraph:
                        break
                    continue
                if ":" in following or following.isupper() or following == "-":
                    break
                paragraph.append(following)
            return " ".join(paragraph)
    return ""


def get_meta(key):
    """Extract metadata from the dataset's README on every call.
    """
    sources = {
        "biogeochem": ("Pecsi_Hawaii_Biogeochem_PigDecomposition_ReadMe.txt",
                       "Pecsi_Hawaii_Biogeochem_PigDecomposition.csv"),
        "biolog": ("Pecsi_Hawaii_Biolog_PigDecomposition_ReadMe.txt",
                   "Pecsi_Hawaii_Biolog_PigDecomposition.csv"),
        "cow": ("100A_README.txt", "CowEnergyBalanceData-1.csv"),
    }

    if key not in sources:
        return {}
    #get absolute directory path of the current file
    directory = Path(__file__).resolve().parent
    
    readme_name, csv_name = sources[key]
    # Some cattle Notes lines contain damaged characters; preserve the rest.
    text = (directory / readme_name).read_text(encoding="utf-8-sig", errors="replace")

    # Process each line in the readme. 
    lines = [_readme_line(line) for line in text.splitlines()]
    meta = {
        "title": _readme_field(lines, "title of dataset"),
        "authors": [],
        "doi": _readme_field(lines, "dataset doi", "doi"),
        "license": _readme_field(lines, "licenses/restrictions placed on the data",
                                 "licenses/restrictions placed on the dataset"),
        "dates": _readme_field(lines, "date of data collection"),
        "location": _readme_field(lines, "geographic location of data collection",
                                  "geographic location of the data collection"),
        "description": _readme_field(lines, "description of the dataset"),
        "variables": {},
    }
    if not meta["description"]:
        meta["description"] = _readme_field(
            lines, "description of methods used for collection/generation of data",
            "environmental/experimental conditions")

    variable_start = next((i for i, line in enumerate(lines)
                           if line.casefold().startswith("variable list:")), len(lines))
    # Name fields before the variable list describe the authors/contacts.
    for line in lines[:variable_start]:
        label, separator, name = line.partition(":")
        if separator and label.strip().casefold() == "name" and name.strip():
            if name.strip() not in meta["authors"]:
                meta["authors"].append(name.strip())

    current_variable = None
    for line in lines[variable_start + 1:]:
        if not line:
            continue
        lower = line.casefold()
        if (lower.startswith(("missing data codes:", "specialized formats",
                              "methodological information"))):
            break
        label, separator, value = line.partition(":")
        label = label.strip().casefold()
        if separator and label == "name":
            current_variable = value.strip()
            meta["variables"][current_variable] = {"description": "", "unit": ""}
        elif separator and current_variable and label in ("description", "notes", "value labels"):
            info = meta["variables"][current_variable]
            value = value.strip()
            if label == "description":
                info["description"] = value
                unit = re.search(r"\bin\s+((?:kg|g|mg|Mcal|kcal|cm|mm|mL|L)(?:/[A-Za-z]+)?)$", value)
                if unit:
                    info["unit"] = unit.group(1)
                elif "percentage" in value.casefold():
                    info["unit"] = "%"
            elif value:
                info[label.replace(" ", "_")] = value
        elif not separator and "," in line:
            # Split only the first and last commas: descriptions may contain commas.
            name, definition = line.split(",", 1)
            description, comma, unit = definition.rpartition(",")
            if not comma:
                description, unit = definition, ""
            meta["variables"][name.strip()] = {
                "description": description.strip(), "unit": unit.strip()
            }

    # README capitalization differs from CSV headers, and the cattle README
    # spells BWsmth_chg as BWsmooth_chg. Keep descriptions attached to real columns.
    csv_path = directory / csv_name
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as source:
            headers = next(csv.reader(source), [])
        header_names = {name.casefold(): name for name in headers}
        aliases = {"bwsmooth_chg": "bwsmth_chg"}
        meta["variables"] = {
            header_names.get(aliases.get(name.casefold(), name.casefold()), name): info
            for name, info in meta["variables"].items()
        }
    return meta
