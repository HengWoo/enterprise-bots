# CI/CD Pipeline Guide

**Status:** ✅ Production Ready
**Setup Date:** November 6, 2025
**Last Updated:** November 6, 2025

---

## Overview

Fully automated CI/CD pipeline using GitHub Actions with manual approval gates for production deployments.

---

## Quick Start

### Build New Version
1. Navigate to: https://github.com/HengWoo/enterprise-bots/actions
2. Select: "Build and Push to Docker Hub"
3. Click: "Run workflow"
4. Enter version: `vX.Y.Z` (e.g., `v0.5.3`)
5. Check "Also tag as latest": true/false
6. Wait ~5-10 minutes

### Deploy to Production
1. Navigate to: https://github.com/HengWoo/enterprise-bots/actions
2. Select: "Deploy to Production"
3. Click: "Run workflow"
4. Enter version: `vX.Y.Z` or `latest`
5. Wait for approval request
6. Click: "Review deployments" → "Approve and deploy"
7. Wait ~2-3 minutes (includes health checks)

### Rollback
**Automatic:** Deployment failures trigger automatic rollback to v0.5.3.3

**Manual:** Run "Deploy to Production" workflow with previous stable version

---

## Workflows

### Build and Push to Docker Hub
**File:** `.github/workflows/build-and-push.yml`

**Features:**
- Manual trigger with version input (vX.Y.Z format validation)
- Multi-platform Docker build (linux/amd64)
- Automated tagging: vX.Y.Z, X.Y.Z, latest (optional)
- Pushes to Docker Hub: `hengwoo/campfire-ai-bot`
- Creates GitHub release with detailed notes
- Estimated time: 5-10 minutes

**Permissions Required:**
```yaml
permissions:
  contents: write  # For creating GitHub releases
  packages: write  # For pushing Docker images
```

### Deploy to Production
**File:** `.github/workflows/deploy-production.yml`

**Features:**
- Manual trigger with version input
- **Protected production environment** (requires approval)
- SSH to DigitalOcean server (128.199.175.50)
- Pull specified Docker image
- Update docker-compose.yml with version tag
- Execute `docker-compose down && docker-compose up -d`
- 10 health check retries (30s intervals)
- **Automatic rollback to v0.5.3.3 on failure**
- Estimated time: 2-3 minutes after approval

---

## GitHub Configuration

### Secrets (5 required)
```
DOCKERHUB_USERNAME   # Docker Hub login username
DOCKERHUB_TOKEN      # Docker Hub access token
DO_SSH_KEY           # Ed25519 private key for DigitalOcean
DO_HOST              # 128.199.175.50
DO_USER              # root
```

### Production Environment
- Manual approval required before deployment
- Prevents accidental production changes
- Configured in GitHub repository settings

---

## Architecture

```
Developer pushes code → GitHub Repository
                              ↓
Manual trigger: "Build and Push to Docker Hub"
                              ↓
GitHub Actions Runner (ubuntu-latest)
  ├─ Checkout code (with submodules)
  ├─ Validate version format (vX.Y.Z)
  ├─ Docker buildx (linux/amd64)
  ├─ Push to Docker Hub (hengwoo/campfire-ai-bot)
  └─ Create GitHub release (with notes)
                              ↓
Manual trigger: "Deploy to Production"
                              ↓
GitHub Actions Runner
  ├─ Wait for approval (production environment)
  ├─ SSH to DigitalOcean (128.199.175.50)
  ├─ Pull Docker image
  ├─ Update docker-compose.yml
  ├─ Execute: docker-compose down && up -d
  ├─ Health checks (10 retries, 30s intervals)
  └─ Rollback on failure (automatic)
                              ↓
Production Service Running (https://chat.smartice.ai)
```

---

## Git Submodule Configuration

### Problem
financial-mcp was gitignored as nested git repository, causing CI/CD build failures:
```
ERROR: "/financial-mcp": not found
```

### Solution
Converted to proper git submodule (Commit 892fc07)

```bash
# Removed nested repository
git rm -r --cached ai-bot/financial-mcp
rm -rf ai-bot/financial-mcp

# Added as submodule
git submodule add https://github.com/HengWoo/fin_report_agent.git ai-bot/financial-mcp

# Updated workflow to checkout submodules
- uses: actions/checkout@v4
  with:
    submodules: recursive
```

**Benefits:**
- CI/CD builds now include financial-mcp automatically
- Financial Analyst bot maintains all 17 MCP tools
- Proper separation between repositories
- Easy to update financial-mcp independently

**Configuration Files:**
- `.gitmodules` - Submodule definition
- `.gitignore` (root + ai-bot/) - Removed financial-mcp exclusions
- `ai-bot/Dockerfile` - Simplified COPY (no conditional logic)

---

## Testing Results

### Test 1: Build and Push (v0.5.3)
- ✅ Version format validation working
- ✅ Submodule checkout successful
- ✅ Docker build successful (linux/amd64)
- ✅ Images pushed to Docker Hub
- ❌ GitHub release failed (permissions issue)

### Test 2: Build and Push (v0.5.4)
- ✅ Permissions fix applied (commit c629f6f)
- ✅ Docker build successful
- ✅ Images pushed to Docker Hub
- ✅ GitHub release created successfully

