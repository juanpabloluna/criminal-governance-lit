# Criminal Governance Literature Expert

RAG-based research assistant for organized crime, violence, and Latin American politics. Built on a corpus of 304 academic papers indexed via ChromaDB.

## Features

- **Question Answering** -- Traditional RAG Q&A with citations
- **Agentic Q&A** -- Claude orchestrates its own multi-step research
- **Literature Synthesis** -- Generate comprehensive literature reviews
- **Research Review** -- Analyze drafts against the literature corpus

## Deployment

Deployed via [Streamlit Community Cloud](https://share.streamlit.io). Password-protected.

### Secrets required (set in Streamlit Cloud dashboard)

- `ACCESS_PASSWORD` -- General access code. Visitors who enter with it bring
  their own Anthropic API key (sidebar field; kept only in their browser
  session, never stored on the server).
- `SPONSOR_PASSWORD` -- Privileged access code for the owner, close
  collaborators, and RAs. Sessions opened with it run on the server-side
  `ANTHROPIC_API_KEY` (the owner pays).
- `ANTHROPIC_API_KEY` -- The owner's key; used only by sponsored sessions.
- `ADMIN_PASSWORD` -- Unlocks the usage-log page.

Corpus search and the bibliography work without any API key.
