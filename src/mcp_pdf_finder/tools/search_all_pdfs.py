import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.services.pdf_service import PDFService


logger = logging.getLogger(__name__)


def register_search_all_pdfs_tool(
    mcp: MCPServer,
    pdf_service: PDFService,
) -> None:

    @mcp.tool()
    def search_all_pdfs(
        user_id: str,
        query: str,
    ) -> list[dict]:
        """
        Search for text across all PDFs belonging to a user.

        Args:
            user_id:
                User whose PDF repository should be searched.

            query:
                Text to search for.
        Return: A list of dictionaries containing the filename, page number, and text snippet of matching pages
        """

        logger.debug(
            "search_all_pdfs tool called | "
            "user_id=%s query=%s",
            user_id,
            query,
        )

        return pdf_service.search_all_pdfs(
            user_id=user_id,
            query=query,
        )