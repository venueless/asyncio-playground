#!/bin/bash
# Start server
echo "Starting server"
uvicorn world_server.main:app --reload --port 8080
