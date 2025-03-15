FROM python:3.11-slim

WORKDIR /app

# Install debugging tools and curl for healthcheck and uv for package management
RUN apt-get update && apt-get install -y curl procps net-tools && apt-get clean
RUN pip install --no-cache-dir uv

# Copy source code
COPY . .

# Install the mcp-server-qdrant package in development mode
RUN uv pip install --system --no-cache-dir -e .

# Configure logging to stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=DEBUG

# Expose the default port for SSE transport
EXPOSE 8000

# Set environment variables with defaults that can be overridden at runtime
ENV QDRANT_URL="http://qdrant-database:6333"
ENV QDRANT_API_KEY=""
ENV COLLECTION_NAME="llm_documents"
ENV EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Run the server with SSE transport
CMD ["uvx", "mcp-server-qdrant", "--transport", "sse"]