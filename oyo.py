import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# ---------------------------------------------------------
# Cleaning helpers
# ---------------------------------------------------------
def to_num_rating(x):
    if pd.isna(x):
        return np.nan
    m = re.search(r"(\d+(\.\d+)?)", str(x))
    return float(m.group(1)) if m else np.nan

def to_num_int(x):
    if pd.isna(x):
        return np.nan
    s = str(x).lower().replace("₹", "").replace(",", "").strip()
    m_k = re.fullmatch(r"(\d+(\.\d+)?)\s*k", s)
    if m_k:
        return int(float(m_k.group(1)) * 1000)
    s = re.sub(r"[^\d.]", "", s)
    return int(float(s)) if s else np.nan

def to_num_float(x):
    if pd.isna(x):
        return np.nan
    s = str(x).lower().replace("₹", "").replace(",", "")
    s = re.sub(r"[^\d.]", "", s)
    return float(s) if s else np.nan

def extract_room_size(x):
    if pd.isna(x):
        return np.nan
    m = re.search(r"(\d+(\.\d+)?)", str(x).lower())
    return float(m.group(1)) if m else np.nan

def extract_city(addr):
    if pd.isna(addr):
        return np.nan
    parts = [p.strip() for p in str(addr).split(",") if p.strip()]
    if not parts:
        return np.nan
    for candidate in reversed(parts):
        if re.search(r"[A-Za-z]", candidate) and len(candidate) >= 3:
            return candidate
    return parts[-1]

def split_amenities(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return []
    if isinstance(val, (list, tuple, np.ndarray)):
        return [str(x).strip() for x in val if str(x).strip()]
    s = str(val)
    s = s.replace("|", ",").replace("•", ",").replace(";", ",")
    return [x.strip() for x in s.split(",") if x.strip()]

# ---------------------------------------------------------
# Load dataset (direct)
# ---------------------------------------------------------
DATA_PATH = "OYO.json"
try:
    df = pd.read_json(DATA_PATH)
except:
    df = pd.read_json(DATA_PATH, lines=True)

rename_map = {
    "NAME": "hotel_name",
    "RATING": "rating",
    "RATED BY": "rated_by",
    "BASE_COST": "base_cost",
    "FINAL_COST": "final_cost",
    "ROOM SIZE": "room_size",
    "AMENITYS": "amenities",
    "ADDRESS": "address",
    "CATEGORY": "category",
}
df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

# Clean
if "rating" in df:
    df["rating"] = df["rating"].apply(to_num_rating)
if "rated_by" in df:
    df["rated_by"] = df["rated_by"].apply(to_num_int)
if "base_cost" in df:
    df["base_cost"] = df["base_cost"].apply(to_num_float)
if "final_cost" in df:
    df["final_cost"] = df["final_cost"].apply(to_num_float)
if "room_size" in df:
    df["room_size_sqft"] = df["room_size"].apply(extract_room_size)
if "address" in df:
    df["city"] = df["address"].apply(extract_city)
if "amenities" in df:
    df["amenities_list"] = df["amenities"].apply(split_amenities)

# Derived
if set(["base_cost", "final_cost"]).issubset(df.columns):
    df["discount_value"] = df["base_cost"] - df["final_cost"]
    df["discount_pct"] = (df["discount_value"] / df["base_cost"] * 100).round(2)

# ---------------------------------------------------------
# Streamlit setup
# ---------------------------------------------------------
st.set_page_config(page_title="OYO Hotels Dashboard", layout="wide")

# Sidebar Filters
st.sidebar.header("🔍 Filters")
cities = df["city"].dropna().unique().tolist()
city_filter = st.sidebar.multiselect("City", sorted(cities))
if city_filter:
    df = df[df["city"].isin(city_filter)]

if "rating" in df:
    min_r, max_r = float(df["rating"].min()), float(df["rating"].max())
    rating_range = st.sidebar.slider("Rating range", min_r, max_r, (min_r, max_r))
    df = df[df["rating"].between(*rating_range)]

all_amens = sorted({a for row in df.get("amenities_list", []) for a in row})
amen_filter = st.sidebar.multiselect("Amenities", all_amens)
if amen_filter:
    df = df[df["amenities_list"].apply(lambda x: all(am in x for am in x))]

# ---------------------------------------------------------
# Multi-page Dashboard
# ---------------------------------------------------------
page = st.sidebar.radio("📄 Pages", ["Overview", "Deep Dive"])

# ---------------------------------------------------------
# PAGE 1 → Overview
# ---------------------------------------------------------
if page == "Overview":
    st.title("🏨 OYO Hotels Dashboard — Overview")

    # KPIs row
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Hotels", len(df))
    kpi2.metric("Avg Rating", round(df["rating"].mean(), 2))
    kpi3.metric("Avg Final Price", f"₹{round(df['final_cost'].mean(), 0)}")
    kpi4.metric("Median Discount %", f"{round(df['discount_pct'].median(), 1)}%")

    # Row 1: Rating Distribution + Price Distribution
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        fig = px.histogram(df, x="rating", nbins=20, title="⭐ Rating Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with row1_col2:
        fig = px.box(df, y=["base_cost", "final_cost"], title="💰 Price Distribution (Base vs Final)")
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Discount Distribution + Top Hotels
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        fig = px.histogram(df, x="discount_pct", nbins=25, title="🏷️ Discount % Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with row2_col2:
        top_hotels = df.groupby("hotel_name")["rating"].mean().nlargest(10).reset_index()
        fig = px.bar(top_hotels, x="rating", y="hotel_name", orientation="h", 
                     title="🏆 Top 10 Hotels by Rating", color="rating", color_continuous_scale="viridis")
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# PAGE 2 → Deep Dive
# ---------------------------------------------------------
elif page == "Deep Dive":
    st.title("🔎 OYO Hotels Dashboard — Deep Dive")

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        top_cities = df["city"].value_counts().head(10).reset_index()
        top_cities.columns = ["city", "count"]
        fig = px.bar(top_cities, x="count", y="city", orientation="h", 
                     title="📍 Top Cities by Hotels", color="count", color_continuous_scale="plasma")
        st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        cats = df["category"].fillna("Unknown").value_counts().reset_index()
        cats.columns = ["category", "count"]
        fig = px.bar(cats, x="count", y="category", orientation="h", 
                     title="📊 Categories Distribution", color="count", color_continuous_scale="teal")
        st.plotly_chart(fig, use_container_width=True)

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        all_amens = Counter(a for row in df["amenities_list"] for a in row)
        amen_s = pd.Series(dict(all_amens)).sort_values(ascending=False).head(15).reset_index()
        amen_s.columns = ["amenity", "count"]
        fig = px.bar(amen_s, x="count", y="amenity", orientation="h", 
                     title="🧰 Amenities Frequency (Top 15)", color="count", color_continuous_scale="magma")
        st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        num_cols = [
            "rating",
            "rated_by",
            "base_cost",
            "final_cost",
            "discount_value",
            "discount_pct",
            "room_size_sqft",
        ]
        corr = df[num_cols].corr().stack().reset_index()
        corr.columns = ["var1", "var2", "value"]
        fig = px.imshow(df[num_cols].corr(), text_auto=True, 
                        title="📐 Correlation Heatmap", color_continuous_scale="RdBu_r", aspect="auto")
        st.plotly_chart(fig, use_container_width=True)




