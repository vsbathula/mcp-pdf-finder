import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.services.pdf_service import PDFService


logger = logging.getLogger(__name__)


def register_read_pdf_tool(
    mcp: MCPServer,
    pdf_service: PDFService,
) -> None:

    @mcp.tool()
    def read_pdf(
        user_id: str,
        filename: str,
        page: int,
    ) -> dict:
        """
        Read text from a specific page of a PDF.

        Args:
            user_id:
                User whose document repository
                contains the PDF.

            filename:
                Name of the PDF document.

            page:
                Page number to read.
                Page numbering starts at 1.
        """

        logger.debug(
            "read_pdf tool called | "
            "user_id=%s filename=%s page=%d",
            user_id,
            filename,
            page,
        )

        return pdf_service.read_pdf_page(
            user_id=user_id,
            filename=filename,
            page=page,
        )