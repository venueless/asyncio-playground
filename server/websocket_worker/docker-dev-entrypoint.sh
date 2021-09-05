#!/bin/bash
# Start server
echo "Starting server"
uvicorn websocket_worker.main:app --reload --port 8375
