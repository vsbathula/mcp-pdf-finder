import logging

from mcp.server.mcpserver import MCPServer

from mcp_pdf_finder.config import settings
from mcp_pdf_finder.logging_config import setup_logging
from mcp_pdf_finder.services.pdf_service import PDFService
from mcp_pdf_finder.tools.list_pdfs import register_list_pdfs_tool
from mcp_pdf_finder.tools.pdf_info import register_pdf_info_tool
from mcp_pdf_finder.tools.read_pdf import register_read_pdf_tool
from mcp_pdf_finder.tools.search_pdf import register_search_pdf_tool
from mcp_pdf_finder.tools.search_all_pdfs import register_search_all_pdfs_tool

setup_logging()

logger = logging.getLogger(__name__)


def create_server() -> MCPServer:

    mcp = MCPServer("MCP PDF Finder")

    pdf_service = PDFService(settings)

    register_list_pdfs_tool(
        mcp=mcp,
        pdf_service=pdf_service,
    )

    register_pdf_info_tool(
        mcp=mcp,
        pdf_service=pdf_service,
    )
    
    register_read_pdf_tool(
        mcp=mcp,
        pdf_service=pdf_service,
    )
    
    register_search_pdf_tool(
        mcp=mcp,
        pdf_service=pdf_service,
    )
    
    register_search_all_pdfs_tool(
        mcp=mcp,
        pdf_service=pdf_service,
    )

    return mcp


mcp = create_server()


# ---------------------------------------------------------
# Start Server
# ---------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting PDF Content Finder MCP server")
    mcp.run()