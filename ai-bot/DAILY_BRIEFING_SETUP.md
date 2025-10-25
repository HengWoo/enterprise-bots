# Daily Briefing Automation Setup Guide

**Date:** 2025-10-16
**Version:** v0.2.4+
**Purpose:** Set up automated daily briefing generation via cron

---

## 📋 Overview

The daily briefing system automatically generates summaries of previous day's activity across all Campfire rooms. It runs at 9:00 AM daily and stores briefings for future reference.

### **How It Works**
1. **Cron job** triggers at 9:00 AM daily
2. **Script** runs inside Docker container
3. **Analyzes** all messages from yesterday
4. **Generates** markdown briefing file
5. **Stores** in `/root/ai-knowledge/briefings/`

### **Briefing Contents**
- 📊 Activity summary by room
- 💬 Key discussions and decisions
- 📎 Files uploaded
- 👥 Active participants
- 🔍 Searchable archive

---

## 🚀 Setup Steps (Production Server)

### **Step 1: Create Knowledge Base Directories**

SSH to production via DigitalOcean console:

```bash
# Create directory structure
sudo mkdir -p /root/ai-knowledge/briefings
sudo mkdir -p /root/ai-knowledge/user_contexts
sudo mkdir -p /root/ai-knowledge/logs

# Set permissions (container runs as appuser UID 1000)
sudo chown -R 1000:1000 /root/ai-knowledge

# Verify
ls -la /root/ai-knowledge/
```

**Expected output:**
```
drwxr-xr-x 2 1000 1000 4096 Oct 16 09:00 briefings
drwxr-xr-x 2 1000 1000 4096 Oct 16 09:00 user_contexts
drwxr-xr-x 2 1000 1000 4096 Oct 16 09:00 logs
```

---

### **Step 2: Test Script Manually**

Before setting up cron, verify the script works:

```bash
# Test with yesterday's date
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py

# Test with specific date
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --date 2025-10-15

# Test with detailed format
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --format detailed
```

**Expected output:**
```
[Cron] Generating briefing for yesterday: 2025-10-15
[Cron] Using database: /var/once/campfire/db/production.sqlite3
[Cron] ✅ CampfireTools initialized
[Cron] 📋 Generating briefing...
[Cron] ✅ Success!
[Cron]    File: /root/ai-knowledge/briefings/briefing_2025-10-15.md
[Cron]    Messages: 42
[Cron]    Files: 3
[Cron]    Rooms: 5
[Cron]    Participants: 8
[Cron] 🎉 Daily briefing generation complete!
```

**Check generated file:**
```bash
cat /root/ai-knowledge/briefings/briefing_2025-10-15.md
```

---

### **Step 3: Create Cron Job**

Now that we've verified it works, set up the automated schedule:

```bash
# Edit crontab for root user
sudo crontab -e
```

**Add this line:**
```cron
# Daily briefing generation at 9:00 AM
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-knowledge/logs/briefing-cron.log 2>&1
```

**Save and exit** (in vi: press `ESC`, type `:wq`, press `ENTER`)

**Verify cron is scheduled:**
```bash
sudo crontab -l
```

**Expected output:**
```
# Daily briefing generation at 9:00 AM
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-knowledge/logs/briefing-cron.log 2>&1
```

---

### **Step 4: Test Cron Job**

