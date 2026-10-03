import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def detect_column_type(series):
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "date"
    name = str(series.name).lower()
    if "date" in name or "time" in name:
        try:
            converted = pd.to_datetime(series, errors="coerce")
            if converted.notna().sum() > len(series) * 0.5:
                return "date"
        except Exception:
            pass
    return "category"

def create_chart(df, selected_columns, chart_preference="bar"):
    if not selected_columns or df.empty:
        return None

    types = {col: detect_column_type(df[col]) for col in selected_columns}
    numeric_cols = [c for c, t in types.items() if t == "numeric"]
    category_cols = [c for c, t in types.items() if t == "category"]
    date_cols = [c for c, t in types.items() if t == "date"]

    if len(selected_columns) == 1 and len(numeric_cols) == 1:
        col = numeric_cols[0]
        fig = px.histogram(df, x=col, title=f"Distribution of {col}", marginal="box")
        fig.update_layout(template="plotly_white")
        return fig

    if len(selected_columns) == 1 and len(category_cols) == 1:
        col = category_cols[0]
        counts = df[col].value_counts().reset_index()
        counts.columns = [col, "Count"]
        fig = px.bar(counts, x=col, y="Count", title=f"Counts of {col}")
        fig.update_layout(template="plotly_white")
        return fig

    if len(numeric_cols) == 1 and (len(category_cols) == 1 or len(date_cols) == 1):
        num_col = numeric_cols[0]
        cat_col = category_cols[0] if category_cols else date_cols[0]

        if chart_preference == "box":
            fig = px.box(df, x=cat_col, y=num_col, title=f"{num_col} by {cat_col}")
        else:
            mean_df = df.groupby(cat_col, as_index=False)[num_col].mean()
            fig = px.bar(mean_df, x=cat_col, y=num_col, title=f"Mean {num_col} by {cat_col}")

        fig.update_layout(template="plotly_white")
        return fig

    if len(selected_columns) == 2 and len(numeric_cols) == 2:
        x_col, y_col = numeric_cols[0], numeric_cols[1]
        fig = px.scatter(df, x=x_col, y=y_col, title=f"{y_col} vs {x_col}")
        fig.update_layout(template="plotly_white")
        return fig

    if len(numeric_cols) >= 2 and len(category_cols) == 0 and len(date_cols) == 0:
        sub_df = df[numeric_cols].dropna()
        corr = sub_df.corr()
        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            title="Correlation Heatmap",
            color_continuous_scale="RdBu_r"
        )
        fig.update_layout(template="plotly_white")
        return fig

    if len(numeric_cols) >= 2 and len(category_cols) >= 1:
        cat_col = category_cols[0]
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        fig = px.scatter(df, x=x_col, y=y_col, color=cat_col, title=f"{y_col} vs {x_col} grouped by {cat_col}")
        fig.update_layout(template="plotly_white")
        return fig

    return None

def create_surface_chart(df, x_col, y_col, z_col):
    pivot = df.pivot_table(index=y_col, columns=x_col, values=z_col, aggfunc="mean")
    fig = go.Figure(data=[go.Surface(z=pivot.values, x=pivot.columns, y=pivot.index)])
    fig.update_layout(
        title=f"3D Surface: {z_col} by {x_col} and {y_col}",
        scene=dict(
            xaxis_title=str(x_col),
            yaxis_title=str(y_col),
            zaxis_title=str(z_col)
        )
    )
    return fig
