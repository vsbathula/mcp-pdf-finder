import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.services.pdf_service import (
    PDFService,
)


logger = logging.getLogger(__name__)


def register_search_pdf_tool(
    mcp: MCPServer,
    pdf_service: PDFService,
) -> None:

    @mcp.tool()
    def search_pdf(
        user_id: str,
        filename: str,
        query: str,
    ) -> list[dict]:
        """
        Search for text inside a PDF document.

        Returns matching page numbers and
        surrounding text snippets.

        Args:
            user_id:
                User whose repository contains
                the PDF.

            filename:
                Name of the PDF document.

            query:
                Text to search for.
        Return: A list of dictionaries containing the page number and text snippet
        """

        logger.debug(
            "search_pdf tool called | "
            "user_id=%s filename=%s query=%s",
            user_id,
            filename,
            query,
        )

        return pdf_service.search_pdf(
            user_id=user_id,
            filename=filename,
            query=query,
        )