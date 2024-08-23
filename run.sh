#!/bin/bash

hyperfine \
  --warmup 3 \
  --runs 100 \
  --export-json "results.json" \
  '.venv/bin/python benchmark.py threads-recreate -r 1000' \
  '.venv/bin/python benchmark.py threads-reuse -r 1000' \
  '.venv/bin/python benchmark.py threads-map -r 1000' \
  '.venv/bin/python benchmark.py async-for -r 1000' \
  '.venv/bin/python benchmark.py async-map -r 1000'
