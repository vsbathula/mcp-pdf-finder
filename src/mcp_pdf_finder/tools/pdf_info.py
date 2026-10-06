import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.services.pdf_service import PDFService


logger = logging.getLogger(__name__)


def register_pdf_info_tool(
    mcp: MCPServer,
    pdf_service: PDFService,
) -> None:

    @mcp.tool("pdf_info")
    def pdf_info(
        user_id: str,
        filename: str,
    ) -> dict:
        """
            Get metadata about a PDF document.
        
            Args:
                user_id: User whose document repository contains the PDF.
                filename: Name of the PDF document.
            Return: A dictionary containing the PDF's metadata and information
        """

        logger.debug(
            "pdf_info tool called | "
            "user_id=%s filename=%s",
            user_id,
            filename,
        )

        return pdf_service.get_pdf_info(
            user_id=user_id,
            filename=filename,
        )