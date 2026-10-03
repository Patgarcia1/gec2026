import os
import sys
import json
import csv
import pandas as pd

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

def get_meta(key):
    registry = {
        "biogeochem": {
            "title": "Biogeochemical evaluation of soils impacted by pig carcass decomposition in a Hawaiian tropical savanna ecosystem",
            "authors": [
                "Emily Leanna Pecsi",
                "François Guillemette",
                "Shari Forbes",
                "Hugo Germain",
                "David Carter",
                "Mélodie B Plourde",
                "Théo Devèze"
            ],
            "doi": "10.5683/SP4/UXYJGA",
            "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "dates": "2022-03-30 to 2022-04-19",
            "location": "21.290833 N, -157.804722 W",
            "description": "Biogeochemical soil measurements across decomposition phases and distances from pig carcass in Hawaiian tropical savanna ecosystem.",
            "variables": {
                "Pig": {"description": "Identifier of pig carcass in which soil was collected around", "unit": ""},
                "Phase": {"description": "Decomposition phase", "unit": ""},
                "Distance": {"description": "Distance from pig carcass", "unit": "cm"},
                "BA": {"description": "Absolute bacterial cell count", "unit": "cells/gSoil"},
                "BR": {"description": "Bacterial respiration rate", "unit": "ugC/gSoil/hour"},
                "DOC": {"description": "Dissolved organic carbon", "unit": "mgC gSoil-1"},
                "FI": {"description": "Fluorescence index", "unit": ""},
                "HIX": {"description": "Humification index", "unit": ""},
                "BIX": {"description": "Biological index", "unit": ""},
                "SR": {"description": "Spectral slope ratio", "unit": ""},
                "pC1": {"description": "Percent contribution of PARAFAC component 1 (Terrestrial humic-like)", "unit": "%"},
                "pC2": {"description": "Percent contribution of PARAFAC component 2 (Microbial humic-like)", "unit": "%"},
                "pC3": {"description": "Percent contribution of PARAFAC component 3 (Microbial protein-like)", "unit": "%"},
                "pC4": {"description": "Percent contribution of PARAFAC component 4 (Terrestrial phenol-like)", "unit": "%"}
            }
        },
        "biolog": {
            "title": "Biolog EcoPlate profiles of soil bacterial communities impacted by pig carcass decomposition in a Hawaiian tropical savanna ecosystem",
            "authors": [
                "Emily Leanna Pecsi",
                "François Guillemette",
                "Shari Forbes"
            ],
            "doi": "10.5683/SP3/DEH8FG",
            "license": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
            "dates": "2020-08-11 to 2021-09-27",
            "location": "Bécancour, Québec, Canada / Hawaii savanna",
            "description": "Biolog EcoPlate carbon substrate utilization profiles (AWCD) of soil bacterial communities impacted by pig carcass decomposition.",
            "variables": {
                "Pig": {"description": "Identifier of pig carcass in which soil was collected around", "unit": ""},
                "Distance": {"description": "Distance from pig carcass", "unit": "cm"},
                "Phase": {"description": "Decomposition phase", "unit": ""},
                "C1": {"description": "BioLog EcoPlate carbohydrate substrate (β-Methyl-D-Glucoside)", "unit": "AWCD"},
                "C2": {"description": "BioLog EcoPlate carbohydrate substrate (D-Galactonic Acid γ-Lactone)", "unit": "AWCD"},
                "AA1": {"description": "BioLog EcoPlate amino acid substrate (L-Arginine)", "unit": "AWCD"},
                "CA1": {"description": "BioLog EcoPlate carboxylic acid substrate (Pyruvic Acid Methyl Ester)", "unit": "AWCD"},
                "C3": {"description": "BioLog EcoPlate carbohydrate substrate (D-Xylose)", "unit": "AWCD"},
                "CA2": {"description": "BioLog EcoPlate carboxylic acid substrate (D-Galacturonic Acid)", "unit": "AWCD"},
                "AA2": {"description": "BioLog EcoPlate amino acid substrate (L-Asparagine)", "unit": "AWCD"},
                "P1": {"description": "BioLog EcoPlate polymer substrate (Tween 40)", "unit": "AWCD"},
                "C4": {"description": "BioLog EcoPlate carbohydrate substrate (i-Erythritol)", "unit": "AWCD"},
                "PC1": {"description": "BioLog EcoPlate phenolic substrate (2-Hydroxy Benzoic Acid)", "unit": "AWCD"},
                "AA3": {"description": "BioLog EcoPlate amino acid substrate (L-Phenylalanine)", "unit": "AWCD"},
                "P2": {"description": "BioLog EcoPlate polymer substrate (Tween 80)", "unit": "AWCD"},
                "C5": {"description": "BioLog EcoPlate carbohydrate substrate (D-Mannitol)", "unit": "AWCD"},
                "PC2": {"description": "BioLog EcoPlate phenolic substrate (4-Hydroxy Benzoic Acid)", "unit": "AWCD"},
                "AA4": {"description": "BioLog EcoPlate amino acid substrate (L-Serine)", "unit": "AWCD"},
                "P3": {"description": "BioLog EcoPlate polymer substrate (α-Cyclodextrin)", "unit": "AWCD"},
                "C6": {"description": "BioLog EcoPlate carbohydrate substrate (N-Acetyl-D-Glucosamine)", "unit": "AWCD"},
                "CA3": {"description": "BioLog EcoPlate carboxylic acid substrate (γ-Amino Butyric Acid)", "unit": "AWCD"},
                "AA5": {"description": "BioLog EcoPlate amino acid substrate (L-Threonine)", "unit": "AWCD"},
                "P4": {"description": "BioLog EcoPlate polymer substrate (Glycogen)", "unit": "AWCD"},
                "CA4": {"description": "BioLog EcoPlate carboxylic acid substrate (D-Glucosaminic Acid)", "unit": "AWCD"},
                "CA5": {"description": "BioLog EcoPlate carboxylic acid substrate (Itaconic Acid)", "unit": "AWCD"},
                "AA6": {"description": "BioLog EcoPlate amino acid substrate (α-Hydroxy-Glycyl-L-Glutaminic Acid)", "unit": "AWCD"},
                "C7": {"description": "BioLog EcoPlate carbohydrate substrate (D-Cellobiose)", "unit": "AWCD"},
                "C8": {"description": "BioLog EcoPlate carbohydrate substrate (Glucose-1-Phosphate)", "unit": "AWCD"},
                "CA6": {"description": "BioLog EcoPlate carboxylic acid substrate (α-Keto Butyric Acid)", "unit": "AWCD"},
                "A1": {"description": "BioLog EcoPlate amine substrate (Phenylethylamine)", "unit": "AWCD"},
                "C9": {"description": "BioLog EcoPlate carbohydrate substrate (α-D-Lactose)", "unit": "AWCD"},
                "C10": {"description": "BioLog EcoPlate carbohydrate substrate (D, L-α-Glycerol Phosphate)", "unit": "AWCD"},
                "CA7": {"description": "BioLog EcoPlate carboxylic acid substrate (D-Malic Acid)", "unit": "AWCD"},
                "A2": {"description": "BioLog EcoPlate amine substrate (Putrescine)", "unit": "AWCD"}
            }
        },
        "cow": {
            "title": "Daily energy flows of freestall-housed dairy cattle estimated with automated data collection",
            "authors": [
                "John Cant",
                "Patricia Kedzierski",
                "Carolina Reyes"
            ],
            "doi": "https://doi.org/10.5683/SP4/MS7XVT",
            "license": "CC BY 4.0",
            "dates": "2018-10-26 to 2018-11-22",
            "location": "Elora and Guelph, Ontario, Canada",
            "description": "Automatically recorded performance and respiratory gas exchange data from dairy cows housed in a free-stall pen.",
            "variables": {
                "CowID": {"description": "Unique cow identifier", "unit": ""},
                "date": {"description": "Date in YYYY-MM-DD of last day of data collection week", "unit": "YYYY-MM-DD"},
                "parity": {"description": "Lactation number of cow", "unit": ""},
                "DIM": {"description": "Days in milk of cow", "unit": "days"},
                "BCS": {"description": "Cow body condition score on a 5-point scale", "unit": "score"},
                "BW_raw": {"description": "Cow bodyweight", "unit": "kg"},
                "BWraw_chg": {"description": "Change in body weight", "unit": "kg/d"},
                "BW_smooth": {"description": "Smoothed cow bodyweight", "unit": "kg"},
                "BWsmth_chg": {"description": "Change in smoothed body weight", "unit": "kg/d"},
                "DMI_PMR": {"description": "Dry matter intake of partial mixed ration", "unit": "kg/d"},
                "DMI_pellet": {"description": "Dry matter intake of pellet", "unit": "kg/d"},
                "DMI": {"description": "Total dry matter intake", "unit": "kg/d"},
                "CO2_g_d": {"description": "Daily carbon dioxide production", "unit": "g/d"},
                "O2_g_d": {"description": "Daily oxygen consumption", "unit": "g/d"},
                "CH4_g_d": {"description": "Daily methane production", "unit": "g/d"},
                "milk": {"description": "Milk yield", "unit": "kg/d"},
                "milk_fat": {"description": "Milk fat percentage", "unit": "%"},
                "milk_prt": {"description": "Milk protein percentage", "unit": "%"},
                "milk_lac": {"description": "Milk lactose percentage", "unit": "%"},
                "MEI": {"description": "Metabolizable energy intake", "unit": "Mcal/d"},
                "milkE": {"description": "Milk energy output", "unit": "Mcal/d"},
                "HP_Greenfeed": {"description": "Whole-body heat production", "unit": "Mcal/d"},
                "RE": {"description": "Retained energy in body and milk", "unit": "Mcal/d"},
                "tissueE": {"description": "Tissue energy retention in body", "unit": "Mcal/d"}
            }
        }
    }
    return registry.get(key, {})

