#!/bin/bash

set -e

# Parse inputs
GITHUB_TOKEN="${INPUT_GITHUB_TOKEN}"
REPO_NAME="${INPUT_REPO_NAME:-${GITHUB_REPOSITORY}}"
REPO_PATH="${INPUT_REPO_PATH:-./}"
CLOSE_RESOLVED="${INPUT_CLOSE_RESOLVED:-false}"
IGNORE_DIRS="${INPUT_IGNORE_DIRS:-}"
IGNORE_PATTERNS="${INPUT_IGNORE_PATTERNS:-}"
DRY_RUN="${INPUT_DRY_RUN:-false}"

# Build command arguments
CMD_ARGS=()
CMD_ARGS+=("--github-token" "${GITHUB_TOKEN}")
CMD_ARGS+=("--repo-name" "${REPO_NAME}")
CMD_ARGS+=("--repo-path" "${REPO_PATH}")

if [ "${DRY_RUN}" = "true" ]; then
    CMD_ARGS+=("--dry-run")
fi

if [ "${CLOSE_RESOLVED}" = "true" ]; then
    CMD_ARGS+=("--close-resolved")
fi

# Parse comma-separated ignore dirs
if [ -n "${IGNORE_DIRS}" ]; then
    IFS=',' read -ra DIRS <<< "${IGNORE_DIRS}"
    for dir in "${DIRS[@]}"; do
        CMD_ARGS+=("--ignore-dirs" "${dir// /}")
    done
fi

# Parse comma-separated ignore patterns
if [ -n "${IGNORE_PATTERNS}" ]; then
    IFS=',' read -ra PATTERNS <<< "${IGNORE_PATTERNS}"
    for pattern in "${PATTERNS[@]}"; do
        CMD_ARGS+=("--ignore-patterns" "${pattern// /}")
    done
fi

echo "Running TODO Tracker with arguments: ${CMD_ARGS[*]}"

# Run the todo tracker and capture output
OUTPUT_FILE="/tmp/todo_output.txt"
todo-tracker track "${CMD_ARGS[@]}" --verbose 2>&1 | tee "${OUTPUT_FILE}"

# Parse output to set GitHub Action outputs
TODOS_FOUND=$(grep -oP "Total TODOs found: \K\d+" "${OUTPUT_FILE}" || echo "0")
ISSUES_CREATED=$(grep -oP "Created \K\d+" "${OUTPUT_FILE}" || echo "0")
ISSUES_SKIPPED=$(grep -oP "Skipped \K\d+" "${OUTPUT_FILE}" || echo "0")
ISSUES_CLOSED=$(grep -oP "Closed \K\d+" "${OUTPUT_FILE}" || echo "0")

# Set outputs
echo "todos-found=${TODOS_FOUND}" >> "$GITHUB_OUTPUT"
echo "issues-created=${ISSUES_CREATED}" >> "$GITHUB_OUTPUT"
echo "issues-skipped=${ISSUES_SKIPPED}" >> "$GITHUB_OUTPUT"
echo "issues-closed=${ISSUES_CLOSED}" >> "$GITHUB_OUTPUT"

echo "TODO Tracker completed successfully!"
