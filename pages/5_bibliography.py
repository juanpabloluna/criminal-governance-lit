"""
Bibliography page - Full list of indexed papers in APA format.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from loguru import logger

from src.embeddings.vector_store import VectorStore


st.markdown("## Bibliography")
st.markdown(
    "Complete list of papers indexed in this corpus, formatted in APA style."
)


@st.cache_data(ttl=3600)
def get_all_papers():
    """Extract unique papers from ChromaDB metadata."""
    try:
        vs = VectorStore()
        # Get all metadata (no need for documents/embeddings)
        result = vs.collection.get(include=["metadatas"])

        papers = {}
        for metadata in result["metadatas"]:
            item_id = metadata.get("item_id")
            if item_id and item_id not in papers:
                authors_raw = metadata.get("authors", "")
                authors = [a.strip() for a in authors_raw.split(";") if a.strip()]
                year = metadata.get("year", 0)
                title = metadata.get("title", "Untitled")
                collections_raw = metadata.get("collections", "")
                collections = [c.strip() for c in collections_raw.split(";") if c.strip()]

                papers[item_id] = {
                    "authors": authors,
                    "year": year if year > 0 else None,
                    "title": title,
                    "collections": collections,
                }

        return papers
    except Exception as e:
        logger.error(f"Error loading papers: {e}")
        return {}


def format_apa(paper):
    """Format a paper entry in APA style."""
    authors = paper["authors"]
    year = paper["year"]
    title = paper["title"]

    # Format authors: Last, F. M., Last, F. M., & Last, F. M.
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

    year_str = f"({year})" if year else "(n.d.)"

    return f"{author_str} {year_str}. {title}."


papers = get_all_papers()

if not papers:
    st.warning("No papers found in the database.")
    st.stop()

# Statistics
st.markdown(f"**{len(papers)} papers indexed**")

# Collect all collections for filter
all_collections = set()
for p in papers.values():
    all_collections.update(p["collections"])

# Sidebar filters
with st.sidebar:
    st.markdown("### Filters")

    # Collection filter
    if all_collections:
        selected_collection = st.selectbox(
            "Collection",
            ["All"] + sorted(all_collections),
        )
    else:
        selected_collection = "All"

    # Year range
    years = [p["year"] for p in papers.values() if p["year"]]
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

    # Search
    search_query = st.text_input("Search by author or title")

# Apply filters
filtered = {}
for item_id, paper in papers.items():
    # Collection filter
    if selected_collection != "All":
        if selected_collection not in paper["collections"]:
            continue

    # Year filter
    if year_range and paper["year"]:
        if paper["year"] < year_range[0] or paper["year"] > year_range[1]:
            continue

    # Search filter
    if search_query:
        query_lower = search_query.lower()
        authors_text = " ".join(paper["authors"]).lower()
        title_text = paper["title"].lower()
        if query_lower not in authors_text and query_lower not in title_text:
            continue

    filtered[item_id] = paper

st.markdown(f"Showing **{len(filtered)}** of {len(papers)} papers")
st.markdown("---")

# Sort by first author last name, then year
sorted_papers = sorted(
    filtered.values(),
    key=lambda p: (
        p["authors"][0].split(",")[0].lower() if p["authors"] else "zzz",
        p["year"] or 0,
    ),
)

# Display bibliography
for paper in sorted_papers:
    st.markdown(format_apa(paper))

# Export option
st.markdown("---")
bib_text = "\n\n".join(format_apa(p) for p in sorted_papers)
st.download_button(
    label="Download bibliography (.txt)",
    data=bib_text,
    file_name="criminal_governance_bibliography.txt",
    mime="text/plain",
)
