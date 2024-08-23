#!/bin/bash

POSITIONAL_ARGS=()
QUERIES="1000"
RUNS="10"
WARMUP="10"
OUTPUT="results.json"


while [[ $# -gt 0 ]]; do
  case $1 in
    -q|--queries)
      QUERIES="$2"
      shift; shift
      ;;
    -r|--runs)
      RUNS="$2"
      shift; shift
      ;;
    -w|--warmup)
      WARMUP="$2"
      shift; shift
      ;;
    -o|--output)
      OUTPUT="$2"
      shift; shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

if [[ -z "$1" ]]; then
  echo "Error: interpreter must be specified"
  exit 1
fi

INTERPRETER="$1"

hyperfine \
  --warmup "$WARMUP" \
  --runs "$RUNS" \
  --export-json "$OUTPUT" \
  "$INTERPRETER benchmark.py threads-recreate -r $QUERIES" \
  "$INTERPRETER benchmark.py threads-reuse -r $QUERIES" \
  "$INTERPRETER benchmark.py threads-map -r $QUERIES" \
  "$INTERPRETER benchmark.py async-for -r $QUERIES" \
  "$INTERPRETER benchmark.py async-map -r $QUERIES"
