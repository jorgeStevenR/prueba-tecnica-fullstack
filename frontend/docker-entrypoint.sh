#!/bin/sh
set -e

echo ""
echo "[frontend] App en http://localhost:3000"
echo ""

exec npm run preview
