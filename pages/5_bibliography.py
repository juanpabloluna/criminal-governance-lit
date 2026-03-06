"""
Bibliography page - Full list of indexed papers in APA format.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from loguru import logger


st.markdown("## Bibliography")
st.markdown(
    "Complete list of papers indexed in this corpus, formatted in APA style."
)

METADATA_PATH = Path(__file__).parent.parent / "data" / "papers_metadata.json"


@st.cache_data(ttl=3600)
def get_all_papers():
    """Load paper metadata from JSON file."""
    try:
        with open(METADATA_PATH) as f:
            records = json.load(f)
        # Key by item_id for dedup
        papers = {}
        for r in records:
            item_id = r.get("item_id")
            if item_id and item_id not in papers:
                papers[item_id] = r
        return papers
    except Exception as e:
        logger.error(f"Error loading papers metadata: {e}")
        return {}


def format_apa(paper):
    """Format a paper entry in APA 7th edition style."""
    authors = paper.get("authors", [])
    year = paper.get("year")
    title = paper.get("title", "Untitled")
    publication = paper.get("publication")
    doi = paper.get("doi")
    url = paper.get("url")

    # Authors
    if not authors:
        author_str = "Unknown"
    elif len(authors) == 1:
        author_str = authors[0]
    elif len(authors) == 2:
        author_str = f"{authors[0]} & {authors[1]}"
    elif len(authors) <= 20:
        author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
    else:
        author_str = ", ".join(authors[:19]) + f", ... {authors[-1]}"

    # Year
    year_str = f"({year})" if year else "(n.d.)"

    # Build citation
    parts = [f"{author_str} {year_str}. {title}."]

    if publication:
        parts.append(f"*{publication}*.")

    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        parts.append(doi_url)
    elif url:
        parts.append(url)

    return " ".join(parts)


papers = get_all_papers()

if not papers:
    st.warning("No papers found.")
    st.stop()

# Statistics
st.markdown(f"**{len(papers)} papers indexed**")

# Collect all collections for filter
all_collections = set()
for p in papers.values():
    for c in p.get("collections", []):
        if c:
            all_collections.add(c)

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")

    if all_collections:
        selected_collection = st.selectbox(
            "Collection",
            ["All"] + sorted(all_collections),
        )
    else:
        selected_collection = "All"

    years = [p["year"] for p in papers.values() if p.get("year")]
    if years:
        min_year, max_year = min(years), max(years)
        year_range = st.slider(
            "Year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
        )
    else:
        year_range = None

    search_query = st.text_input("Search by author or title")

# Apply filters
filtered = {}
for item_id, paper in papers.items():
    if selected_collection != "All":
        if selected_collection not in paper.get("collections", []):
            continue

    if year_range and paper.get("year"):
        if paper["year"] < year_range[0] or paper["year"] > year_range[1]:
            continue

    if search_query:
        query_lower = search_query.lower()
        authors_text = " ".join(paper.get("authors", [])).lower()
        title_text = paper.get("title", "").lower()
        pub_text = (paper.get("publication") or "").lower()
        if query_lower not in authors_text and query_lower not in title_text and query_lower not in pub_text:
            continue

    filtered[item_id] = paper

st.markdown(f"Showing **{len(filtered)}** of {len(papers)} papers")
st.markdown("---")

# Sort by first author last name, then year
sorted_papers = sorted(
    filtered.values(),
    key=lambda p: (
        p["authors"][0].split(",")[0].lower() if p.get("authors") else "zzz",
        p.get("year") or 0,
    ),
)

# Display bibliography
for paper in sorted_papers:
    st.markdown(format_apa(paper))

# Export
st.markdown("---")
bib_text = "\n\n".join(format_apa(p) for p in sorted_papers)
st.download_button(
    label="Download bibliography (.txt)",
    data=bib_text,
    file_name="criminal_governance_bibliography.txt",
    mime="text/plain",
)
