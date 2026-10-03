import os
import streamlit as st
from loader import load_project, get_datasets, get_dataset_names, get_dataframe, get_variable_details
from charts import create_chart, create_surface_chart, detect_column_type

# Streamlit reruns this file when a widget changes. Build the page from the
# current selections on each run; the controls below do not edit source files.
st.set_page_config(page_title="Research Data Dashboard", layout="wide")

st.sidebar.title("Data Selection")
st.sidebar.caption("Choose a research project here, then explore it using the four tabs.")

json_files = [f for f in os.listdir(".") if f.endswith(".json")]
source_choice = st.sidebar.radio("Data Source", ["Local Files", "Upload JSON"],
                                help="Local Files lists project JSON files. Upload JSON opens a file from your computer for this session.")

# The loader gives both C-generated record lists and structured project JSON
# the same metadata/datasets shape, so the tabs can display either format.
project = None


#side bar definitions
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
    uploaded = st.sidebar.file_uploader("Upload Project JSON", type=["json"],
                                       help="Use a JSON list of records or a project object containing metadata and datasets.")
    if uploaded:
        try:
            project = load_project(uploaded)
        except Exception as e:
            st.error(f"Error reading uploaded file: {str(e)}")

if not project:
    # Stop here rather than building controls for a project that failed to load.
    st.info("Please select or upload a valid project JSON file from the sidebar to begin.")
    st.stop()

metadata = project.get("metadata", {})
datasets = get_datasets(project)
dataset_names = get_dataset_names(project)
warnings = project.get("warnings", [])

st.caption("Overview: study details · Data: inspect and filter rows · Charts: compare variables · Warnings: processing messages")
tab_overview, tab_data, tab_charts, tab_warnings = st.tabs(["Overview", "Data", "Charts", "Warnings"])

with tab_overview:
    # Metadata describes the study; the summary counts describe its records.
    st.title(metadata.get("title", "Research Project Overview"))
    st.caption("Read the study details and check the number of observations and variables before exploring the data.")

    col1, col2 = st.columns(2)
    #source citattions
    with col1:
        st.subheader("Project Details")
        authors = metadata.get("authors", [])
        if isinstance(authors, list):
            authors_str = ", ".join(authors) if authors else "Not specified"
        else:
            authors_str = str(authors)

    
        st.write(f"**Authors:** {authors_str}")
        st.write(f"**License:** {metadata.get('license') or 'Not specified'}")
        st.write(f"**Collection Dates:** {metadata.get('dates') or 'Not specified'}")
        st.write(f"**Location:** {metadata.get('location') or 'Not specified'}")

        doi = metadata.get("doi", "")
        if doi:
            if doi.startswith("http"):
                st.write(f"**DOI:** [{doi}]({doi})")
            else:
                st.write(f"**DOI:** [{doi}](https://doi.org/{doi})")

    # data summary and counts
    with col2:
        st.subheader("Dataset Summary")
        st.caption("Rows are observations; columns are recorded variables.")
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
#for viewing raw data from files and filtering it
with tab_data:
    st.caption("Select a dataset, read a variable's definition, then narrow the rows shown in the table.")
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
            st.caption("Category selections keep matching rows; numeric sliders keep values within the chosen range. These filters affect this table only. Charts use the full dataset.")

            # Create a Filtered copy so the original df is not changed. 
            filtered_df = df.copy()
            filter_cols = st.columns(min(3, max(1, len(df.columns))))

            cat_cols = [c for c in df.columns if detect_column_type(df[c]) == "category"]
            num_cols = [c for c in df.columns if detect_column_type(df[c]) == "numeric"]

            # Show up to two category and two numeric controls to keep the UI
            # manageable. Categories with more than 20 values are skipped.
            filter_count = 0
            for col in cat_cols[:2]:
                with filter_cols[filter_count % len(filter_cols)]:
                    unique_vals = list(df[col].dropna().unique())
                    if len(unique_vals) <= 20:
                        chosen = st.multiselect(f"Filter by {col}", unique_vals, default=unique_vals,
                                                help="Choose categories to keep. Clearing the selection disables this category filter.")
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
            st.caption("Click a column heading to sort the table. Use the table toolbar to search or download the displayed rows.")
            st.dataframe(filtered_df, width="stretch")

with tab_charts:
    st.caption("Charts use all rows in the selected dataset, including rows hidden by filters in the Data tab.")
    if not dataset_names:
        st.warning("No datasets available.")
    else:
    
        chart_dataset = st.selectbox("Dataset for Charting", dataset_names, key="chart_ds_picker")
        chart_df = get_dataframe(project, chart_dataset)

        if chart_df.empty:
            st.warning("Dataset is empty.")
        else:
            all_cols = list(chart_df.columns)
            with st.expander("How to choose a chart"):
                st.markdown(
                    "- **One numeric variable:** histogram showing the distribution of values.\n"
                    "- **One category:** bar chart counting observations in each group.\n"
                    "- **One category and one numeric variable:** compare group means or use a box plot to see the spread.\n"
                    "- **Two numeric variables:** scatter plot showing their relationship.\n"
                    "- **Three or more numeric variables:** correlation heatmap.\n"
                    "- **One category and two numeric variables:** scatter plot colored by group."
                )
                st.caption("Hover over a chart for values. Use its toolbar to zoom, reset the view, or save an image.")
            selected_cols = st.multiselect("Select Columns to Visualize", all_cols, default=all_cols[:2] if len(all_cols) >= 2 else all_cols,
                                           help="Choose a combination described in the chart guide. The chart type is selected automatically.")

            chart_pref = "bar"
            # Column types determine which chart choices are meaningful.
            types = {c: detect_column_type(chart_df[c]) for c in selected_cols}
            numeric_count = sum(1 for t in types.values() if t == "numeric")
            category_count = sum(1 for t in types.values() if t in ("category", "date"))

            if numeric_count == 1 and category_count == 1:
                chart_pref = st.radio("Chart Presentation", ["bar", "box"], horizontal=True, format_func=lambda x: "Bar (Mean)" if x == "bar" else "Box Plot",
                                      help="Bar (Mean) compares group averages. Box Plot shows the median, middle half of values, and potential outliers.")

            if selected_cols:
                fig = create_chart(chart_df, selected_cols, chart_preference=chart_pref)
                if fig:
                    st.plotly_chart(fig, width="stretch")
                else:
                    st.warning("Could not automatically determine a chart for the chosen combination. Try selecting 1-3 numeric or category columns.")
            else:
                st.info("Select at least one column to create a chart.")

            #handling 3d surface chart for 3d comparisons 
            if len(all_cols) >= 3:
                with st.expander("Advanced Visualization: 3D Surface"):
                    st.caption("Choose X and Y to group observations, and a numeric Z value for height. Each surface point is the mean Z value for that X/Y pair; some pairs may have no observations.")
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
                            # Surface generation is opt-in because large grids
                            # can be expensive to render on every rerun.
                            try:
                                surface_fig = create_surface_chart(chart_df, x_axis, y_axis, z_axis)
                                st.plotly_chart(surface_fig, width="stretch")
                            except Exception as e:
                                st.error(f"Unable to generate surface: {str(e)}")

with tab_warnings:
    st.subheader("Data Validation & Parser Warnings")
    st.caption("Review messages reported while loading or processing the data. A message may describe a conversion or missing value; it does not always mean loading failed.")
    if warnings:
        st.warning(f"Found {len(warnings)} warning(s) during data processing:")
        for w in warnings:
            st.write(f"- {w}")
    else:
        st.success("No processing warnings were reported.")
    st.caption("This tab reports available processing messages; it does not certify that every source value is correct.")
