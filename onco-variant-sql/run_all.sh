#!/usr/bin/env bash
# Rebuild everything from scratch: data -> database -> analysis results.
set -euo pipefail
cd "$(dirname "$0")"

python3 scripts/generate_data.py data
rm -f onco.db
sqlite3 onco.db < sql/00_schema.sql
sqlite3 onco.db < sql/01_load.sql

mkdir -p results
for f in sql/0[2-8]_*.sql; do
    out="results/$(basename "$f" .sql).txt"
    sqlite3 -header -column -echo onco.db < "$f" > "$out"
    echo "ran $f -> $out"
done
