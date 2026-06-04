#!/bin/sh
set -e

echo ""
echo "[backend] API en http://localhost:8080"
echo "[backend] Swagger en http://localhost:8080/docs"
echo ""

exec uvicorn app.main:app --host 0.0.0.0 --port 8080
