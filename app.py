"""
Main Streamlit application for Literature Expert Agent (HuggingFace Spaces).
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import streamlit as st
from loguru import logger

# Page configuration — must be the first Streamlit command
st.set_page_config(
    page_title="Criminal Governance Literature Expert",
    page_icon="\U0001F4DA",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Password gate ---
def check_password():
    """Simple password gate for access control."""
    access_password = os.environ.get("ACCESS_PASSWORD", "")
    if not access_password:
        # No password configured — allow access (local dev)
        return True

    if st.session_state.get("authenticated"):
        return True

    st.markdown("## Criminal Governance Literature Expert")
    st.markdown("This application is password-protected. Enter the access code to continue.")

    password = st.text_input("Access code", type="password", key="password_input")
    if st.button("Enter", type="primary"):
        if password == access_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect access code.")
    return False


if not check_password():
    st.stop()

# --- Main app (only runs after authentication) ---

from src.config.settings import settings
from src.embeddings.vector_store import VectorStore
from src.rag.retriever import Retriever

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f77b4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_retriever():
    """Initialize and cache the retriever."""
    try:
        return Retriever()
    except Exception as e:
        st.error(f"Error initializing retriever: {e}")
        logger.error(f"Failed to initialize retriever: {e}", exc_info=True)
        return None


def main():
    """Main application page."""

    # Header
    st.markdown(
        '<div class="main-header">Criminal Governance Literature Expert</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">RAG-based research assistant for organized crime, violence, and Latin American politics (304 papers)</div>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        st.markdown("""
        Use the pages in the sidebar to:
        - **Question Answering**: Traditional RAG Q&A
        - **Agentic Q&A**: Claude orchestrates its own research
        - **Literature Synthesis**: Generate literature reviews
        - **Research Review**: Get feedback on drafts
        """)

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This agent helps you query a corpus of 304 academic papers
        on criminal governance, organized crime, violence, and
        Latin American politics through:
        - Semantic search across papers
        - Citation-backed answers
        - Literature synthesis
        - Research draft review
        """)

    # Main content
    tab1, tab2, tab3 = st.tabs(["Overview", "System Status", "Quick Start"])

    with tab1:
        st.markdown("## System Overview")

        col1, col2, col3 = st.columns(3)

        retriever = get_retriever()
        if retriever:
            try:
                stats = retriever.get_stats()
                vs_stats = stats.get("vector_store", {})

                with col1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{vs_stats.get('total_chunks', 0):,}</div>
                        <div class="stat-label">Total Chunks</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{vs_stats.get('sample_unique_items', 0):,}</div>
                        <div class="stat-label">Documents Indexed</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    year_range = vs_stats.get("year_range", (None, None))
                    year_text = f"{year_range[0]}-{year_range[1]}" if year_range[0] else "N/A"
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-value">{year_text}</div>
                        <div class="stat-label">Year Range</div>
                    </div>
                    """, unsafe_allow_html=True)

                if vs_stats.get("sample_collections"):
                    st.markdown("### Collections in Database")
                    cols = st.columns(2)
                    for i, coll in enumerate(vs_stats["sample_collections"][:6]):
                        with cols[i % 2]:
                            st.markdown(f"- {coll}")

            except Exception as e:
                st.error(f"Error loading statistics: {e}")
                logger.error(f"Error in stats display: {e}", exc_info=True)
        else:
            st.warning("Retriever not initialized. Please check configuration.")

    with tab2:
        st.markdown("## System Status")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Configuration")
            st.code(f"""
Embedding Model: {settings.embedding_model}
LLM Model: {settings.llm_model}
Chunk Size: {settings.chunk_size} tokens
Chunk Overlap: {settings.chunk_overlap} tokens
Top-K Results: {settings.top_k}
            """)

        with col2:
            st.markdown("### Paths")
            st.code(f"""
ChromaDB: {settings.chromadb_path}
            """)

        if retriever:
            st.markdown("### Vector Database")
            try:
                count = retriever.vector_store.count()
                st.success(f"Connected - {count:,} chunks indexed")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("### API Configuration")
        if settings.anthropic_api_key and settings.anthropic_api_key != "YOUR_API_KEY_HERE":
            st.success("Anthropic API key configured")
        else:
            st.error("Anthropic API key not configured")

    with tab3:
        st.markdown("## Quick Start Guide")

        st.markdown("""
        ### How to Use

        1. **Question Answering** -- Ask questions about the criminal governance literature.
           Filter by collection or year range. Get citation-backed answers.

        2. **Agentic Q&A** -- Claude autonomously decides which searches to run,
           iterating until it has enough evidence. Best for complex questions.

        3. **Literature Synthesis** -- Enter a topic and generate a structured
           literature review with bibliography.

        4. **Research Review** -- Paste a research draft to get feedback
           with supporting/contradicting evidence from the corpus.

        ### Tips

        - Be specific in your questions for best results
        - Use collection filters to narrow your search domain
        - Check sources to see which papers were used
        """)

        st.markdown("### Example Questions")
        examples = [
            "What factors explain variation in gang violence across Latin American cities?",
            "How do criminal organizations interact with local communities?",
            "What is the relationship between state capacity and organized crime?",
            "How does incarceration affect crime rates in Latin America?",
            "What are the main theories of criminal governance?",
        ]

        for example in examples:
            if st.button(f"{example}", key=example, use_container_width=True):
                st.session_state["example_question"] = example
                st.info("Go to the **Question Answering** page and paste this question!")


if __name__ == "__main__":
    main()
