#!/bin/bash

function usage() {
    echo "Usage: ./cli [up|down]"
    exit 1
}

function func_up() {
    echo "Starting services..."
    # Build and start the container in detached mode
    docker compose -f docker-compose.yml up -d
}

function func_up_force() {
    echo "Starting services..."
    # Force rebuild and start the container in detached mode
    docker compose -f docker-compose.yml up -d --force-recreate --build
}

function func_down() {
    echo "Stopping services and cleaning up..."
    # Stop and remove containers and networks
    docker compose -f docker-compose.yml down --remove-orphans

    # Garbage Collection: Remove dangling images and containers
    echo "Performing garbage collection (pruning dangling images/containers)..."
    docker image prune --force --filter "dangling=true" 2>/dev/null || true
    docker container prune --force 2>/dev/null || true
}

# Check for arguments
if [ -z "$1" ]; then
    usage
fi

case "$1" in
    up)
        func_up
        ;;
    up-force)
        func_up_force
        ;;
    down)
        func_down
        ;;
    *)
        usage
        ;;
esac