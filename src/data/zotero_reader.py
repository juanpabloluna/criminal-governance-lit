"""Zotero database reader for extracting library metadata."""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any

from loguru import logger

from src.config.settings import settings
from src.data.models import ZoteroItem


class ZoteroReader:
    """Reader for Zotero SQLite database."""

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the Zotero reader.

        Args:
            db_path: Path to Zotero SQLite database. If None, uses settings.
        """
        self.db_path = db_path or settings.zotero_db_path
        self.storage_path = settings.zotero_storage_path

        if not self.db_path.exists():
            raise FileNotFoundError(f"Zotero database not found: {self.db_path}")

        logger.info(f"Initialized ZoteroReader with database: {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """Get a read-only connection to the Zotero database."""
        # Open in read-only mode to prevent accidental modifications
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def get_collections(self) -> List[Dict[str, Any]]:
        """Get all collections from Zotero library."""
        query = """
        SELECT
            collectionID,
            collectionName,
            parentCollectionID
        FROM collections
        ORDER BY collectionName
        """

        with self.get_connection() as conn:
            cursor = conn.execute(query)
            collections = [dict(row) for row in cursor.fetchall()]

        logger.info(f"Found {len(collections)} collections in Zotero library")
        return collections

    def get_items_with_pdfs(
        self, collection_names: Optional[List[str]] = None
    ) -> List[ZoteroItem]:
        """
        Get all items that have PDF attachments.

        Args:
            collection_names: Optional list of collection names to filter by.
                             If None, returns all items with PDFs.

        Returns:
            List of ZoteroItem objects with metadata.
        """
        # Base query to get items with PDFs
        query = """
        WITH item_fields AS (
            SELECT
                i.itemID,
                i.key,
                i.dateAdded,
                i.dateModified,
                f.fieldName,
                idv.value
            FROM items i
            LEFT JOIN itemData id ON i.itemID = id.itemID
            LEFT JOIN fields f ON id.fieldID = f.fieldID
            LEFT JOIN itemDataValues idv ON id.valueID = idv.valueID
            WHERE i.itemID IN (
                SELECT DISTINCT parentItemID
                FROM itemAttachments
                WHERE contentType = 'application/pdf'
                AND path IS NOT NULL
            )
        ),
        item_creators AS (
            SELECT
                i.itemID,
                GROUP_CONCAT(
                    CASE
                        WHEN c.firstName IS NOT NULL AND c.lastName IS NOT NULL
                        THEN c.firstName || ' ' || c.lastName
                        WHEN c.lastName IS NOT NULL
                        THEN c.lastName
                        ELSE c.firstName
                    END,
                    '; '
                ) as authors
            FROM items i
            JOIN itemCreators ic ON i.itemID = ic.itemID
            JOIN creators c ON ic.creatorID = c.creatorID
            GROUP BY i.itemID
        ),
        item_collections AS (
            SELECT
                ci.itemID,
                GROUP_CONCAT(col.collectionName, '; ') as collections
            FROM collectionItems ci
            JOIN collections col ON ci.collectionID = col.collectionID
            GROUP BY ci.itemID
        ),
        item_tags AS (
            SELECT
                it.itemID,
                GROUP_CONCAT(t.name, '; ') as tags
            FROM itemTags it
            JOIN tags t ON it.tagID = t.tagID
            GROUP BY it.itemID
        ),
        item_attachments AS (
            SELECT
                ia.parentItemID as itemID,
                ia.path as pdf_path,
                ia.itemID as attachment_id,
                i.key as attachment_key
            FROM itemAttachments ia
            JOIN items i ON ia.itemID = i.itemID
            WHERE ia.contentType = 'application/pdf'
            AND ia.path IS NOT NULL
        )
        SELECT DISTINCT
            if.itemID,
            if.key as zotero_key,
            if.dateAdded,
            if.dateModified,
            MAX(CASE WHEN if.fieldName = 'title' THEN if.value END) as title,
            MAX(CASE WHEN if.fieldName = 'abstractNote' THEN if.value END) as abstract,
            MAX(CASE WHEN if.fieldName = 'publicationTitle' THEN if.value END) as publication,
            MAX(CASE WHEN if.fieldName = 'date' THEN if.value END) as date,
            MAX(CASE WHEN if.fieldName = 'DOI' THEN if.value END) as doi,
            MAX(CASE WHEN if.fieldName = 'url' THEN if.value END) as url,
            ic.authors,
            icol.collections,
            it.tags,
            ia.pdf_path,
            ia.attachment_key
        FROM item_fields if
        LEFT JOIN item_creators ic ON if.itemID = ic.itemID
        LEFT JOIN item_collections icol ON if.itemID = icol.itemID
        LEFT JOIN item_tags it ON if.itemID = it.itemID
        LEFT JOIN item_attachments ia ON if.itemID = ia.itemID
        WHERE ia.pdf_path IS NOT NULL
        """

        # Add collection filter if specified
        if collection_names:
            collection_filter = "' OR icol.collections LIKE '%".join(collection_names)
            query += f" AND (icol.collections LIKE '%{collection_filter}%')"

        query += " GROUP BY if.itemID, if.key, if.dateAdded, if.dateModified, ic.authors, icol.collections, it.tags, ia.pdf_path, ia.attachment_key"

        with self.get_connection() as conn:
            cursor = conn.execute(query)
            rows = cursor.fetchall()

        items = []
        for row in rows:
            # Convert Row to dict for easier access
            row_dict = dict(row)

            # Resolve PDF path
            pdf_path = self._resolve_pdf_path(row_dict["pdf_path"], row_dict.get("attachment_key"))

            # Parse authors
            authors = (
                [a.strip() for a in row_dict["authors"].split(";")]
                if row_dict["authors"]
                else []
            )

            # Parse collections
            collections = (
                [c.strip() for c in row_dict["collections"].split(";")]
                if row_dict["collections"]
                else []
            )

            # Parse tags
            tags = (
                [t.strip() for t in row_dict["tags"].split(";")] if row_dict["tags"] else []
            )

            # Extract year from date
            year = self._extract_year(row_dict.get("date"))

            item = ZoteroItem(
                item_id=row_dict["itemID"],
                zotero_key=row_dict["zotero_key"],
                title=row_dict["title"] or "Untitled",
                authors=authors,
                year=year,
                abstract=row_dict.get("abstract"),
                publication=row_dict.get("publication"),
                doi=row_dict.get("doi"),
                url=row_dict.get("url"),
                collections=collections,
                tags=tags,
                pdf_path=str(pdf_path) if pdf_path else None,
                date_added=row_dict.get("dateAdded"),
                date_modified=row_dict.get("dateModified"),
            )
            items.append(item)

        logger.info(
            f"Retrieved {len(items)} items with PDFs"
            + (f" from collections: {collection_names}" if collection_names else "")
        )
        return items

    def _resolve_pdf_path(self, zotero_path: Optional[str], attachment_key: Optional[str] = None) -> Optional[Path]:
        """
        Resolve Zotero's internal path format to absolute path.

        Zotero stores paths in format: "storage:filename.pdf"
        The actual location is: /Users/jpl/Zotero/storage/{attachment_key}/filename.pdf
        where attachment_key is the key from the items table for the attachment.
        """
        if not zotero_path:
            return None

        if zotero_path.startswith("storage:"):
            # Remove "storage:" prefix to get filename
            filename = zotero_path[8:]

            # Use attachment_key to construct full path
            if attachment_key:
                full_path = self.storage_path / attachment_key / filename
                if full_path.exists():
                    return full_path
                else:
                    logger.warning(f"PDF file not found: {full_path}")
                    return None
            else:
                logger.warning(f"No attachment key provided for: {zotero_path}")
                return None
        elif zotero_path.startswith("attachments:"):
            # Handle attachments: prefix
            filename = zotero_path[12:]
            if attachment_key:
                full_path = self.storage_path.parent / "attachments" / attachment_key / filename
                if full_path.exists():
                    return full_path
            logger.warning(f"PDF file not found for attachments: {zotero_path}")
            return None
        else:
            # Assume it's already a full path
            full_path = Path(zotero_path)
            if full_path.exists():
                return full_path
            else:
                logger.warning(f"PDF file not found: {full_path}")
                return None

    def _extract_year(self, date_string: Optional[str]) -> Optional[int]:
        """Extract year from Zotero date field."""
        if not date_string:
            return None

        import re

        # Try to find a 4-digit year
        match = re.search(r"\b(19|20)\d{2}\b", date_string)
        if match:
            return int(match.group())

        return None

    def get_item_by_id(self, item_id: int) -> Optional[ZoteroItem]:
        """Get a specific item by its ID."""
        items = self.get_items_with_pdfs()
        for item in items:
            if item.item_id == item_id:
                return item
        return None

    def get_library_stats(self) -> Dict[str, int]:
        """Get statistics about the Zotero library."""
        with self.get_connection() as conn:
            # Total items
            total_items = conn.execute(
                "SELECT COUNT(*) FROM items WHERE itemTypeID NOT IN (SELECT itemTypeID FROM itemTypes WHERE typeName = 'attachment')"
            ).fetchone()[0]

            # Items with PDFs
            items_with_pdfs = conn.execute(
                """
                SELECT COUNT(DISTINCT parentItemID)
                FROM itemAttachments
                WHERE contentType = 'application/pdf' AND path IS NOT NULL
                """
            ).fetchone()[0]

            # Total PDFs
            total_pdfs = conn.execute(
                """
                SELECT COUNT(*)
                FROM itemAttachments
                WHERE contentType = 'application/pdf' AND path IS NOT NULL
                """
            ).fetchone()[0]

            # Collections
            total_collections = conn.execute(
                "SELECT COUNT(*) FROM collections"
            ).fetchone()[0]

        stats = {
            "total_items": total_items,
            "items_with_pdfs": items_with_pdfs,
            "total_pdfs": total_pdfs,
            "total_collections": total_collections,
        }

        logger.info(f"Library stats: {stats}")
        return stats
