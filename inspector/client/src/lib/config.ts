/**
 * MCP Inspector configuration
 */

// Default server connection for Qdrant MCP server
// User will connect to this URL through the Inspector proxy at port 3000
export const DEFAULT_MCP_SERVER_URL = "http://qdrant-mcp-server:8000/sse";

// Default connection options
export const DEFAULT_CONNECTION_OPTIONS = {
  transportType: "sse",
  url: DEFAULT_MCP_SERVER_URL,
};

// Additional configuration specific to Docker environment
export const DOCKER_CONFIG = {
  // Define network connection details
  qdrantServer: "http://qdrant-database:6333",
  qdrantMcpServer: "http://qdrant-mcp-server:8000",
  inspectorProxyServer: "http://localhost:3000",
  inspectorClientUrl: "http://localhost:5173",
};