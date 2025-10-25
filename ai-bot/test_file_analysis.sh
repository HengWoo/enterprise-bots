#!/bin/bash

echo "Testing file analysis with Financial MCP..."

curl -X POST http://localhost:5001/webhook/financial_analyst \
  -H "Content-Type: application/json" \
  -d @- <<'EOF'
{
  "creator": {"id": 1, "name": "Test User"},
  "room": {"id": 2, "name": "Finance Team"},
  "content": "Use parse_excel tool to read this file",
  "attachments": [{
    "path": "/Users/heng/Development/AI_apps/fin_report_agent/fin_report_agent/sample_restaurant.xlsx",
    "filename": "sample_restaurant.xlsx"
  }]
}
EOF
