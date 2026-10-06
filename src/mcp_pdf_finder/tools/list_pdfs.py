import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.services.pdf_service import PDFService


logger = logging.getLogger(__name__)


def register_list_pdfs_tool(
    mcp: MCPServer,
    pdf_service: PDFService,
) -> None:

    @mcp.tool("list_pdfs")
    def list_pdfs(
        user_id: str,
    ) -> list[dict]:
        """
            List PDF documents available for a user.
        
            Args:
                user_id: User whose document repository should be listed.
            Return: A list of dictionaries containing the PDF file names and sizes
         """

        logger.debug(
            "list_pdfs tool called | user_id=%s",
            user_id,
        )

        pdfs = pdf_service.list_pdfs(
            user_id=user_id,
        )

        return [
            {
                "name": pdf.name,
                "size_bytes": pdf.stat().st_size,
            }
            for pdf in pdfs
        ]