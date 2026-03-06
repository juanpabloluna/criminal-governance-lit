"""
Agentic RAG Tools - Tools that Claude can use to search and explore literature.

In agentic RAG, Claude has access to tools and decides:
- What to search for
- How many results to retrieve
- Whether to refine the search
- When it has enough information to answer
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from src.embeddings.embedding_service import EmbeddingService
from src.embeddings.vector_store import VectorStore
from src.data.zotero_reader import ZoteroReader
from src.data.models import RetrievalResult
from src.config.settings import settings


class AgenticRAGTools:
    """Tools for agentic literature exploration."""

    def __init__(self):
        """Initialize the tools with access to vector store and Zotero."""
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        try:
            self.zotero_reader = ZoteroReader()
        except Exception:
            self.zotero_reader = None
            logger.warning("ZoteroReader unavailable (no Zotero DB) — paper details disabled")
        logger.info("Initialized AgenticRAGTools")

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in Anthropic's tool use format.

        Returns:
            List of tool definition dictionaries for Claude API.
        """
        return [
            {
                "name": "search_literature",
                "description": "Semantic search across the literature corpus. Returns relevant passages from academic papers on organized crime, violence, and Latin American politics. Use this to find information relevant to answering the user's question.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query - describe what information you're looking for",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results to return (default: 10, max: 50)",
                            "default": 10,
                        },
                        "collections": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional: Filter by collection names",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_paper_details",
                "description": "Get detailed metadata about a specific paper by its ID. Use this when you need more information about a paper that appeared in search results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "item_id": {
                            "type": "integer",
                            "description": "The item_id of the paper from search results",
                        }
                    },
                    "required": ["item_id"],
                },
            },
            {
                "name": "list_available_collections",
                "description": "Get a list of all available Zotero collections to filter searches. Use this if you want to see what collections are available.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "get_papers_by_year_range",
                "description": "Search for papers published within a specific year range. Useful for temporal analysis or finding recent research.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "start_year": {
                            "type": "integer",
                            "description": "Start year (inclusive)",
                        },
                        "end_year": {
                            "type": "integer",
                            "description": "End year (inclusive)",
                        },
                        "n_results": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 5,
                        },
                    },
                    "required": ["query", "start_year", "end_year"],
                },
            },
            {
                "name": "multi_query_search",
                "description": "Perform multiple searches with different queries to get comprehensive coverage of a topic. Use this when you need to understand a topic from multiple angles or ensure you're not missing important perspectives. Automatically deduplicates results.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "queries": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of 2-5 different search queries to explore the topic comprehensively",
                            "minItems": 2,
                            "maxItems": 5,
                        },
                        "n_results_per_query": {
                            "type": "integer",
                            "description": "Results per query (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["queries"],
                },
            },
        ]

    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from Claude.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result
        """
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")

        if tool_name == "search_literature":
            return self._search_literature(**tool_input)
        elif tool_name == "get_paper_details":
            return self._get_paper_details(**tool_input)
        elif tool_name == "list_available_collections":
            return self._list_collections()
        elif tool_name == "get_papers_by_year_range":
            return self._get_papers_by_year_range(**tool_input)
        elif tool_name == "multi_query_search":
            return self._multi_query_search(**tool_input)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def _search_literature(
        self,
        query: str,
        n_results: int = 10,
        collections: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Search the literature corpus."""
        try:
            # Limit n_results to reasonable bounds (increased for broader coverage)
            n_results = min(max(n_results, 1), 50)

            # Use the query_by_text method which handles collections filtering
            results = self.vector_store.query_by_text(
                query_text=query,
                embedding_service=self.embedding_service,
                n_results=n_results,
                collections=collections,
            )

            # Format results for the agent
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {
                        "text": result.chunk.text,
                        "title": result.chunk.title,
                        "authors": ", ".join(result.chunk.authors),
                        "year": result.chunk.year,
                        "item_id": result.chunk.item_id,
                        "relevance_score": result.similarity,
                        "section": result.chunk.section,
                    }
                )

            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query,
            }

        except Exception as e:
            logger.error(f"Error in search_literature: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_paper_details(self, item_id: int) -> Dict[str, Any]:
        """Get detailed metadata about a specific paper."""
        try:
            if not self.zotero_reader:
                return {"error": "Paper details not available (Zotero DB not configured)"}
            item = self.zotero_reader.get_item_by_id(item_id)

            if not item:
                return {"error": f"Paper with item_id {item_id} not found"}

            return {
                "item_id": item.item_id,
                "title": item.title,
                "authors": item.authors,
                "year": item.year,
                "abstract": item.abstract,
                "publication": item.publication,
                "doi": item.doi,
                "url": item.url,
                "collections": item.collections,
                "tags": item.tags,
            }

        except Exception as e:
            logger.error(f"Error in get_paper_details: {e}", exc_info=True)
            return {"error": str(e)}

    def _list_collections(self) -> Dict[str, Any]:
        """List all available collections."""
        try:
            if not self.zotero_reader:
                return {"error": "Collection listing not available (Zotero DB not configured)"}
            collections = self.zotero_reader.get_collections()
            return {
                "collections": [c["collectionName"] for c in collections],
                "total": len(collections),
            }
        except Exception as e:
            logger.error(f"Error in list_collections: {e}", exc_info=True)
            return {"error": str(e)}

    def _get_papers_by_year_range(
        self,
        query: str,
        start_year: int,
        end_year: int,
        n_results: int = 5,
    ) -> Dict[str, Any]:
        """Search papers within a year range."""
        try:
            # Use query_by_text with year filters
            results = self.vector_store.query_by_text(
                query_text=query,
                embedding_service=self.embedding_service,
                n_results=n_results,
                min_year=start_year,
                max_year=end_year,
            )

            # Format results
            formatted_results = []
            for result in results[:n_results]:
                formatted_results.append(
                    {
                        "text": result.chunk.text,
                        "title": result.chunk.title,
                        "authors": ", ".join(result.chunk.authors),
                        "year": result.chunk.year,
                        "item_id": result.chunk.item_id,
                        "relevance_score": result.similarity,
                    }
                )

            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query,
                "year_range": f"{start_year}-{end_year}",
            }

        except Exception as e:
            logger.error(f"Error in get_papers_by_year_range: {e}", exc_info=True)
            return {"error": str(e)}

    def _multi_query_search(
        self,
        queries: List[str],
        n_results_per_query: int = 10,
    ) -> Dict[str, Any]:
        """
        Perform multiple searches and combine results.

        This gives comprehensive coverage by searching from multiple angles.
        Deduplicates results based on chunk_id.
        """
        try:
            all_results = []
            seen_chunk_ids = set()
            queries_executed = []

            for query in queries:
                # Search for this query
                results = self.vector_store.query_by_text(
                    query_text=query,
                    embedding_service=self.embedding_service,
                    n_results=n_results_per_query,
                )

                queries_executed.append(query)

                # Add unique results
                for result in results:
                    chunk_id = result.chunk.chunk_id
                    if chunk_id not in seen_chunk_ids:
                        seen_chunk_ids.add(chunk_id)
                        all_results.append(result)

            # Format results
            formatted_results = []
            for result in all_results:
                formatted_results.append(
                    {
                        "text": result.chunk.text,
                        "title": result.chunk.title,
                        "authors": ", ".join(result.chunk.authors),
                        "year": result.chunk.year,
                        "item_id": result.chunk.item_id,
                        "relevance_score": result.similarity,
                        "section": result.chunk.section,
                    }
                )

            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "queries_executed": queries_executed,
                "unique_chunks": len(seen_chunk_ids),
                "summary": f"Searched {len(queries)} queries, found {len(formatted_results)} unique chunks from {len(set(r['item_id'] for r in formatted_results))} papers",
            }

        except Exception as e:
            logger.error(f"Error in multi_query_search: {e}", exc_info=True)
            return {"error": str(e)}
