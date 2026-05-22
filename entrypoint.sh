#!/bin/bash
# This script runs before the garmin-mcp server starts.
# It writes Garmin OAuth tokens from Railway environment variables
# to the correct location on disk, so the server can skip authentication.
 
TOKEN_DIR="/root/.garminconnect"
mkdir -p "$TOKEN_DIR"
 
WROTE_TOKENS=0
 
# Loop through all env vars starting with GARMIN_TOKEN_
for var in $(env | grep "^GARMIN_TOKEN_" | cut -d= -f1); do
    value="${!var}"
 
    # Convert env var name back to filename
    # e.g. GARMIN_TOKEN_OAUTH1_TOKEN_JSON -> oauth1_token.json
    filename=$(echo "$var" \
        | sed 's/^GARMIN_TOKEN_//' \
        | tr '[:upper:]' '[:lower:]' \
        | sed 's/_json$/.json/' \
        | sed 's/__/-/g')
 
    filepath="$TOKEN_DIR/$filename"
    echo "$value" > "$filepath"
    echo "✓ Written token file: $filepath"
    WROTE_TOKENS=1
done
 
if [ "$WROTE_TOKENS" -eq 1 ]; then
    echo "Tokens loaded from environment. Skipping Garmin authentication."
else
    echo "No GARMIN_TOKEN_* variables found. Will attempt normal login."
fi
 
# Start the garmin-mcp server
exec uv run garmin-mcp
