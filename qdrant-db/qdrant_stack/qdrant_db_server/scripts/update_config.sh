#\!/bin/bash
# This script updates the production config file with optimized settings for LLM retrieval

CONFIG_FILE="/Users/frank/mcp_servers/qdrant-db/qdrant_stack/qdrant_db_server/config/production.yaml"

# Backup the original config
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

# Update performance settings
cat > "$CONFIG_FILE" << 'YAML'
log_level: INFO

storage:
  # Where to store all the data
  storage_path: ./storage

  # Where to store snapshots
  snapshots_path: ./snapshots

  # If true - point payloads will not be stored in memory.
  on_disk_payload: true

  performance:
    # Number of parallel threads used for search operations. If 0 - auto selection.
    max_search_threads: 0
    
    # Max number of threads for running optimizations across all collections
    max_optimization_threads: 0
    
    # CPU budget for optimization jobs
    optimizer_cpu_budget: 0

  optimizers:
    # The minimal fraction of deleted vectors in a segment, required to perform segment optimization
    deleted_threshold: 0.2
    
    # The minimal number of vectors in a segment, required to perform segment optimization
    vacuum_min_vector_number: 1000
    
    # Target amount of segments optimizer will try to keep
    default_segment_number: 0
    
    # Maximum size (in KiloBytes) of vectors allowed for plain index
    indexing_threshold_kb: 20000
    
    # Interval between forced flushes
    flush_interval_sec: 5

  # Default parameters of HNSW Index
  hnsw_index:
    # Number of edges per node in the index graph. Larger the value - more accurate the search, more space required
    m: 16
    
    # Number of neighbours to consider during the index building
    ef_construct: 100
    
    # Minimal size (in KiloBytes) of vectors for additional payload-based indexing
    full_scan_threshold_kb: 10000
    
    # Number of parallel threads used for background index building
    max_indexing_threads: 0
    
    # Store HNSW index on disk. If set to false, index will be stored in RAM
    on_disk: false

  # Default parameters for collections
  collection:
    # Default parameters for vectors
    vectors:
      # Whether vectors should be stored in memory or on disk
      on_disk: false

service:
  # Maximum size of POST data in a single request in megabytes
  max_request_size_mb: 64
  
  # Number of parallel workers used for serving the api
  max_workers: 0
  
  # Host to bind the service on
  host: 0.0.0.0
  
  # HTTP(S) port to bind the service on
  http_port: 6333
  
  # gRPC port to bind the service on
  grpc_port: 6334
  
  # Enable CORS headers in REST API
  enable_cors: true

# Set to true to prevent service from sending usage statistics to the developers
telemetry_disabled: false
YAML

echo "Configuration updated with optimized settings for LLM retrieval"
