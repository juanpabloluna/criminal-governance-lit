"""
Usage Log page - View who has used the system and what they queried.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import streamlit as st
import pandas as pd

from src.utils.usage_logger import read_usage_log

st.markdown("## Usage Log")
st.markdown("Record of queries submitted to the system.")

entries = read_usage_log()

if not entries:
    st.info("No usage recorded yet.")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(entries)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp", ascending=False)

# Summary stats
st.markdown(f"**{len(df)} queries** by **{df['user'].nunique()} user(s)**")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total queries", len(df))
with col2:
    st.metric("Unique users", df["user"].nunique())
with col3:
    page_counts = df["page"].value_counts()
    most_used = page_counts.index[0] if len(page_counts) > 0 else "N/A"
    st.metric("Most used page", most_used)

st.markdown("---")

# Filters
with st.sidebar:
    st.markdown("### Filters")

    users = ["All"] + sorted(df["user"].unique().tolist())
    selected_user = st.selectbox("User", users)

    pages = ["All"] + sorted(df["page"].unique().tolist())
    selected_page = st.selectbox("Page", pages)

# Apply filters
filtered = df.copy()
if selected_user != "All":
    filtered = filtered[filtered["user"] == selected_user]
if selected_page != "All":
    filtered = filtered[filtered["page"] == selected_page]

st.markdown(f"Showing **{len(filtered)}** of {len(df)} entries")

# Display table
display_df = filtered[["timestamp", "user", "page", "query"]].copy()
display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
display_df.columns = ["Time", "User", "Page", "Query"]
st.dataframe(display_df, use_container_width=True, hide_index=True)

# Export
st.markdown("---")
log_json = json.dumps(entries, indent=2, ensure_ascii=False)
st.download_button(
    label="Download full log (JSON)",
    data=log_json,
    file_name="usage_log.json",
    mime="application/json",
)
