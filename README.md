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

- `ANTHROPIC_API_KEY` -- Anthropic API key
- `ACCESS_PASSWORD` -- Access code shared with collaborators