### Test 3: Deploy to Production (v0.5.4)
- ✅ Approval gate working (manual approval required)
- ✅ SSH connection successful
- ⚠️ Deployment cancelled before completion (test only)

**Test Cleanup:**
- Deleted GitHub releases: v0.5.3, v0.5.4
- Test tags remain in Docker Hub for reference

---

## Cleanup Results (Nov 6, 2025)

### Local Docker Images
- Removed 7 old images (0.4.x, 0.5.0, 0.5.2, 0.5.2.1)
- Removed old ARM64 images (2.66GB from v0.5.0)
- Removed dangling images (372.6MB)
- **Total reclaimed: ~3GB**
- Kept: v0.5.2.2, latest (production images only)

### DigitalOcean Production Server
- Removed 12 dangling images (7.75GB)
- Removed 2 old tagged versions (2GB): 0.2.4.2, 1.0.12
- **Total reclaimed: ~9.75GB (78% reduction)**
- Down from 12.53GB to 2.78GB
- Kept: v0.5.2.2, latest (current production)

### Local Codebase
- Removed ~700MB of temporary files:
  - Old Docker archives: `campfire-ai-bot-1.0.0.tar.gz`, `1.0.1.tar.gz`, `1.0.4.tar.gz` (694MB)
  - Old scripts: `DAILY_BRIEFING_QUICKSTART.sh`, `deploy-kb.sh`, etc.
  - Old docker-compose variants: `docker-compose.local.yml`, `.production.yml`, `.test.yml`
  - Test files: `test_*.py`, `test_*.json`, `test_*.txt`, `test_*.sh`
- Untracked `archive/` folder (96 files, 1.3MB) - stays local, won't sync to GitHub
- **Total cleanup: ~700MB local files**

**Combined Total:** ~13.75GB reclaimed

---

## Key Benefits

### Automation
- ✓ One-click builds (no local Docker required)
- ✓ One-click deployments (no SSH required)
- ✓ Automated health checks
- ✓ Automatic rollback on failures

### Safety
- ✓ Version format validation
- ✓ Manual approval gates for production
- ✓ Comprehensive health checks
- ✓ Automatic rollback protection

### Quality
- ✓ Consistent build environment (GitHub-hosted runners)
- ✓ Automated GitHub releases with notes
- ✓ Multi-platform support ready (currently amd64 only)
- ✓ Clean separation: build vs deploy workflows

### Efficiency
- ✓ No local Docker builds needed
- ✓ No SSH key management on local machines
- ✓ 5-10 min builds (faster than local M1 cross-compilation)
- ✓ 2-3 min deployments (including health checks)

---

## Troubleshooting

### Build fails with "financial-mcp not found"
**Solution:** Ensure submodule is properly initialized and workflow uses `submodules: recursive`

### GitHub release creation fails with 403
**Solution:** Check workflow has `permissions: contents:write, packages:write`

### Deployment fails health checks
**Result:** Automatic rollback to v0.5.3.3 will be triggered

### SSH connection fails
**Check:** Verify DO_SSH_KEY, DO_HOST, DO_USER secrets are correctly configured

---

## Infrastructure Requirements

### NGINX Reverse Proxy (Required for v0.5.3.2+)

**Purpose:** Routes file download requests from `https://chat.smartice.ai/files/download/*` to AI service on port 5000.

**Why Needed:**
- File download endpoint exists in AI service (FastAPI), not Campfire (Rails)
- Generated download URLs use Campfire domain for better UX
- Without nginx routing, users get 404 errors

**Configuration File:** `ai-bot/deployment/nginx-file-downloads.conf`

**Installation Steps:**

1. **SSH to production server:**
   ```bash
   ssh root@128.199.175.50
   ```

2. **Locate nginx config:**
   ```bash
   ls /etc/nginx/sites-available/
   # Usually: campfire or default
   ```

3. **Edit config file:**
   ```bash
   sudo nano /etc/nginx/sites-available/campfire
   ```

4. **Add location block BEFORE `location /`:**
   ```nginx
   location /files/download/ {
       proxy_pass http://localhost:5000/files/download/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_read_timeout 300;
   }
   ```

5. **Test configuration:**
   ```bash
   sudo nginx -t
   ```

6. **Reload nginx:**
   ```bash
   sudo systemctl reload nginx
   ```

7. **Verify routing:**
   ```bash
   # Should return 404 from FastAPI (not Campfire)
   curl -I https://chat.smartice.ai/files/download/test
   ```

**See Also:** Complete configuration with comments in `ai-bot/deployment/nginx-file-downloads.conf`

---

## Future Enhancements

- Consider adding ARM64 builds for Apple Silicon
- Consider adding staging environment
- Consider automated testing before deployment
- Consider automatic version bumping

---

## Commits

- `892fc07` - Convert financial-mcp to git submodule + add recursive checkout
- `c629f6f` - Add GitHub release permissions to build workflow

---

**Document Version:** 1.0
**Created:** 2025-11-06
**See Also:** QUICK_REFERENCE.md (quick commands), CLAUDE.md (project overview)
