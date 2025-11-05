# DOCX Processing Feature Implementation (v0.4.0)

**Date:** October 26, 2025
**Status:** ✅ Implementation Complete - Ready for Testing
**Priority:** HIGH - Blocks v0.4.0 deployment

---

## 📝 Problem Statement

User reported that bots were failing to read PDF and DOCX files despite claiming support in their configurations.

### Root Cause Analysis

**PDF Files**:
- ✅ Read tool works perfectly for PDFs (confirmed with 712KB, 14-page test file)
- Bot system prompts had **misleading instructions** telling bots NOT to use Read tool for PDFs
- **Fix**: Updated system prompts to instruct bots to use Read tool for PDFs

**DOCX Files**:
- ❌ Read tool CANNOT read binary DOCX files (error: "cannot read binary files")
- Bot system prompts incorrectly claimed Read tool could handle DOCX
- Skills MCP approach requires Bash access (blocked by v0.4.0 security model)
- **Solution**: Created custom `process_docx` MCP tool using pandoc

---

## 🔧 Solution Implemented

### 1. Created Custom DOCX Processing Tool

**New File:** `/Users/heng/Development/campfire/ai-bot/src/tools/document_decorators.py`

**Tool:** `process_docx`
- **Purpose**: Convert DOCX files to markdown using pandoc
- **Security**: No Bash access required - uses controlled subprocess calls
- **Implementation**:
  - Validates file exists and is .docx/.doc
  - Checks file size (max 10MB)
  - Runs `pandoc --track-changes=all file.docx -o output.md`
  - Returns markdown content
  - Graceful error handling with helpful messages

**Key Features**:
- ✅ Works within v0.4.0 security model (no Bash tool needed)
- ✅ Uses temporary files for conversion
- ✅ Preserves document structure (headings, lists, tables)
- ✅ Preserves tracked changes if present
- ✅ File size validation (prevents overload)
- ✅ Timeout protection (30 seconds max)
- ✅ Clear error messages for troubleshooting

### 2. Updated Tools Infrastructure

**Modified:** `/Users/heng/Development/campfire/ai-bot/src/tools/__init__.py`
- Added `document_decorators` import
- Added `process_docx_tool` to exports
- Added initialization in `initialize_decorator_tools()`

### 3. Updated Bot Configurations

#### Personal Assistant (`bots/personal_assistant.json`)

**System Prompt Updates**:
- ✅ **Supported document types**: Clarified PDF uses Read, DOCX uses process_docx
- ✅ **Tool usage rules**: Added separate entries for Read (PDF) and process_docx (DOCX)
- ✅ **Best practices**: Updated workflow to use correct tool for each file type
- ✅ **Important tips**: Warn against using wrong tool

**Tools Enabled**: Added `"process_docx"` to tools array

#### Technical Assistant (`bots/technical_assistant.json`)

**System Prompt Updates**:
- ✅ Updated document processing capabilities section
- ✅ Clarified when to use Read (PDF) vs process_docx (DOCX)
- ✅ Added step-by-step instructions for document analysis

**Tools Enabled**: Added `"process_docx"` to tools array

### 4. Updated Docker Infrastructure

**Modified:** `/Users/heng/Development/campfire/ai-bot/Dockerfile`
- Added `pandoc` installation in runtime stage
- Updated version label to v0.4.0
- Updated description to include "DOCX Processing"

**Installation**:
```dockerfile
# Install sqlite3 and pandoc for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    pandoc \
    && rm -rf /var/lib/apt/lists/*
```

---

## 📋 Files Modified

| File | Changes | Status |
|------|---------|--------|
| `src/tools/document_decorators.py` | **NEW** - DOCX processing tool | ✅ Created |
| `src/tools/__init__.py` | Add document_decorators imports/exports | ✅ Updated |
| `bots/personal_assistant.json` | System prompt + add process_docx tool | ✅ Updated |
| `bots/technical_assistant.json` | System prompt + add process_docx tool | ✅ Updated |
| `Dockerfile` | Install pandoc + update version to 0.4.0 | ✅ Updated |

