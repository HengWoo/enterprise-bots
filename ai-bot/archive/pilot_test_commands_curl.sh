#!/bin/bash
# v0.5.0 Pilot Validation Test Commands
# Run these against local FastAPI server (http://localhost:8000)

# Server should be running:
# cd /Users/heng/Development/campfire/ai-bot
# TESTING=true CAMPFIRE_URL=https://chat.smartice.ai uv run python src/app_fastapi.py

# ==============================================================================
# Workflow 1: Financial Calculation with Verification
# ==============================================================================
echo "🧪 Workflow 1: Financial Calculation"
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {
      "id": 1,
      "name": "Pilot Tester",
      "email_address": "test@example.com"
    },
    "room": {
      "id": 999,
      "name": "Pilot Validation"
    },
    "content": "<p>计算利润率：营业额 ¥120,000，成本 ¥85,000，请计算利润率并验证计算结果</p>"
  }'

echo -e "\n\n"

# ==============================================================================
# Workflow 2: HTML Report Generation
# ==============================================================================
echo "🧪 Workflow 2: HTML Report Generation"
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {
      "id": 1,
      "name": "Pilot Tester",
      "email_address": "test@example.com"
    },
    "room": {
      "id": 999,
      "name": "Pilot Validation"
    },
    "content": "<p>创建一个HTML演示文稿，主题是《v0.5.0新功能介绍》，包含3个部分：1. 验证模块 2. 代码生成 3. 测试基础设施。使用专业的样式和交互效果。</p>"
  }'

echo -e "\n\n"

# ==============================================================================
# Workflow 3: Data Query with Validation
# ==============================================================================
echo "🧪 Workflow 3: Data Query Validation"
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {
      "id": 1,
      "name": "Pilot Tester",
      "email_address": "test@example.com"
    },
    "room": {
      "id": 999,
      "name": "Pilot Validation"
    },
    "content": "<p>搜索我最近10条对话记录，找出关于\"menu engineering\"或\"菜单工程\"的讨论，并总结关键要点</p>"
  }'

echo -e "\n\n"

# ==============================================================================
# Workflow 4: Code Generation
# ==============================================================================
echo "🧪 Workflow 4: Code Generation"
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {
      "id": 1,
      "name": "Pilot Tester",
      "email_address": "test@example.com"
    },
    "room": {
      "id": 999,
      "name": "Pilot Validation"
    },
    "content": "<p>生成一个Python脚本来计算ROI（投资回报率）。脚本应该接收成本和收益作为输入，计算ROI百分比，并处理除零错误。请确保代码通过ruff linting检查。</p>"
  }'

echo -e "\n\n"

# ==============================================================================
# Workflow 5: Multi-Step PDF Processing
# ==============================================================================
# Note: This requires a PDF file to exist. For local testing, we'll simulate with a request
echo "🧪 Workflow 5: Multi-Step Workflow (Simulated)"
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {
      "id": 1,
      "name": "Pilot Tester",
      "email_address": "test@example.com"
    },
    "room": {
      "id": 999,
      "name": "Pilot Validation"
    },
    "content": "<p>创建一个任务提醒：明天下午3点提醒我完成v0.5.0验证报告。并为这个任务生成一个简单的HTML checklist，包含5个验证门控的检查项。</p>"
  }'

echo -e "\n\n"

# ==============================================================================
# Health Check
# ==============================================================================
echo "🏥 Health Check"
curl -X GET http://localhost:8000/health

echo -e "\n\n✅ All test commands executed. Check server logs for responses."
