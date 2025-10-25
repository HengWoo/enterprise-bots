#!/bin/bash
# Claude Code Knowledge Base Deployment Script
# Deploy to: /root/ai-knowledge/company_kb/claude-code/

set -e

echo "🚀 Deploying Claude Code Knowledge Base..."

# Create base64 encoded data file
cat > /tmp/claude-code-kb.tar.gz.b64 << 'EOF'
REPLACE_WITH_BASE64_DATA
EOF

echo "📦 Decoding archive..."
base64 -d -i /tmp/claude-code-kb.tar.gz.b64 -o /tmp/claude-code-kb.tar.gz

echo "📂 Extracting to /root/ai-knowledge/company_kb/..."
cd /root/ai-knowledge/company_kb/
tar -xzf /tmp/claude-code-kb.tar.gz

# Move to correct location
if [ -d "knowledge-base/claude-code" ]; then
    echo "🔄 Moving to correct location..."
    rm -rf claude-code
    mv knowledge-base/claude-code ./
    rm -rf knowledge-base
fi

echo "🧹 Cleaning up temporary files..."
rm -f /tmp/claude-code-kb.tar.gz.b64 /tmp/claude-code-kb.tar.gz

echo "✅ Deployment complete!"
echo ""
echo "📋 Verifying deployment..."
ls -la /root/ai-knowledge/company_kb/claude-code/

echo ""
echo "🎯 Knowledge base structure:"
find /root/ai-knowledge/company_kb/claude-code/ -type f -name "*.md" -o -name "llm.txt" | sort

echo ""
echo "✨ Ready to test! Run:"
echo "curl -X POST http://localhost:5000/webhook/cc_tutor \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"creator\":{\"id\":1,\"name\":\"Test\"},\"room\":{\"id\":1,\"name\":\"Test\"},\"content\":\"如何安装 Claude Code?\"}'"