---

## 🧪 Testing Plan

### Phase 1: Local Testing (Required Before Deployment)

#### Test 1: PDF Reading (Verify Fix Works)
```bash
# Start local server
cd /Users/heng/Development/campfire/ai-bot
PYTHONPATH=/Users/heng/Development/campfire/ai-bot \
  TESTING=true \
  CAMPFIRE_URL=https://chat.smartice.ai \
  uv run python src/app_fastapi.py

# In another terminal, test PDF reading
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 999, "name": "Test User"},
    "room": {"id": 999, "name": "PDF Test"},
    "content": "请分析这个PDF文件：/Users/heng/Development/campfire/doc/餐饮会员体系调研报告与方案建议.pdf"
  }'
```

**Expected Result**:
- ✅ Bot uses Read tool
- ✅ Successfully extracts PDF content
- ✅ Provides analysis of the document

#### Test 2: DOCX Reading (New Feature)
```bash
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 999, "name": "Test User"},
    "room": {"id": 999, "name": "DOCX Test"},
    "content": "请分析这个Word文档：/Users/heng/Development/campfire/doc/睿畜科技战略合作服务商授权书2025.docx"
  }'
```

**Expected Result**:
- ✅ Bot uses process_docx tool
- ✅ Successfully converts DOCX to markdown
- ✅ Provides analysis of the document
- ✅ No errors about binary files

#### Test 3: Error Handling
```bash
# Test with non-existent file
curl -X POST http://localhost:8000/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 999, "name": "Test User"},
    "room": {"id": 999, "name": "Error Test"},
    "content": "请分析这个文件：/nonexistent/file.docx"
  }'
```

**Expected Result**:
- ✅ Clear error message: "File not found"
- ✅ No crashes or exceptions

### Phase 2: Docker Build Testing

```bash
# Build Docker image
cd /Users/heng/Development/campfire/ai-bot
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.4.0-test .

# Run container locally
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e CAMPFIRE_URL="https://chat.smartice.ai" \
  -e TESTING=true \
  hengwoo/campfire-ai-bot:0.4.0-test

# Verify pandoc is installed
docker exec <container_id> which pandoc
# Expected: /usr/bin/pandoc

# Test DOCX processing inside container
docker exec <container_id> bash -c "echo 'Test' | pandoc -f markdown -t docx -o /tmp/test.docx && pandoc /tmp/test.docx -o -"
# Expected: Successfully converts
```

---

## 🚀 Deployment Procedure

**IMPORTANT**: Only proceed after successful local testing

### Step 1: Verify All Tests Pass
- [ ] Test 1: PDF reading works
- [ ] Test 2: DOCX processing works
- [ ] Test 3: Error handling works
- [ ] Docker build succeeds
- [ ] Pandoc available in container

### Step 2: Build Production Image
```bash
cd /Users/heng/Development/campfire/ai-bot
docker buildx build --platform linux/amd64 \
  -t hengwoo/campfire-ai-bot:0.4.0 \
  -t hengwoo/campfire-ai-bot:latest .
```

### Step 3: Push to Docker Hub
```bash
docker push hengwoo/campfire-ai-bot:0.4.0
docker push hengwoo/campfire-ai-bot:latest
```

### Step 4: Deploy to Production
```bash
# SSH to production server (use DigitalOcean console)
ssh root@128.199.175.50

cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:latest
docker-compose up -d
docker logs -f campfire-ai-bot
```

### Step 5: Production Verification
```bash
# Test PDF reading in production
curl -X POST https://chat.smartice.ai/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":999,"name":"Test"},"room":{"id":999,"name":"Test"},"content":"测试PDF文件读取"}'

# Test DOCX processing in production
curl -X POST https://chat.smartice.ai/webhook/personal_assistant \
  -H "Content-Type: application/json" \
  -d '{"creator":{"id":999,"name":"Test"},"room":{"id":999,"name":"Test"},"content":"测试DOCX文件处理"}'
```

