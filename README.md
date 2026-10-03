# Environmental & Biological Research Data Dashboard

## Team Information
- **Project Title:** Interactive Multi-Dataset Scientific Analysis Dashboard

## Overview
An interactive Streamlit application for exploring, filtering, analyzing, and visualizing research datasets from soil biogeochemistry, microbial ecoplate profiles, and dairy cattle metabolic energy balance studies.

## Project Structure
- `parse.py`: Command-line data parser converting CSV, TSV, and XLSX datasets into structured JSON with typed numbers, variable definitions, and validation warnings.
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

4. **Run Data Parser (Optional)**
   To re-parse the datasets from their raw CSV/XLSX sources:
   ```bash
   python parse.py all
   ```

5. **Launch the Dashboard**
   ```bash
   streamlit run app.py
   ```

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
