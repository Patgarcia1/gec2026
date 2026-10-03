# Environmental & Biological Research Data Dashboard

## Team Information
- **Project Title:** Interactive Multi-Dataset Scientific Analysis Dashboard

## Overview
An interactive Streamlit application for exploring, filtering, analyzing, and visualizing research datasets from soil biogeochemistry, microbial ecoplate profiles, and dairy cattle metabolic energy balance studies.

## Project Structure
- `parse.c`: CSV parser used by the Windows launchers to generate JSON record lists.
- `run_parser.bat`: Compiles and runs the C parser for all three datasets.
- `parse.py`: README metadata extraction and value conversion helpers used by the Python loader. Dataset file parsing is performed by `parse.c`.
- `loader.py`: Module for loading and validating project JSON files into pandas DataFrames.
- `charts.py`: Automated chart selection engine using Plotly Express and Plotly Graph Objects.
- `app.py`: Streamlit multi-tab user interface (Overview, Data, Charts, Warnings).
- `requirements.txt`: Python package dependencies.
- `biogeochem.json`: Parsed biogeochemical soil measurements.
- `biolog.json`: Parsed Biolog EcoPlate carbon substrate profiles.
- `cowenergy.json`: Parsed dairy cow daily energy flows dataset.

## Installation and Run Steps

1. **Prerequisites**
   Python 3.10 or later installed on your system.

2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the C Data Parser**
   On Windows, install GCC (MinGW-w64) and run:
   ```bat
   run_parser.bat
   ```
   This compiles the unchanged `parse.c` and sends `all` to its input prompt
   to regenerate the three JSON files. The Python loader adds metadata and
   converts numeric strings for the dashboard; CSV parsing is performed by C.
   `get_meta(key)` reads the corresponding dataset README on each call to extract
   titles, authors, collection dates, locations, licenses, descriptions, and
   variable definitions. Only explicitly identified dataset DOIs are used;
   ancillary links are not treated as dataset DOIs. Missing fields remain empty.

5. **Launch the Dashboard**
   ```bat
   run.bat
   ```
   The launcher runs the C parser before starting the Python dashboard.

## Features
- **Project Selection:** Switch seamlessly between local project JSON files or upload a custom JSON directly in the sidebar.
- **Overview Tab:** Summary of study metadata, author credentials, DOI, licenses, and dataset dimensions.
- **Data Tab:** Interactive sortable tables, category multiselect filters, numeric range sliders, and column variable descriptions.
- **Charts Tab:** Dynamic visualization selecting appropriate graphs based on column data types (histograms, bar plots of means, box plots, scatter plots, correlation heatmaps, and 3D surface models).
- **Warnings Tab:** Parser diagnostics reporting missing values, formatting anomalies, or validation confirmation.

## References & IEEE Citations

[1] Streamlit Inc., "Streamlit: The fastest way to build and share data apps," 2026. [Online]. Available: https://docs.streamlit.io.

[2] Plotly Technologies Inc., "Plotly Open Source Graphing Library for Python," Montreal, QC, 2026. [Online]. Available: https://plotly.com/python/.

[3] The pandas development team, "pandas-dev/pandas: Pandas," Zenodo, 2026. doi: 10.5281/zenodo.3509134.

[4] E. L. Pecsi, D. O. Carter, M. B. Plourde, T. Devèze, H. Germain, S. Forbes, and F. Guillemette, "Biogeochemical evaluation of soils impacted by pig carcass decomposition in a Hawaiian tropical savanna ecosystem," Université du Québec à Trois-Rivières, Borealis, 2026. doi: 10.5683/SP4/UXYJGA.

[5] E. L. Pecsi, S. Forbes, and F. Guillemette, "Biolog EcoPlate profiles of soil bacterial communities impacted by pig carcass decomposition in a Hawaiian tropical savanna ecosystem," Université du Québec à Trois-Rivières, Borealis, 2026. doi: 10.5683/SP3/DEH8FG.

[6] J. Cant, P. Kedzierski, and C. Reyes, "Daily energy flows of freestall-housed dairy cattle estimated with automated data collection," Borealis, V1, 2026. doi: 10.5683/SP4/MS7XVT.
