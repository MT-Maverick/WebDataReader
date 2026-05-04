import pandas as pd
import streamlit as st
from pathlib import Path

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Spreadsheet Dashboard", page_icon="📊", layout="wide")

st.title("Spreadsheet Dashboard Service")
st.markdown(
    """
    Use this dashboard to explore spreadsheet files uploaded through the file sharing service.
    The app reads files from the shared `uploads/` folder used by the Node upload service.

    """
)

file_list = sorted(
    [path for path in UPLOAD_DIR.iterdir() if path.suffix.lower() in {".csv", ".xlsx", ".xls"}],
    key=lambda path: path.name,
)

if not file_list:
    st.info("No spreadsheet files found in the shared `uploads/` directory.")
    st.markdown(
        "Upload a spreadsheet first through the Node app at `http://localhost:3000` or place files in the `uploads/` folder."
    )
    st.stop()

selected_file = st.selectbox("Choose a spreadsheet", file_list, format_func=lambda path: path.name)

@st.cache_data(show_spinner=False)
def load_sheet(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)

try:
    df = load_sheet(selected_file)
except Exception as exc:
    st.error(f"Unable to read {selected_file.name}: {exc}")
    st.stop()

st.markdown("## File summary")
col1, col2, col3 = st.columns(3)
col1.metric("Rows", len(df))
col2.metric("Columns", len(df.columns))
col3.metric("File size", f"{selected_file.stat().st_size / 1024:.1f} KB")

with st.expander("Preview data", expanded=True):
    st.dataframe(df.head(20), use_container_width=True)

with st.expander("Column details"):
    details = pd.DataFrame(
        {
            "Column": df.columns,
            "Type": df.dtypes.astype(str),
            "Non-null": df.notna().sum().values,
        }
    )
    st.dataframe(details, use_container_width=True)

st.markdown("### Complete Data Summary")

full_summary = df.describe(include='all').transpose()
st.dataframe(full_summary, use_container_width=True)


def categorical_impact_analyzer(df):
    st.write("## 🎯 Categorical Impact Analysis")
    
    # 1. Identify the column types
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    num_cols = df.select_dtypes(include=['number']).columns.tolist()

    if not cat_cols or not num_cols:
        st.warning("Need both categorical and numerical columns for this analysis.")
        return

    # 2. Let the user pick the "Metric of Interest" (The Y-Axis)
    # This prevents the app from guessing wrong
    target_num = st.selectbox("Select the numeric metric to analyze:", num_cols)
    
    # Optional: Let them choose the aggregation method
    stat_type = st.radio("Show:", ["Average", "Total Sum"], horizontal=True)

    st.divider()

    # 3. Create Tabs for each Category to keep the page clean
    if cat_cols:
        tabs = st.tabs(cat_cols)  # Creates one tab per categorical column

        for i, col in enumerate(cat_cols):
            with tabs[i]:
                st.write(f"### {target_num} by {col}")
                
                # Perform the grouping
                if stat_type == "Average":
                    analysis = df.groupby(col)[target_num].mean().sort_values(ascending=False)
                    label = f"Average {target_num}"
                else:
                    analysis = df.groupby(col)[target_num].sum().sort_values(ascending=False)
                    label = f"Total {target_num}"

                # Render the chart
                st.bar_chart(analysis)
                
                # Show a small data table snippet for the curious user
                with st.expander("View raw numbers"):
                    st.dataframe(analysis)

# Usage:
categorical_impact_analyzer(df)

st.markdown("---")
st.markdown("### Hosting notes")
st.markdown(
    """
    - Use the Node upload app at http://localhost:3000 to place spreadsheet files into the shared `uploads/` folder.
    """
)
