"""
Instructions page - renders USER_INSTRUCTIONS.md (English + Spanish).
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

st.set_page_config(
    page_title="Instructions - Literature Expert",
    page_icon="\U0001F4D6",
    layout="wide",
)

from src.utils.auth import require_auth
require_auth()

from src.utils.user_key import render_key_sidebar
render_key_sidebar()

_INSTRUCTIONS_PATH = project_root / "USER_INSTRUCTIONS.md"

try:
    st.markdown(_INSTRUCTIONS_PATH.read_text(encoding="utf-8"))
except Exception:
    st.error("Instructions file not found (USER_INSTRUCTIONS.md).")
