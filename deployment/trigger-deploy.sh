#!/bin/bash
# Trigger deployment by calling the webhook endpoint
# This script can be run locally to manually trigger a deployment

set -e

WEBHOOK_URL="https://cryptoalpha.vip/webhook"

echo "================================================"
echo "Manual Deployment Trigger"
echo "================================================"
echo ""
echo "Triggering deployment via webhook..."
echo "URL: ${WEBHOOK_URL}"
echo ""

RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {
      "full_name": "ripgtxgt/trading_dashboard"
    },
    "pusher": {
      "name": "manual-trigger"
    },
    "head_commit": {
      "id": "manual-deployment",
      "message": "Manual deployment triggered"
    }
  }' \
  "${WEBHOOK_URL}")

echo "Response: ${RESPONSE}"
echo ""
echo "================================================"
echo "Deployment triggered!"
echo "================================================"
echo ""
echo "Check deployment status:"
echo "  ssh ubuntu@3.112.226.9 'pm2 logs webhook-deploy-server --lines 50'"
