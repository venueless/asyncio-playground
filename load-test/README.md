# Load Testing

## Run

https://github.com/grafana/k6/releases/download/v0.33.0/k6-v0.33.0-linux-amd64.tar.gz


### Server

```sh
load-test/limits.sh # bump socket limit
ulimit -n 4000000
dc up db world_server
docker-compose run -p 8375:8375 --entrypoint "gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8375 --max-requests 1200 --max-requests-jitter 200 -w 4 websocket_worker.main:app" websocket_worker
```

### Load test

```sh
limits.sh # bump socket limit
ulimit -n 4000000
WS_URL=ws://65.21.152.130:8375/ws/world/load-test/ ./k6 run flood.js
```
