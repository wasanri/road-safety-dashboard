import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Road Safety Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.title("Road Accident Risk Management")
st.write("Road Safety Dashboard | Saudi Arabia | 2020–2024")

# Load the actual Excel dataset
file_path = Path(__file__).parent / "Dataset.xlsx"

if not file_path.exists():
    st.error(
        "Excel file not found. Put the dataset in the same "
        "folder as app.py and check the filename."
    )
    st.stop()

try:
    excel = pd.ExcelFile(file_path)

    # Find the worksheet containing the required columns
    df = None

    for sheet in excel.sheet_names:
        temp = pd.read_excel(file_path, sheet_name=sheet)
        temp.columns = [
            str(c).strip().lower() for c in temp.columns
        ]

        required = {
            "year", "region_en", "injury_rate", "death_rate"
        }

        if required.issubset(temp.columns):
            df = temp
            break

    if df is None:
        st.error(
            "Could not find a worksheet containing year, region_en, "
            "injury_rate, and death_rate."
        )
        st.write("Available worksheets:", excel.sheet_names)
        st.stop()

except Exception as e:
    st.error(f"Error reading Excel file: {e}")
    st.stop()

# Prepare the real data
df["year"] = pd.to_numeric(df["year"], errors="coerce")
df["injury_rate"] = pd.to_numeric(
    df["injury_rate"], errors="coerce"
)
df["death_rate"] = pd.to_numeric(
    df["death_rate"], errors="coerce"
)

df = df.dropna(
    subset=["year", "region_en", "injury_rate", "death_rate"]
)

df["year"] = df["year"].astype(int)
df = df[df["year"].between(2020, 2024)]

if df.empty:
    st.error("No usable data found for 2020–2024.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")

years = sorted(df["year"].unique())
selected_years = st.sidebar.multiselect(
    "Select years",
    options=years,
    default=years
)

regions = sorted(df["region_en"].astype(str).unique())
selected_regions = st.sidebar.multiselect(
    "Select regions",
    options=regions,
    default=regions
)

filtered = df[
    df["year"].isin(selected_years)
    & df["region_en"].astype(str).isin(selected_regions)
]

if filtered.empty:
    st.warning("Select at least one year and one region.")
    st.stop()

# KPI cards
c1, c2 = st.columns(2)

c1.metric(
    "Average Injury Rate",
    f"{filtered['injury_rate'].mean():.2f}"
)

c2.metric(
    "Average Death Rate",
    f"{filtered['death_rate'].mean():.2f}"
)

# Average rates by year across selected regions
yearly = (
    filtered.groupby("year", as_index=False)
    [["injury_rate", "death_rate"]]
    .mean()
)

fig = px.line(
    yearly,
    x="year",
    y=["injury_rate", "death_rate"],
    markers=True,
    title="Average Injury and Death Rates by Year",
    labels={
        "year": "Year",
        "value": "Rate",
        "variable": "Indicator"
    }
)

st.plotly_chart(fig, use_container_width=True)

# Compare regions
regional = (
    filtered.groupby("region_en", as_index=False)
    [["injury_rate", "death_rate"]]
    .mean()
)

fig2 = px.bar(
    regional,
    x="region_en",
    y=["injury_rate", "death_rate"],
    barmode="group",
    title="Average Injury and Death Rates by Region",
    labels={
        "region_en": "Region",
        "value": "Rate",
        "variable": "Indicator"
    }
)

st.plotly_chart(fig2, use_container_width=True)

# Actual data table
st.subheader("Dataset")
st.dataframe(
    filtered.sort_values(["year", "region_en"]),
    use_container_width=True
)

st.caption(
    "Source: The uploaded road safety dataset. "
    "Rates are displayed as recorded in the source file."
)