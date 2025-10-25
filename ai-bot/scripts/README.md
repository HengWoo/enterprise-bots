# Automated Daily Briefing Scripts

## Overview

This directory contains scripts for automated daily briefing generation.

## Scripts

### `generate_daily_briefing.py`

Generates daily briefings for Campfire conversations. Designed to run via cron at 9:00 AM daily.

**Features:**
- Generates briefing for previous day by default
- Supports custom date ranges
- Can filter by specific rooms
- Handles days with no activity gracefully
- Logs output for monitoring

**Usage:**

```bash
# Generate briefing for yesterday (default)
python scripts/generate_daily_briefing.py

# Generate for specific date
python scripts/generate_daily_briefing.py --date 2025-10-15

# Generate for specific rooms only
python scripts/generate_daily_briefing.py --rooms 1,2,3

# Generate detailed briefing (instead of concise)
python scripts/generate_daily_briefing.py --format detailed
```

## Production Setup (DigitalOcean Server)

### Step 1: Create Log Directory

```bash
mkdir -p /root/ai-knowledge/logs
```

### Step 2: Test Script Manually

```bash
cd /root/ai-service
uv run python scripts/generate_daily_briefing.py --date 2025-10-15
```

Expected output:
```
[Cron] Generating briefing for specified date: 2025-10-15
[Cron] Target: All rooms
[Cron] Using database: /var/once/campfire/db/production.sqlite3
[Cron] ✅ CampfireTools initialized
[Cron] 📋 Generating briefing...
[Cron] ✅ Success!
[Cron]    File: /root/ai-knowledge/company_kb/briefings/2025/10/daily-briefing-2025-10-15.md
[Cron]    Messages: 25
[Cron]    Files: 3
[Cron]    Rooms: 2
[Cron]    Participants: 5
[Cron] 🎉 Daily briefing generation complete!
```

### Step 3: Install Cron Job

Edit crontab:
```bash
crontab -e
```

Add this line to run at 9:00 AM daily (generates briefing for previous day):
```cron
# Generate daily briefing at 9:00 AM
0 9 * * * cd /root/ai-service && /usr/bin/uv run python scripts/generate_daily_briefing.py >> /root/ai-knowledge/logs/briefing-cron.log 2>&1
```

**Explanation:**
- `0 9 * * *` - Run at 9:00 AM every day
- `cd /root/ai-service` - Change to project directory
- `/usr/bin/uv run python` - Use uv to run Python with correct dependencies
- `scripts/generate_daily_briefing.py` - The script to run
- `>> /root/ai-knowledge/logs/briefing-cron.log 2>&1` - Append output to log file

### Step 4: Verify Cron Job

Check cron is installed:
```bash
crontab -l
```

You should see the daily briefing line.

### Step 5: Monitor Logs

```bash
# View logs
tail -f /root/ai-knowledge/logs/briefing-cron.log

# Check today's briefing
cat /root/ai-knowledge/company_kb/briefings/$(date +%Y)/$(date +%m)/daily-briefing-$(date -d "yesterday" +%Y-%m-%d).md
```

## Timezone Considerations

**Server Timezone**: The cron job runs based on server timezone.

To check server timezone:
```bash
timedatectl
```

To change timezone (if needed):
```bash
# Example: Set to China Standard Time (UTC+8)
sudo timedatectl set-timezone Asia/Shanghai

# Or for UTC
sudo timedatectl set-timezone UTC
```

**Important**: Adjust cron time based on your timezone. The script generates briefings for "yesterday", so running at 9:00 AM generates the previous day's briefing.

## Troubleshooting

### Script fails with "Database not found"

Check database path:
```bash
ls -la /var/once/campfire/db/production.sqlite3
```

If using different path, set environment variable:
```bash
export CAMPFIRE_DB_PATH=/path/to/database.db
```

### No output in log file

Check cron service is running:
```bash
systemctl status cron
```

Check file permissions:
```bash
chmod +x /root/ai-service/scripts/generate_daily_briefing.py
chmod 755 /root/ai-knowledge/logs
```

### Script runs but no briefing generated

Check script output manually:
```bash
cd /root/ai-service
uv run python scripts/generate_daily_briefing.py --date 2025-10-15
```

Look for error messages in the output.

### Cron not running at expected time

Verify cron schedule:
```bash
crontab -l
```

Check cron logs:
```bash
grep CRON /var/log/syslog
```

## Testing

### Local Testing (Development)

```bash
# From ai-bot directory
CAMPFIRE_DB_PATH=./tests/fixtures/test.db uv run python scripts/generate_daily_briefing.py --date 2025-10-04
```

### Production Testing

```bash
# Generate briefing for yesterday
cd /root/ai-service
uv run python scripts/generate_daily_briefing.py

# Check result
ls -la /root/ai-knowledge/company_kb/briefings/$(date +%Y)/$(date +%m)/
```

## Alternative: Manual Trigger via Bot

Instead of (or in addition to) cron, users can manually trigger briefing generation by mentioning the briefing bot in Campfire:

```
@日报助手 生成昨天的日报
@日报助手 生成10月15日的日报
```

The cron job ensures briefings are always generated even if users forget.

## Logs Rotation

To prevent log files from growing too large, set up logrotate:

Create `/etc/logrotate.d/briefing-cron`:
```
/root/ai-knowledge/logs/briefing-cron.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

## Backup Consideration

Briefings are stored in `/root/ai-knowledge/company_kb/briefings/`.

This directory should be included in regular backups since it contains historical team activity records.

---

**Last Updated:** October 15, 2025
**Version:** 0.2.3
**Owner:** Engineering Team