def parse_file(file_name, json_name, meta_key=None):
    if not os.path.exists(file_name):
        print(f"error opening file {file_name}")
        return 1

    if meta_key is None:
        lower = file_name.lower()
        if "biolog" in lower:
            meta_key = "biolog"
        elif "biochem" in lower or "biogeochem" in lower:
            meta_key = "biogeochem"
        elif "cow" in lower:
            meta_key = "cow"
        else:
            meta_key = "biogeochem"

    meta = get_meta(meta_key)
    warnings = []
    records = []
    headers = []

    if file_name.endswith(".xlsx"):
        df_excel = pd.read_excel(file_name)
        headers = list(df_excel.columns)
        for row_idx, row in df_excel.iterrows():
            record = {}
            for col in headers:
                raw_val = row[col]
                parsed = parse_val(raw_val)
                if parsed is None and pd.notna(raw_val) and str(raw_val).strip() != "":
                    warnings.append(f"Row {row_idx + 1}: Missing value for column '{col}'")
                record[col] = parsed
            records.append(record)
    else:
        delim = "\t" if file_name.endswith(".tsv") or file_name.endswith(".tab") else ","

        with open(file_name, "r", encoding="utf-8-sig") as f:
            first_line = f.readline()
            if not first_line:
                warnings.append(f"File {file_name} is empty")
                project = {
                    "metadata": {
                        "title": meta.get("title", ""),
                        "authors": meta.get("authors", []),
                        "doi": meta.get("doi", ""),
                        "license": meta.get("license", ""),
                        "dates": meta.get("dates", ""),
                        "location": meta.get("location", ""),
                        "description": meta.get("description", "")
                    },
                    "variables": meta.get("variables", {}),
                    "datasets": {
                        os.path.splitext(os.path.basename(file_name))[0]: {
                            "row_count": 0,
                            "col_count": 0,
                            "records": []
                        }
                    },
                    "warnings": warnings
                }
                with open(json_name, "w", encoding="utf-8") as out:
                    json.dump(project, out, indent=4)
                return 0

            if "\t" in first_line and delim == ",":
                delim = "\t"
            f.seek(0)
            reader = csv.reader(f, delimiter=delim)
            headers = [h.strip() for h in next(reader, [])]

            for row_idx, row in enumerate(reader, start=1):
                if not row or all(col.strip() == "" for col in row):
                    warnings.append(f"Row {row_idx}: Empty row skipped")
                    continue

                record = {}
                for col_idx, col_name in enumerate(headers):
                    if col_idx < len(row):
                        raw_val = row[col_idx]
                        parsed = parse_val(raw_val)
                        if parsed is None and raw_val.strip() != "":
                            warnings.append(f"Row {row_idx}: Missing value for column '{col_name}'")
                        record[col_name] = parsed
                    else:
                        record[col_name] = None
                        warnings.append(f"Row {row_idx}: Missing column '{col_name}'")
                records.append(record)

    all_vars = meta.get("variables", {}).copy()
    for h in headers:
        if h not in all_vars:
            all_vars[h] = {"description": h, "unit": ""}

    dataset_name = os.path.splitext(os.path.basename(file_name))[0]

    project = {
        "metadata": {
            "title": meta.get("title", dataset_name),
            "authors": meta.get("authors", []),
            "doi": meta.get("doi", ""),
            "license": meta.get("license", ""),
            "dates": meta.get("dates", ""),
            "location": meta.get("location", ""),
            "description": meta.get("description", "")
        },
        "variables": all_vars,
        "datasets": {
            dataset_name: {
                "row_count": len(records),
                "col_count": len(headers),
                "records": records
            }
        },
        "warnings": warnings
    }

    with open(json_name, "w", encoding="utf-8") as out:
        json.dump(project, out, indent=4)

    print(f"Done created {json_name}")
    return 0

