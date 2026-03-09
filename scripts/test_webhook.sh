#!/usr/bin/env bash
# Test the Linear webhook with a simple "Ready for Spec" issue.
# Usage:
#   ./scripts/test_webhook.sh                    # use default title and fake id
#   ./scripts/test_webhook.sh "Your issue title"  # custom title
#   LINEAR_ISSUE_ID=real-uuid-here ./scripts/test_webhook.sh  # real Linear issue (Nova will update description)

set -e
BASE_URL="${AGLANCER_BASE_URL:-https://api.aglancer.tech}"
TITLE="${1:-Add a simple test button to the dashboard}"
ISSUE_ID="${LINEAR_ISSUE_ID:-test-issue-$(date +%s)}"

echo "POST $BASE_URL/webhooks/linear"
echo "Issue ID: $ISSUE_ID"
echo "Title: $TITLE"
echo "State: Ready for Spec"
echo ""

curl -sS -X POST "$BASE_URL/webhooks/linear" \
  -H "Content-Type: application/json" \
  -d "{
    \"action\": \"create\",
    \"data\": {
      \"id\": \"$ISSUE_ID\",
      \"title\": \"$TITLE\",
      \"state\": \"Ready for Spec\"
    }
  }" | jq .

echo ""
echo "Check Slack for 'Task routed to Nova' and 'Nova completed work'."
echo "Check Supabase: tasks, jobs, agent_outputs."
echo "If you used a real LINEAR_ISSUE_ID, check the Linear issue description for the spec."
