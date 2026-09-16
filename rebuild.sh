#!/bin/bash
docker compose down -v
docker builder prune -af
docker compose build --no-cache --build-arg CACHE_BUST="$(date +%s)"
docker compose up -d
