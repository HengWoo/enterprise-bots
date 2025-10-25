#!/bin/bash
# Agent Skills Comparison Testing Script
# Compares v0.2.4.2 (baseline) vs v0.3.0 (with skills)
# Usage: ./test_skills_comparison.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Campfire AI Bot - Agent Skills Comparison Test"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in the right directory
if [ ! -f "src/campfire_agent.py" ]; then
    echo -e "${RED}Error: Please run this script from ai-bot/ directory${NC}"
    exit 1
fi

# Save current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch: $CURRENT_BRANCH${NC}"
echo ""

# Function to test a version
test_version() {
    local VERSION=$1
    local BRANCH=$2

    echo -e "${YELLOW}━━━ Testing $VERSION ━━━${NC}"

    # Checkout the branch
    git checkout $BRANCH > /dev/null 2>&1

    # Verify version
    echo -n "Version check: "
    DOCKERFILE_VERSION=$(grep 'LABEL version=' Dockerfile | cut -d'"' -f2)
    echo -e "${GREEN}$DOCKERFILE_VERSION${NC}"

    # Check for skills directory
    echo -n "Skills directory: "
    if [ -d ".claude/skills" ]; then
        SKILL_COUNT=$(ls -1 .claude/skills/ | wc -l | tr -d ' ')
        echo -e "${GREEN}Found ($SKILL_COUNT skills)${NC}"
    else
        echo -e "${YELLOW}Not present${NC}"
    fi

    # Check agent config
    echo -n "Agent SDK config: "
    if grep -q "setting_sources" src/campfire_agent.py; then
        echo -e "${GREEN}Skills enabled${NC}"
    else
        echo -e "${YELLOW}Skills disabled${NC}"
    fi

    echo ""
}

# Test scenarios
test_scenarios() {
    local VERSION=$1

    echo -e "${BLUE}Test Scenarios for $VERSION:${NC}"
    echo ""
    echo "1. Simple Query: 'Hello'"
    echo "   Expected token usage: ~2600 (v0.2.4.2) vs ~600 (v0.3.0)"
    echo ""
    echo "2. Financial Query: 'Calculate ROE'"
    echo "   Expected token usage: ~2600 (v0.2.4.2) vs ~1400 (v0.3.0)"
    echo ""
    echo "3. KB Query: \"What's our expense policy?\""
    echo "   Expected token usage: ~2600 (v0.2.4.2) vs ~1000 (v0.3.0)"
    echo ""
    echo "To run actual tests:"
    echo "  1. Start server: TESTING=true uv run python src/app_fastapi.py"
    echo "  2. Send test requests (see examples below)"
    echo "  3. Check logs for token usage"
    echo ""
}

# Show test commands
show_test_commands() {
    echo -e "${BLUE}Test Commands (run after starting server):${NC}"
    echo ""

    echo "# Test 1: Simple Query"
    echo 'curl -X POST http://localhost:8000/webhook/financial_analyst \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '"'"'{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"Hello"}'"'"
    echo ""

    echo "# Test 2: Financial Query"
    echo 'curl -X POST http://localhost:8000/webhook/financial_analyst \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '"'"'{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"Calculate ROE"}'"'"
    echo ""

    echo "# Test 3: KB Query"
    echo 'curl -X POST http://localhost:8000/webhook/financial_analyst \'
    echo '  -H "Content-Type: application/json" \'
    echo '  -d '"'"'{"creator":{"id":1,"name":"Test"},"room":{"id":1,"name":"Test"},"content":"What is our expense policy?"}'"'"
    echo ""
}

# Main comparison
echo -e "${GREEN}Step 1: Version Comparison${NC}"
echo ""

# Test baseline
test_version "Baseline (v0.2.4.2)" "main"

# Test new version
test_version "Skills (v0.3.0)" "feature/agent-skills-v0.3.0"

# Show test scenarios
echo -e "${GREEN}Step 2: Token Usage Testing${NC}"
echo ""
test_scenarios

# Show test commands
echo -e "${GREEN}Step 3: How to Test${NC}"
echo ""
show_test_commands

# Return to original branch
echo -e "${YELLOW}Returning to original branch: $CURRENT_BRANCH${NC}"
git checkout $CURRENT_BRANCH > /dev/null 2>&1

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Comparison Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Review output above to verify both versions"
echo "  2. Follow 'How to Test' instructions to run actual tests"
echo "  3. Record results in SKILLS_COMPARISON_TEST_PLAN.md"
echo ""
echo "For detailed testing guide, see:"
echo "  - SKILLS_COMPARISON_TEST_PLAN.md"
echo "  - SKILLS_CHANGES_SUMMARY.md"
echo ""
