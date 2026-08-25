import os
import logging
from mcp.client.streamable_http import streamable_http_client
from mcp_proxy_for_aws.client import aws_iam_streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient

logger = logging.getLogger(__name__)

# ExaAI provides information about code through web searches, crawling and code context searches through their platform. Requires no authentication
EXAMPLE_MCP_ENDPOINT = "https://mcp.exa.ai/mcp"

GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

def get_streamable_http_mcp_client() -> MCPClient:
    """Returns an MCP Client compatible with Strands"""
    # to use an MCP server that supports bearer authentication, add headers={"Authorization": f"Bearer {access_token}"}
    return MCPClient(lambda: streamable_http_client(EXAMPLE_MCP_ENDPOINT))

def get_gateway_mcp_client() -> MCPClient | None:
    """Returns a SigV4-authenticated MCP client pointing at the AgentCore Gateway."""
    if not GATEWAY_URL:
        logger.warning("AGENTCORE_GATEWAY_URL not set — gateway MCP client disabled")
        return None
    return MCPClient(lambda: aws_iam_streamablehttp_client(
        endpoint=GATEWAY_URL,
        aws_region=AWS_REGION,
        aws_service="bedrock-agentcore",
    ))
