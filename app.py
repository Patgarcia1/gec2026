import os
import streamlit as st
import pandas as pd
from loader import load_project, get_datasets, get_dataset_names, get_dataframe, get_variable_details
from charts import create_chart, create_surface_chart, detect_column_type

st.set_page_config(page_title="Research Data Dashboard", layout="wide")

st.sidebar.title("Data Selection")

json_files = [f for f in os.listdir(".") if f.endswith(".json")]
source_choice = st.sidebar.radio("Data Source", ["Local Files", "Upload JSON"])

project = None

if source_choice == "Local Files":
    if json_files:
        default_index = 0
        if "biogeochem.json" in json_files:
            default_index = json_files.index("biogeochem.json")
        selected_file = st.sidebar.selectbox("Choose Project JSON", json_files, index=default_index)
        try:
            project = load_project(selected_file)
        except Exception as e:
            st.error(f"Error loading {selected_file}: {str(e)}")
    else:
        st.sidebar.warning("No JSON files found in current directory.")
else:
    uploaded = st.sidebar.file_uploader("Upload Project JSON", type=["json"])
    if uploaded:
        try:
            project = load_project(uploaded)
        except Exception as e:
            st.error(f"Error reading uploaded file: {str(e)}")

if not project:
    st.info("Please select or upload a valid project JSON file from the sidebar to begin.")
    st.stop()

metadata = project.get("metadata", {})
datasets = get_datasets(project)
dataset_names = get_dataset_names(project)
warnings = project.get("warnings", [])

tab_overview, tab_data, tab_charts, tab_warnings = st.tabs(["Overview", "Data", "Charts", "Warnings"])

with tab_overview:
    st.title(metadata.get("title", "Research Project Overview"))

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Project Details")
        authors = metadata.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors) if authors else "Not specified"
        else:
            authors_str = str(authors)

        st.write(f"**Authors:** {authors_str}")
        st.write(f"**License:** {metadata.get('license', 'Not specified')}")
        st.write(f"**Collection Dates:** {metadata.get('dates', 'Not specified')}")
        st.write(f"**Location:** {metadata.get('location', 'Not specified')}")

        doi = metadata.get("doi", "")
        if doi:
            if doi.startswith("http"):
                st.write(f"**DOI:** [{doi}]({doi})")
            else:
                st.write(f"**DOI:** [{doi}](https://doi.org/{doi})")

    with col2:
        st.subheader("Dataset Summary")
        for dname in dataset_names:
            ds = datasets[dname]
            rc = ds.get("row_count", len(ds.get("records", [])))
            cc = ds.get("col_count", 0)
            if cc == 0 and ds.get("records"):
                cc = len(ds.get("records")[0])
            st.metric(label=dname, value=f"{rc} rows", delta=f"{cc} columns", delta_color="off")

    if metadata.get("description"):
        st.markdown("---")
        st.subheader("Description")
        st.write(metadata["description"])

with tab_data:
    if not dataset_names:
        st.warning("No datasets found in project.")
    else:
        active_dataset = st.selectbox("Select Dataset", dataset_names)
        df = get_dataframe(project, active_dataset)

        if df.empty:
            st.warning("Selected dataset contains no records.")
        else:
            st.subheader("Variable Information")
            selected_var = st.selectbox("Inspect Variable Details", list(df.columns))
            desc, unit = get_variable_details(project, selected_var)
            unit_display = f" | Unit: {unit}" if unit else ""
            st.info(f"**{selected_var}**: {desc}{unit_display}")

            st.markdown("---")
            st.subheader("Filter Data")

            filtered_df = df.copy()
            filter_cols = st.columns(min(3, max(1, len(df.columns))))

            cat_cols = [c for c in df.columns if detect_column_type(df[c]) == "category"]
            num_cols = [c for c in df.columns if detect_column_type(df[c]) == "numeric"]

            filter_count = 0
            for col in cat_cols[:2]:
                with filter_cols[filter_count % len(filter_cols)]:
                    unique_vals = list(df[col].dropna().unique())
                    if len(unique_vals) <= 20:
                        chosen = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals)
                        if chosen:
                            filtered_df = filtered_df[filtered_df[col].isin(chosen)]
                        filter_count += 1

            for col in num_cols[:2]:
                with filter_cols[filter_count % len(filter_cols)]:
                    col_min = float(df[col].min())
                    col_max = float(df[col].max())
                    if col_min < col_max:
                        val_range = st.slider(f"Range for {col}", col_min, col_max, (col_min, col_max))
                        filtered_df = filtered_df[(filtered_df[col] >= val_range[0]) & (filtered_df[col] <= val_range[1])]
                        filter_count += 1

            st.markdown("---")
            st.subheader(f"Data Table ({len(filtered_df)} of {len(df)} rows)")
            st.dataframe(filtered_df, use_container_width=True)

with tab_charts:
    if not dataset_names:
        st.warning("No datasets available.")
    else:
        chart_dataset = st.selectbox("Dataset for Charting", dataset_names, key="chart_ds_picker")
        chart_df = get_dataframe(project, chart_dataset)

        if chart_df.empty:
            st.warning("Dataset is empty.")
        else:
            all_cols = list(chart_df.columns)
            selected_cols = st.multiselect("Select Columns to Visualize", all_cols, default=all_cols[:2] if len(all_cols) >= 2 else all_cols)

            chart_pref = "bar"
            types = {c: detect_column_type(chart_df[c]) for c in selected_cols}
            numeric_count = sum(1 for t in types.values() if t == "numeric")
            category_count = sum(1 for t in types.values() if t in ("category", "date"))

            if numeric_count == 1 and category_count == 1:
                chart_pref = st.radio("Chart Presentation", ["bar", "box"], horizontal=True, format_func=lambda x: "Bar (Mean)" if x == "bar" else "Box Plot")

            if selected_cols:
                fig = create_chart(chart_df, selected_cols, chart_preference=chart_pref)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Could not automatically determine a chart for the chosen combination. Try selecting 1-3 numeric or category columns.")

            if len(all_cols) >= 3:
                with st.expander("Advanced Visualization: 3D Surface"):
                    numeric_options = [c for c in all_cols if detect_column_type(chart_df[c]) == "numeric"]
                    cat_options = [c for c in all_cols if detect_column_type(chart_df[c]) == "category"]
                    avail_options = cat_options + numeric_options

                    if len(avail_options) >= 2 and len(numeric_options) >= 1:
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            x_axis = st.selectbox("X Axis", avail_options, index=0)
                        with c2:
                            y_axis = st.selectbox("Y Axis", [c for c in avail_options if c != x_axis], index=0)
                        with c3:
                            z_axis = st.selectbox("Z Axis (Value)", numeric_options, index=0)

                        if st.button("Generate 3D Surface"):
                            try:
                                surface_fig = create_surface_chart(chart_df, x_axis, y_axis, z_axis)
                                st.plotly_chart(surface_fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Unable to generate surface: {str(e)}")

with tab_warnings:
    st.subheader("Data Validation & Parser Warnings")
    if warnings:
        st.warning(f"Found {len(warnings)} warning(s) during data processing:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No issues")