Test the cron job manually (don't wait until 9 AM):

```bash
# Run the exact command from cron
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py >> /root/ai-knowledge/logs/briefing-cron.log 2>&1

# Check the log
cat /root/ai-knowledge/logs/briefing-cron.log
```

**Expected log output:**
```
[Cron] Generating briefing for yesterday: 2025-10-15
[Cron] ✅ CampfireTools initialized
[Cron] 📋 Generating briefing...
[Cron] ✅ Success!
[Cron] 🎉 Daily briefing generation complete!
```

---

## 🔍 Verification Checklist

After setup, verify everything works:

- [ ] **Directories exist:** `/root/ai-knowledge/briefings`, `/root/ai-knowledge/logs`
- [ ] **Permissions correct:** Owned by UID 1000 (appuser)
- [ ] **Manual test passes:** Script runs successfully via `docker exec`
- [ ] **Cron installed:** `sudo crontab -l` shows the job
- [ ] **Log file created:** `/root/ai-knowledge/logs/briefing-cron.log` exists
- [ ] **Briefing generated:** Files appear in `/root/ai-knowledge/briefings/`

---

## 📊 Monitoring & Maintenance

### **Check if briefings are being generated:**
```bash
# List generated briefings
ls -lh /root/ai-knowledge/briefings/

# Check today's briefing
cat /root/ai-knowledge/briefings/briefing_$(date -d "yesterday" +%Y-%m-%d).md
```

### **Monitor cron logs:**
```bash
# View recent cron executions
tail -50 /root/ai-knowledge/logs/briefing-cron.log

# Watch cron log in real-time (for testing)
tail -f /root/ai-knowledge/logs/briefing-cron.log
```

### **Check cron execution history:**
```bash
# System-wide cron logs
sudo grep CRON /var/log/syslog | grep briefing | tail -20
```

---

## 🔧 Troubleshooting

### **Problem 1: Script fails with "Permission denied"**

**Symptom:**
```
[Cron] Error: [Errno 13] Permission denied: 'briefings'
```

**Solution:**
```bash
sudo chown -R 1000:1000 /root/ai-knowledge
sudo chmod -R 755 /root/ai-knowledge
```

---

### **Problem 2: Database not found**

**Symptom:**
```
[Cron] Error: Database not found at /var/once/campfire/db/production.sqlite3
```

**Solution:**
Verify the database path is correctly mounted in `docker-compose.yml`:
```yaml
volumes:
  - /var/once/campfire/db:/var/once/campfire/db:ro
```

---

### **Problem 3: Cron not running**

**Check if cron daemon is active:**
```bash
sudo systemctl status cron
```

**Restart cron if needed:**
```bash
sudo systemctl restart cron
```

---

### **Problem 4: No output in log file**

**Check cron is executing:**
```bash
# Check system cron logs
sudo grep CRON /var/log/syslog | tail -20

# Check for errors
sudo grep briefing /var/log/syslog | tail -20
```

**Verify container is running:**
```bash
docker ps | grep campfire-ai-bot
```

---

## 📅 Cron Schedule Examples

**Current setup (9:00 AM daily):**
```cron
0 9 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
```

**Alternative schedules:**

**Run at 8:00 AM:**
```cron
0 8 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
```

**Run twice daily (9 AM and 6 PM):**
```cron
0 9,18 * * * docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
```

**Run on weekdays only (Mon-Fri at 9 AM):**
```cron
0 9 * * 1-5 docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py
```

**Run weekly on Monday at 9 AM:**
```cron
0 9 * * 1 docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --format detailed
```

---

## 🎯 Usage Scenarios

### **Scenario 1: Daily Team Briefings**
- **When:** 9:00 AM every day
- **What:** Concise summary of yesterday's activity
- **Who:** Team leads, managers
- **How:** Automated via cron

### **Scenario 2: Manual Briefing Generation**
```bash
# Generate briefing for specific date
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --date 2025-10-10

# Generate detailed briefing
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --format detailed

# Generate for specific rooms only
docker exec campfire-ai-bot python /app/scripts/generate_daily_briefing.py --rooms "1,5,10"
```

### **Scenario 3: Briefing Assistant Integration**
Users can also request briefings in Campfire:
```
@日报助手 生成今天的日报
@日报助手 搜索上周的简报
```

---

## 📁 File Structure

### **Briefing Files Location**
```
/root/ai-knowledge/briefings/
├── briefing_2025-10-14.md
├── briefing_2025-10-15.md
├── briefing_2025-10-16.md
└── ...
```

### **Briefing File Format**
```markdown
# Daily Briefing: 2025-10-15

Generated: 2025-10-16 09:00:00

## Summary
- **Messages:** 42
- **Active Rooms:** 5
- **Participants:** 8
- **Files Uploaded:** 3

## Room Activity

### Finance Team (Room #5)
- 15 messages
- Key topics: Q3 budget review, expense reports
- Files: 2 (budget_Q3.xlsx, expenses_September.pdf)

### Engineering Team (Room #3)
- 18 messages
- Key topics: API deployment, bug fixes
- Files: 1 (deployment_plan.md)

...
```

---

## 🔐 Security Notes

1. **Database Access:** Read-only mount for safety
2. **Permissions:** Only appuser (UID 1000) can write briefings
3. **Privacy:** Briefings contain conversation summaries
4. **Retention:** Consider rotation policy (e.g., keep 90 days)

---

## ✅ Success Criteria

Daily briefing automation is working when:

1. ✅ Cron job runs at 9:00 AM daily
2. ✅ New briefing file created each day
3. ✅ Log file shows successful execution
4. ✅ No permission errors
5. ✅ Briefings contain expected content
6. ✅ Files accessible to authorized users

---

## 📝 Next Steps After Setup

1. **Test for one week** - Verify briefings generated daily
2. **Set up monitoring** - Alert if briefing fails
3. **Configure retention** - Auto-delete old briefings
4. **Customize format** - Adjust summary_length if needed
5. **Train users** - Show how to access briefings

---

**Document Version:** 1.0
**Created:** 2025-10-16
**Prerequisites:** v0.2.4 deployed with scripts/ directory
**Estimated Setup Time:** 10 minutes

**Ready to proceed? Follow the steps above on your production server!**
