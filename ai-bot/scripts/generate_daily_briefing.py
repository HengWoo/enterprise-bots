#!/usr/bin/env python3
"""
Daily Briefing Generation Script (AI-Powered)

Triggers the Briefing Assistant bot to generate intelligent daily briefings.
The bot analyzes conversations and creates summaries using Claude AI.

Usage:
    python scripts/generate_daily_briefing.py [--date YYYY-MM-DD] [--room ROOM_ID]

Options:
    --date: Optional date to generate briefing for (defaults to yesterday)
    --room: Optional room ID to post briefing request to (defaults to room 1)

Cron setup (run at 9:00 AM daily):
    0 9 * * * cd /root/ai-service && /usr/bin/python3 scripts/generate_daily_briefing.py >> /var/lib/docker/volumes/ai-service_ai-knowledge/_data/logs/briefing-cron.log 2>&1
"""

import sys
import os
import argparse
import httpx
from datetime import datetime, timedelta


def main():
    """Main function to trigger briefing generation via Briefing Assistant bot"""

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Trigger daily briefing generation")
    parser.add_argument(
        "--date",
        type=str,
        help="Date to generate briefing for (YYYY-MM-DD). Defaults to yesterday."
    )
    parser.add_argument(
        "--room",
        type=int,
        default=1,
        help="Room ID to post briefing request to. Defaults to room 1 (All Hands)."
    )

    args = parser.parse_args()

    # Determine date (default to yesterday)
    if args.date:
        target_date = args.date
        print(f"[Cron] Triggering briefing for specified date: {target_date}")
    else:
        yesterday = datetime.now() - timedelta(days=1)
        target_date = yesterday.strftime("%Y-%m-%d")
        print(f"[Cron] Triggering briefing for yesterday: {target_date}")

    # Get configuration from environment
    campfire_url = os.environ.get("CAMPFIRE_URL", "https://chat.smartice.ai")
    briefing_bot_key = os.environ.get("BRIEFING_BOT_KEY", "11-cLwvq6mLx4WV")
    room_id = args.room

    # Construct webhook URL (internal container URL)
    webhook_url = "http://localhost:8000/webhook/briefing_assistant"

    # Construct message to trigger bot
    message = f"生成{target_date}的日报"

    # Prepare webhook payload
    payload = {
        "creator": {
            "id": 0,
            "name": "Cron Job"
        },
        "room": {
            "id": room_id,
            "name": "All Hands"
        },
        "content": message
    }

    print(f"[Cron] Posting briefing request to webhook...")
    print(f"[Cron]    URL: {webhook_url}")
    print(f"[Cron]    Room: {room_id}")
    print(f"[Cron]    Message: {message}")

    try:
        # Post to webhook (triggers Briefing Assistant bot)
        response = httpx.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10.0
        )

        if response.status_code == 200:
            print(f"[Cron] ✅ Briefing request accepted!")
            print(f"[Cron]    Briefing Assistant is now processing...")
            print(f"[Cron]    Check Campfire room #{room_id} for AI-generated briefing")
        else:
            print(f"[Cron] ⚠️  Warning: Webhook returned status {response.status_code}")
            print(f"[Cron]    Response: {response.text}")
            sys.exit(1)

    except httpx.TimeoutException:
        print(f"[Cron] ⚠️  Warning: Webhook request timed out (10s)")
        print(f"[Cron]    This is normal - briefing generation may take 30-60 seconds")
        print(f"[Cron]    Check Campfire room #{room_id} for results")
        # Exit success - timeout is expected for long-running tasks
        sys.exit(0)

    except Exception as e:
        print(f"[Cron] ❌ Error: Failed to trigger briefing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print(f"[Cron] 🎉 Daily briefing request submitted successfully!")
    print(f"[Cron]")
    print(f"[Cron] Next steps:")
    print(f"[Cron]   1. Briefing Assistant bot will analyze {target_date}'s conversations")
    print(f"[Cron]   2. AI will generate intelligent summary with key insights")
    print(f"[Cron]   3. Results will be posted to Campfire room #{room_id}")
    print(f"[Cron]   4. Briefing saved to: /app/ai-knowledge/company_kb/briefings/{target_date[:4]}/{target_date[5:7]}/")


if __name__ == "__main__":
    main()
