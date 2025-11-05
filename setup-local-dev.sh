#!/bin/bash
# ============================================================================
# Local Development Environment Setup Script
# ============================================================================
# Quick setup for production-faithful local testing environment
#
# Usage:
#   ./setup-local-dev.sh
#
# What it does:
#   1. Creates .env.local from template (if not exists)
#   2. Creates storage directories
#   3. Builds Docker images
#   4. Initializes Campfire database
#   5. Provides next steps guidance
#
# Author: Claude AI Assistant
# Date: 2025-10-27
# ============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Campfire AI Bot - Local Development Environment Setup        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "docker-compose.dev.yml" ]; then
    echo -e "${RED}❌ Error: Must run from /campfire/ directory${NC}"
    echo -e "${YELLOW}   cd /Users/heng/Development/campfire${NC}"
    exit 1
fi

# Step 1: Check/Create .env.local
echo -e "${YELLOW}[1/5] Checking environment configuration...${NC}"
if [ ! -f "ai-bot/.env.local" ]; then
    if [ ! -f "ai-bot/.env.local.example" ]; then
        echo -e "${RED}❌ Error: .env.local.example not found${NC}"
        exit 1
    fi

    echo -e "${GREEN}   ✅ Creating ai-bot/.env.local from template${NC}"
    cp ai-bot/.env.local.example ai-bot/.env.local

    echo ""
    echo -e "${YELLOW}   ⚠️  ACTION REQUIRED:${NC}"
    echo -e "${YELLOW}   Edit ai-bot/.env.local and add your fallback API key${NC}"
    echo -e "${YELLOW}   (HusanAI key is already set)${NC}"
    echo ""
    echo -e "${BLUE}   Run: nano ai-bot/.env.local${NC}"
    echo -e "${BLUE}   Add: ANTHROPIC_API_KEY_FALLBACK=sk-ant-api03-YOUR_KEY${NC}"
    echo ""
    read -p "   Press Enter after editing .env.local to continue..."
else
    echo -e "${GREEN}   ✅ ai-bot/.env.local already exists${NC}"
fi

# Step 2: Create storage directories
echo ""
echo -e "${YELLOW}[2/5] Creating storage directories...${NC}"
mkdir -p storage/db storage/files log
echo -e "${GREEN}   ✅ Created: storage/db, storage/files, log${NC}"

# Step 3: Build Docker images
echo ""
echo -e "${YELLOW}[3/5] Building Docker images (this may take 5-10 minutes)...${NC}"
docker-compose -f docker-compose.dev.yml build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Docker images built successfully${NC}"
else
    echo -e "${RED}   ❌ Docker build failed${NC}"
    exit 1
fi

# Step 4: Initialize database
echo ""
echo -e "${YELLOW}[4/5] Initializing Campfire database...${NC}"
docker-compose -f docker-compose.dev.yml run --rm campfire bin/rails db:setup

if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Database initialized${NC}"
    echo -e "${GREEN}   Default admin: admin@example.com / password${NC}"
else
    echo -e "${RED}   ❌ Database initialization failed${NC}"
    exit 1
fi

# Step 5: Final instructions
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Setup Complete! Next Steps:                               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}1. Create bot users (required):${NC}"
echo -e "   docker-compose -f docker-compose.dev.yml run --rm campfire bin/rails console"
echo ""
echo -e "   ${YELLOW}# In Rails console, paste this:${NC}"
echo -e '   bots = [
     {name: "财务分析师", id: "financial_analyst"},
     {name: "技术助手", id: "technical_assistant"},
     {name: "个人助手", id: "personal_assistant"},
     {name: "日报助手", id: "briefing_assistant"},
     {name: "AI Assistant", id: "default"},
     {name: "运营数据助手", id: "operations_assistant"},
     {name: "Claude Code导师", id: "cc_tutor"},
     {name: "菜单工程师", id: "menu_engineer"}
   ]
   bots.each do |b|
     bot = User.create!(name: b[:name], email: "#{b[:id]}@bots.local", password: "dev123", role: "bot")
     puts "#{b[:name]}: #{bot.id}-#{bot.bot_token}"
   end'
echo ""
echo -e "${BLUE}2. Update bot configurations:${NC}"
echo -e "   Copy the bot keys from above and update ai-bot/bots/*.json files"
echo ""
echo -e "${BLUE}3. Start the environment:${NC}"
echo -e "   docker-compose -f docker-compose.dev.yml up"
echo ""
echo -e "${BLUE}4. Access Campfire:${NC}"
echo -e "   open http://localhost:3000"
echo ""
echo -e "${BLUE}5. Read full documentation:${NC}"
echo -e "   cat DEV_SETUP.md"
echo ""
echo -e "${GREEN}Happy testing! 🚀${NC}"
