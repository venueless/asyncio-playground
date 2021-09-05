#!/bin/bash
# Start server
echo "Starting server"
uvicorn world_server.main:app --reload --host 0.0.0.0 --port 8375 --reload-dir world_server
