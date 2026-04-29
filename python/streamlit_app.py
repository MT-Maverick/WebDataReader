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

numeric_df = df.select_dtypes(include="number")
if not numeric_df.empty:
    st.markdown("### Numeric summary")
    st.dataframe(numeric_df.describe().transpose(), use_container_width=True)

    numeric_column = st.selectbox("Select numeric column to chart", numeric_df.columns)
    if numeric_column:
        st.bar_chart(df[numeric_column].dropna())
else:
    st.info("No numeric columns found. Upload a spreadsheet with numbers to enable charts.")

st.markdown("---")
st.markdown("### Hosting notes")
st.markdown(
    """
    - Run the dashboard with `streamlit run python/streamlit_app.py`
    - Use the Node upload app at `http://localhost:3000` to place spreadsheet files into the shared `uploads/` folder.
    - To host behind IIS, configure IIS Application Request Routing (ARR) or a reverse proxy to forward a public IIS URL to the local Streamlit service on `http://localhost:8501`.
    """
)