---

## ✅ Success Criteria

### Functional Requirements
- [x] Code implementation complete
- [ ] PDF reading works via Read tool (local testing)
- [ ] DOCX processing works via process_docx tool (local testing)
- [ ] Error handling graceful and informative
- [ ] No security violations (no Bash/Write/Edit usage)
- [ ] Pandoc installed in Docker container
- [ ] Docker build succeeds
- [ ] Production deployment successful
- [ ] Both features working in production

### User Experience
- [ ] User can upload PDF files and get analysis
- [ ] User can upload DOCX files and get analysis
- [ ] Clear error messages if file not found or unsupported
- [ ] No misleading "cannot read" messages
- [ ] Fast response times (< 30 seconds for documents)

---

## 🔄 Rollback Plan

If DOCX processing causes issues in production:

```bash
# Option 1: Rollback to v0.3.3.1
cd /root/ai-service
docker-compose down
docker pull hengwoo/campfire-ai-bot:0.3.3.1
docker-compose up -d

# Option 2: Disable process_docx tool only
# 1. Remove "process_docx" from bots/personal_assistant.json tools_enabled
# 2. Remove "process_docx" from bots/technical_assistant.json tools_enabled
# 3. Update system prompts to say DOCX not supported
# 4. Rebuild and redeploy
```

**Rollback Triggers**:
- pandoc command not found in container
- DOCX processing consistently fails
- Timeout issues with large documents
- Security violations detected
- User complaints about functionality

---

## 📊 Technical Details

### Tool Architecture

```
User uploads DOCX → Bot detects file type → Calls process_docx tool
                                                ↓
                                    Validates file (exists, size, type)
                                                ↓
                                    Creates temporary markdown file
                                                ↓
                                    Runs: pandoc --track-changes=all input.docx -o temp.md
                                                ↓
                                    Reads markdown content
                                                ↓
                                    Cleans up temp file
                                                ↓
                                    Returns content to bot
                                                ↓
                                    Bot analyzes and responds to user
```

### Security Considerations

**v0.4.0 Security Model**:
- Bots have access to safe tools only: `["WebSearch", "WebFetch", "Read", "Grep", "Glob", "Task"]`
- Bash, Write, Edit are blocked for security
- process_docx uses controlled subprocess (not Bash tool)
- Subprocess calls are validated and constrained
- File paths validated before processing
- Timeout protection prevents DoS

**Why This Approach**:
- ✅ No Bash access needed (secure)
- ✅ Controlled pandoc execution (safe)
- ✅ File validation (prevents abuse)
- ✅ Works within security restrictions
- ✅ Graceful error handling

---

## 📝 Next Steps

### Immediate (Before v0.4.0 Deployment)
1. **Run local tests** (PDF + DOCX + error handling)
2. **Build Docker image** (verify pandoc installation)
3. **Test in Docker container** (verify process_docx works)
4. **Get user approval** before production deployment

### After Successful Deployment
1. Monitor logs for first 24-48 hours
2. Track process_docx tool usage and errors
3. Document any edge cases or limitations discovered
4. Update user-facing documentation about supported formats

### Future Enhancements (v0.4.1+)
- Add support for .doc (older Word format)
- Add PPTX support (if needed)
- Add document creation capabilities
- Performance optimization for large documents
- Caching of converted documents

---

## 🎯 Summary

**Problem**: Bots couldn't read PDF and DOCX files despite claiming support

**Solution**:
- ✅ **PDF**: Fixed misleading system prompts → Use Read tool (works natively)
- ✅ **DOCX**: Created process_docx custom MCP tool → Uses pandoc conversion
- ✅ **Security**: Solution works within v0.4.0 security restrictions
- ✅ **Infrastructure**: Added pandoc to Docker container

**Status**: Implementation complete, ready for local testing

**Next Action**: Run local tests to verify solution before deployment

---

**Document Version:** 1.0
**Author:** Claude Code
**Last Updated:** October 26, 2025
