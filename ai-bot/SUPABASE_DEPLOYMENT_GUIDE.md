# Supabase Configuration - Secure Deployment Guide

**Security Notice:** This guide contains instructions for deploying Supabase credentials securely. Never commit actual credentials to git.

---

## 🔒 Security Best Practices

### ✅ What's Safe
- `.env` files are **gitignored** - local credentials won't be committed
- This documentation is safe to commit (no actual secrets)
- Production credentials should only exist on the server

### ❌ What to Avoid
- **NEVER** commit `.env` files with real credentials
- **NEVER** add credentials to docker-compose.yml in git
- **NEVER** share service role keys publicly

---

## 📋 Supabase Credentials Needed

You need two pieces of information from your Supabase dashboard:

1. **Project URL:** `https://[PROJECT_ID].supabase.co`
2. **API Key:** Either anon key (read-only) or service role key (full access)

**Where to find them:**
1. Go to https://app.supabase.com
2. Select your project
3. Go to **Settings** → **API**
4. Copy the values

---

## 🚀 Deployment Steps

### Step 1: On Production Server

SSH to your production server:

```bash
ssh root@128.199.175.50
```

### Step 2: Edit .env File

Navigate to the service directory and edit the .env file:

```bash
cd /root/ai-service
nano .env
```

### Step 3: Add Supabase Configuration

Add these lines to the .env file:

```bash
# Supabase Configuration (Operations Data)
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_ACTUAL_KEY_HERE
```

**Replace with your actual values:**
- `YOUR_PROJECT_ID` - Your Supabase project ID
- `YOUR_ACTUAL_KEY_HERE` - Your anon key or service role key

Save and exit (Ctrl+X, Y, Enter).

### Step 4: Restart the Service

```bash
docker-compose down
docker-compose up -d
```

### Step 5: Verify Configuration

Check the logs to verify Supabase connected:

```bash
docker logs campfire-ai-bot | grep -i supabase
```

**Expected output:**
```
[Supabase] ✅ Supabase tools initialized
```

**If you see this instead:**
```
[Supabase] ℹ️  Supabase credentials not found
```

Then the environment variables weren't loaded. Check:
- .env file exists in `/root/ai-service/`
- .env file has correct variable names (`SUPABASE_URL` and `SUPABASE_KEY`)
- docker-compose.yml mounts the .env file

---

## 🧪 Testing

Test the Operations Assistant to verify it can query Supabase:

```bash
curl -X POST https://chat.smartice.ai/webhook/operations_assistant \
  -H "Content-Type: application/json" \
  -d '{
    "creator": {"id": 999, "name": "测试用户"},
    "room": {"id": 999, "name": "测试"},
    "content": "查询本周运营数据"
  }'
```

**Expected:** Bot should query Supabase and return data (not show "credentials not configured" error)

---

## 📊 Current Configuration

**Project:** wdpeoyugsxqnpwwtkqsl
**URL:** https://wdpeoyugsxqnpwwtkqsl.supabase.co
**Key Type:** Anon key (read-only mode)

**Security Note:** Using anon key provides read-only access. For write operations, you'll need the service role key.

---

## 🔧 Troubleshooting

### Issue: "Supabase credentials not found"

**Cause:** Environment variables not loaded

**Solution:**
1. Check .env file exists: `ls -la /root/ai-service/.env`
2. Check content: `grep SUPABASE /root/ai-service/.env`
3. Restart container: `docker-compose restart`

### Issue: "Connection failed"

**Cause:** Incorrect credentials or network issue

**Solution:**
1. Verify credentials in Supabase dashboard
2. Test connection: `curl https://wdpeoyugsxqnpwwtkqsl.supabase.co`
3. Check firewall rules

### Issue: "Permission denied" on queries

**Cause:** Using anon key without proper RLS policies

**Solution:**
1. Check Supabase RLS policies
2. OR use service role key (bypasses RLS)
3. OR update RLS policies to allow anon access

---

## 🔐 Key Management

**Local Development:**
- Credentials in `.env` (gitignored)
- Safe to use anon key for testing

**Production:**
- Credentials in `/root/ai-service/.env` (not in git)
- Consider using secrets manager for production
- Rotate keys periodically

**Best Practices:**
- Use anon key for read-only operations
- Use service role key only when write access needed
- Never commit keys to version control
- Use different keys for dev/staging/prod

---

## 📝 Environment Variable Reference

```bash
# Required for Operations Assistant Supabase integration
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_KEY=[anon-key or service-role-key]
```

**Note:** These are loaded by `src/tools/supabase_tools.py` via `os.environ.get()`

---

## ✅ Verification Checklist

- [ ] .env file created on production server
- [ ] SUPABASE_URL and SUPABASE_KEY added to .env
- [ ] Values copied correctly from Supabase dashboard
- [ ] Service restarted
- [ ] Logs show "Supabase tools initialized"
- [ ] Operations assistant can query data
- [ ] No credentials committed to git

---

**Document Version:** 1.0
**Last Updated:** 2025-10-21
**Security Level:** CONFIDENTIAL - Handle with care