def main():
    if len(sys.argv) < 2:
        try:
            input_csv = input("Enter file name: ").strip()
        except EOFError:
            input_csv = ""

        if len(input_csv) == 0 or input_csv == "all":
            parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json", "biolog")
            parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json", "biogeochem")
            parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json", "cow")
            return 0
        elif input_csv == "biolog" or input_csv == "Pecsi_Hawaii_Biolog_PigDecomposition.csv":
            return parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json", "biolog")
        elif input_csv == "biochem" or input_csv == "Pecsi_Hawaii_Biogeochem_PigDecomposition.csv":
            return parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json", "biogeochem")
        elif input_csv == "cow" or input_csv == "CowEnergyBalanceData-1.csv":
            return parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json", "cow")
        else:
            json_name = os.path.splitext(input_csv)[0] + ".json"
            return parse_file(input_csv, json_name)

    arg = sys.argv[1]
    if arg == "all":
        parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json", "biolog")
        parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json", "biogeochem")
        parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json", "cow")
        return 0
    elif arg == "biolog":
        return parse_file("Pecsi_Hawaii_Biolog_PigDecomposition.csv", "biolog.json", "biolog")
    elif arg == "biochem":
        return parse_file("Pecsi_Hawaii_Biogeochem_PigDecomposition.csv", "biogeochem.json", "biogeochem")
    elif arg == "cow":
        return parse_file("CowEnergyBalanceData-1.csv", "cowenergy.json", "cow")
    elif len(sys.argv) == 3:
        return parse_file(sys.argv[1], sys.argv[2])
    else:
        json_name = os.path.splitext(arg)[0] + ".json"
        return parse_file(arg, json_name)

if __name__ == "__main__":
    main()
