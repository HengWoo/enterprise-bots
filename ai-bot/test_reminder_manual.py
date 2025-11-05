#!/usr/bin/env python3
"""Manual test for reminder delivery"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.reminder_scheduler import create_scheduler

# Create scheduler with testing mode
scheduler = create_scheduler(
    context_dir="user_contexts",
    campfire_url="https://chat.smartice.ai",
    bot_key="10-vWgb0YVbUSYs",
    testing=True
)

print("=" * 60)
print("Manual Reminder Check Test")
print("=" * 60)
print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Context directory: {scheduler.context_dir}")
print(f"Testing mode: {scheduler.testing}")
print()

# Run check
print("Running check_and_send_reminders()...")
print("-" * 60)
scheduler.check_and_send_reminders()
print("-" * 60)
print()

# Check result
import json
reminder_file = Path("user_contexts/user_1/reminders.json")
if reminder_file.exists():
    with open(reminder_file) as f:
        data = json.load(f)

    print("Reminder status after check:")
    for reminder in data.get('reminders', []):
        print(f"  ID: {reminder['id']}")
        print(f"  Text: {reminder['text']}")
        print(f"  Remind at: {reminder['remind_at']}")
        print(f"  Status: {reminder['status']}")
        print(f"  Triggered at: {reminder.get('triggered_at', 'N/A')}")
        print()
else:
    print("ERROR: Reminder file not found!")
