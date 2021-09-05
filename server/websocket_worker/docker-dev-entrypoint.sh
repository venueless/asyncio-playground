#!/bin/bash
# Start server
echo "Starting server"
uvicorn websocket_worker.main:app --reload --host 0.0.0.0 --port 8375 --reload-dir websocket_worker
