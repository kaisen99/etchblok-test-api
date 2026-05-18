#!/usr/bin/env bash
# Dump rows from autodoc_pr_outcomes for inspection after a test run.
#
# Filters to the last 6 hours by default — change WINDOW_HOURS to widen.
# Requires AWS CLI configured with read access to the table.

set -euo pipefail

REGION="${AWS_REGION:-us-east-1}"
TABLE="autodoc_pr_outcomes"
WINDOW_HOURS="${WINDOW_HOURS:-6}"

if ! command -v aws >/dev/null 2>&1; then
    echo "ERROR: aws CLI not found in PATH." >&2
    exit 1
fi

# Cutoff in ISO 8601 — rows older than this are filtered out.
CUTOFF="$(date -u -v-"${WINDOW_HOURS}"H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null \
    || date -u -d "${WINDOW_HOURS} hours ago" +"%Y-%m-%dT%H:%M:%SZ")"

echo "Reading $TABLE (region=$REGION) rows since $CUTOFF…"
echo ""

aws dynamodb scan \
    --region "$REGION" \
    --table-name "$TABLE" \
    --filter-expression "created_at > :cutoff" \
    --expression-attribute-values "{\":cutoff\": {\"S\": \"$CUTOFF\"}}" \
    --projection-expression "pr_number, pr_url, #s, created_at, merged_at, closed_at, sections_count, pusher_login" \
    --expression-attribute-names '{"#s": "status"}' \
    --output table
