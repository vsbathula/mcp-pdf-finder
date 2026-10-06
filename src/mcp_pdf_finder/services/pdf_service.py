import logging
from pathlib import Path

from pypdf import PdfReader

from mcp_pdf_finder.config import Settings

from typing import TypedDict


class PDFSearchMatch(TypedDict):
    page: int
    snippet: str
    
class PDFSearchResult(TypedDict):
    filename: str
    page: int
    snippet: str

logger = logging.getLogger(__name__)


class PDFService:

    def __init__(self, settings: Settings):
        self.settings = settings

    def _get_user_directory(
        self,
        user_id: str,
    ) -> Path:
        """
        Resolve a user's document directory safely.

        The resolved directory must remain inside
        DOCUMENTS_DIR.
        Args:
            user_id: the ID of the user
        Return: the resolved Path object for the user's document directory
        """

        user_id = user_id.strip()
        logger.info(f"Resolving user document directory for user_id={user_id}")

        if not user_id:
            logger.error(f"Invalid user_id provided: {user_id}")
            raise ValueError(
                "user_id cannot be empty"
            )

        documents_root = (
            self.settings.documents_dir.resolve()
        )
        logger.info(f"Documents root directory: {documents_root}")

        user_directory = (
            documents_root / user_id
        ).resolve()
        logger.info(f"Resolved user directory: {user_directory}")
        
        if not user_directory.is_relative_to(
            documents_root
        ):
            logger.warning(
                "Blocked invalid user directory | "
                "user_id=%s resolved=%s",
                user_id,
                user_directory,
            )

            raise ValueError(
                "Invalid user_id"
            )

        if not user_directory.exists():
            logger.error(
                "User document directory does not exist | "
                "user_id=%s resolved=%s",
                user_id,
                user_directory,
            )
            raise FileNotFoundError(
                f"User document directory "
                f"does not exist: {user_id}"
            )

        if not user_directory.is_dir():
            logger.error(
                "User document path is not a directory | "
                "user_id=%s resolved=%s",
                user_id,
                user_directory,
            )
            raise NotADirectoryError(
                f"User document path is not "
                f"a directory: {user_id}"
            )

        return user_directory
    
    def _get_pdf_path(
        self,
        user_id: str,
        filename: str,
    ) -> Path:
        """
        Resolve a PDF file path for a user safely.
        
        Args:
            user_id: the ID of the user
            filename: the name of the PDF file
        Return: the resolved Path object for the PDF file
        """
        
        logger.info(
            f"Resolving PDF path for user_id={user_id} filename={filename}"
        )
        filename = filename.strip()

        if not filename:
            raise ValueError(
                "filename cannot be empty"
            )

        user_directory = self._get_user_directory(
            user_id
        )

        pdf_path = (
            user_directory / filename
        ).resolve()

        # Security boundary:
        # file must remain inside this user's directory.
        if not pdf_path.is_relative_to(
            user_directory
        ):
            logger.warning(
                "Blocked invalid PDF path | "
                "user_id=%s filename=%s resolved=%s",
                user_id,
                filename,
                pdf_path,
            )

            raise ValueError(
                "Invalid PDF filename"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                "Only PDF files are supported"
            )

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF does not exist: {filename}"
            )

        if not pdf_path.is_file():
            raise ValueError(
                f"PDF path is not a file: {filename}"
            )

        return pdf_path
    
    def _create_search_snippet(
        self,
        text: str,
        query: str,
        context_chars: int = 150,
    ) -> str:
        """
        Create a snippet of text around the first occurrence of the query.
        Args:
            text: the full text to search within
            query: the search query string
            context_chars: number of characters to include before and after the match   
        Return: a snippet of text containing the query and surrounding context
        """
        text_lower = text.lower()
        query_lower = query.lower()

        match_index = text_lower.find(
            query_lower
        )

        if match_index == -1:
            return ""

        start = max(
            0,
            match_index - context_chars,
        )

        end = min(
            len(text),
            match_index
            + len(query)
            + context_chars,
        )

        snippet = text[start:end].strip()

        if start > 0:
            snippet = "..." + snippet

        if end < len(text):
            snippet = snippet + "..."

        return snippet
    
    def list_pdfs(
        self,
        user_id: str,
    ) -> list[Path]:
        """
        List PDF documents available for a user.
        
        Args:
            user_id: the ID of the user
        Return: a list of Path objects for the available PDF files
        """
        
        user_directory = (
            self._get_user_directory(user_id)
        )

        logger.debug(
            "Listing PDFs | user_id=%s directory=%s",
            user_id,
            user_directory,
        )

        pdfs = sorted(
            path
            for path in user_directory.iterdir()
            if path.is_file()
            and path.suffix.lower() == ".pdf"
        )

        logger.debug(
            "Found PDFs | user_id=%s count=%d",
            user_id,
            len(pdfs),
        )

        return pdfs
    
    def get_pdf_info(
    self,
    user_id: str,
    filename: str,
    ) -> dict:
        """
        Get metadata and information about a PDF document for a user.
        
        Args:
            user_id: the ID of the user
            filename: the name of the PDF file
        Return: a dictionary containing the PDF's metadata and information
        """
        
        pdf_path = self._get_pdf_path(
            user_id=user_id,
            filename=filename,
        )

        file_size = pdf_path.stat().st_size

        if file_size > self.settings.max_pdf_size:
            logger.warning(
                "PDF exceeds maximum size | "
                "user_id=%s filename=%s "
                "size=%d limit=%d",
                user_id,
                filename,
                file_size,
                self.settings.max_pdf_size,
            )

            raise ValueError(
                "PDF exceeds maximum allowed size"
            )

        logger.debug(
            "Reading PDF metadata | "
            "user_id=%s filename=%s",
            user_id,
            filename,
        )

        reader = PdfReader(pdf_path)

        metadata = reader.metadata

        result = {
            "name": pdf_path.name,
            "size_bytes": file_size,
            "page_count": len(reader.pages),
            "title": (
                metadata.title
                if metadata
                else None
            ),
            "author": (
                metadata.author
                if metadata
                else None
            ),
        }

        logger.debug(
            "PDF metadata loaded | "
            "user_id=%s filename=%s pages=%d",
            user_id,
            filename,
            len(reader.pages),
        )

        return result
    
    def read_pdf_page(
        self,
        user_id: str,
        filename: str,
        page: int,
    ) -> dict:
        """
        Read text content from a specific page of a PDF document for a user.
        Args:
            user_id: the ID of the user
            filename: the name of the PDF file
            page: the page number to read (1-based index)  
        Return: a dictionary containing the PDF's page content and metadata
        """

        pdf_path = self._get_pdf_path(
            user_id=user_id,
            filename=filename,
        )

        file_size = pdf_path.stat().st_size

        if file_size > self.settings.max_pdf_size:
            raise ValueError(
                "PDF exceeds maximum allowed size"
            )

        reader = PdfReader(pdf_path)

        total_pages = len(reader.pages)

        if page < 1 or page > total_pages:
            raise ValueError(
                f"Invalid page number. "
                f"PDF contains {total_pages} pages."
            )

        logger.debug(
            "Reading PDF page | "
            "user_id=%s filename=%s page=%d",
            user_id,
            filename,
            page,
        )

        pdf_page = reader.pages[page - 1]

        text = pdf_page.extract_text() or ""

        return {
            "filename": pdf_path.name,
            "page": page,
            "total_pages": total_pages,
            "text": text.strip(),
        }
        
    def search_pdf(
        self,
        user_id: str,
        filename: str,
        query: str,
    ) -> list[PDFSearchMatch]:
        """
        Search for a query string in a PDF document for a user.
        Args:
            user_id: the ID of the user
            filename: the name of the PDF file
            query: the search query string  
        Return: a list of dictionaries containing the page number and text of matching pages
        """
        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty"
            )

        pdf_path = self._get_pdf_path(
            user_id=user_id,
            filename=filename,
        )

        file_size = pdf_path.stat().st_size

        if file_size > self.settings.max_pdf_size:
            raise ValueError(
                "PDF exceeds maximum allowed size"
            )

        logger.debug(
            "Searching PDF | "
            "user_id=%s filename=%s query=%s",
            user_id,
            filename,
            query,
        )

        reader = PdfReader(pdf_path)

        results: list[PDFSearchMatch] = []

        query_lower = query.lower()

        for page_number, page in enumerate(
            reader.pages,
            start=1,
        ):

            text = page.extract_text() or ""

            if query_lower not in text.lower():
                continue
            
            snippet = self._create_search_snippet(
                text=text,
                query=query,
            )
            
            results.append(
                {
                    "page": page_number,
                    "snippet": snippet,
                }
            )

            if (
                len(results)
                >= self.settings.max_search_results
            ):
                break

        logger.debug(
            "PDF search completed | "
            "user_id=%s filename=%s "
            "query=%s matches=%d",
            user_id,
            filename,
            query,
            len(results),
        )

        return results
    
    def search_all_pdfs(
        self,
        user_id: str,
        query: str,
    ) -> list[PDFSearchResult]:
        """
        Search for a query string across all PDF documents for a user.
        Args:
            user_id: the ID of the user
            query: the search query string  
        Return: a list of dictionaries containing the filename, page number, and text snippet of matching pages
        """
        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty"
            )

        logger.debug(
            "Searching all PDFs | "
            "user_id=%s query=%s",
            user_id,
            query,
        )

        pdfs = self.list_pdfs(
            user_id=user_id,
        )

        results: list[PDFSearchResult] = []

        for pdf_path in pdfs:

            matches = self.search_pdf(
                user_id=user_id,
                filename=pdf_path.name,
                query=query,
            )

            for match in matches:

                results.append(
                    {
                        "filename": pdf_path.name,
                        "page": match["page"],
                        "snippet": match["snippet"],
                    }
                )

                if (
                    len(results)
                    >= self.settings.max_search_results
                ):
                    logger.debug(
                        "Maximum search results reached | "
                        "limit=%d",
                        self.settings.max_search_results,
                    )

                    return results

        logger.debug(
            "Search all PDFs completed | "
            "user_id=%s query=%s matches=%d",
            user_id,
            query,
            len(results),
        )

        return results