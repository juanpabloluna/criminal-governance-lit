"""Per-session Anthropic API key handling.

Two tiers, set at login by which access code the visitor used (see auth.py):

- Sponsored sessions (owner, close collaborators, RAs; entered with the
  SPONSOR_PASSWORD code) run on the server-side key from the
  ANTHROPIC_API_KEY secret.
- General sessions (ACCESS_PASSWORD code) bring their own key. The key
  lives only in that visitor's Streamlit session state: it is never
  written to disk, to logs, to environment variables, or to any
  server-side store.
"""

import os

import streamlit as st

_SESSION_KEY = "user_anthropic_api_key"


def _server_key() -> str:
    """The app owner's key, from env or st.secrets ('' if not configured)."""
    val = os.environ.get("ANTHROPIC_API_KEY", "")
    if not val:
        try:
            val = st.secrets.get("ANTHROPIC_API_KEY", "")
        except Exception:
            val = ""
    return val or ""


def is_sponsored() -> bool:
    """True when this session runs on the app owner's key."""
    return bool(st.session_state.get("sponsored")) and bool(_server_key())


def render_key_sidebar() -> str:
    """Render the sidebar key input (general tier) or a sponsored notice.

    Returns the key the session should use ('' if none available)."""
    if is_sponsored():
        with st.sidebar:
            st.caption("API access: covered for this session. No key needed.")
        return _server_key()

    with st.sidebar:
        st.markdown("### Your Anthropic API key")
        entered = st.text_input(
            "Anthropic API key",
            value=st.session_state.get(_SESSION_KEY, ""),
            type="password",
            placeholder="sk-ant-...",
            help=(
                "Claude-powered features run on your own key "
                "(create one at console.anthropic.com). The key is kept only "
                "in your browser session and is never stored on the server."
            ),
            label_visibility="collapsed",
        )
        entered = (entered or "").strip()
        st.session_state[_SESSION_KEY] = entered
        if entered and not entered.startswith("sk-ant-"):
            st.warning("This does not look like an Anthropic API key (they start with sk-ant-).")
    return st.session_state.get(_SESSION_KEY, "")


def get_user_api_key() -> str:
    """Return the key for the current session ('' if none available)."""
    if is_sponsored():
        return _server_key()
    return st.session_state.get(_SESSION_KEY, "")


def require_user_api_key() -> str:
    """Gate for Claude-powered pages. Sponsored sessions pass automatically;
    general sessions must provide their own key or the page stops."""
    key = render_key_sidebar()
    if not key:
        st.info(
            "This page uses Claude and runs on **your own Anthropic API key**. "
            "Paste your key in the sidebar to continue. "
            "Corpus search and the bibliography work without a key."
        )
        st.stop()
    return key
