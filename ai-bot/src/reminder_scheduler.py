"""
Automated Reminder Delivery System

This module provides background task functionality to check and deliver
reminders at scheduled times. Reminders are stored in user-specific JSON files
and delivered via Campfire API when they become due.

Architecture:
- APScheduler runs check_and_send_reminders() every 1 minute
- Scans all user reminder files for pending reminders
- Posts notifications to Campfire when reminders are due
- Marks reminders as triggered to prevent duplicates

Author: Claude (AI Assistant)
Created: 2025-11-02
Version: 0.5.1
"""

import os
import json
import logging
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dateutil import parser as dateutil_parser
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """
    Manages automated reminder delivery.

    Scans user reminder files periodically and sends notifications
    for reminders that are due.
    """

    def __init__(
        self,
        context_dir: str,
        campfire_url: str,
        bot_key: str,
        testing: bool = False
    ):
        """
        Initialize reminder scheduler.

        Args:
            context_dir: Path to user_contexts directory
            campfire_url: Campfire base URL (e.g., https://chat.smartice.ai)
            bot_key: Bot authentication key
            testing: If True, skip actual HTTP requests
        """
        self.context_dir = Path(context_dir)
        self.campfire_url = campfire_url
        self.bot_key = bot_key
        self.testing = testing

        logger.info(f"[ReminderScheduler] Initialized")
        logger.info(f"[ReminderScheduler] Context dir: {self.context_dir}")
        logger.info(f"[ReminderScheduler] Campfire URL: {self.campfire_url}")
        logger.info(f"[ReminderScheduler] Testing mode: {self.testing}")

    def check_and_send_reminders(self):
        """
        Main check loop: scan all user reminders and send notifications for due reminders.

        This function is called by APScheduler every 1 minute.
        """
        logger.debug("[ReminderScheduler] Starting reminder check cycle")

        try:
            # Find all user directories
            if not self.context_dir.exists():
                logger.warning(f"[ReminderScheduler] Context directory does not exist: {self.context_dir}")
                return

            user_dirs = [d for d in self.context_dir.iterdir() if d.is_dir() and d.name.startswith('user_')]
            logger.debug(f"[ReminderScheduler] Found {len(user_dirs)} user directories")

            for user_dir in user_dirs:
                reminders_file = user_dir / "reminders.json"

                if not reminders_file.exists():
                    continue

                # Process reminders for this user
                self._process_user_reminders(reminders_file)

        except Exception as e:
            logger.error(f"[ReminderScheduler] Error in check cycle: {e}", exc_info=True)

    def _process_user_reminders(self, reminders_file: Path):
        """
        Process reminders for a single user.

        Args:
            reminders_file: Path to user's reminders.json file
        """
        try:
            # Load reminders
            with open(reminders_file, 'r') as f:
                data = json.load(f)

            reminders = data.get("reminders", [])
            pending_reminders = [r for r in reminders if r.get("status") == "pending"]

            if not pending_reminders:
                return

            logger.debug(f"[ReminderScheduler] Processing {len(pending_reminders)} pending reminders from {reminders_file}")

            # Check each pending reminder
            modified = False
            for reminder in pending_reminders:
                if self._is_reminder_due(reminder):
                    # Send notification
                    success = self._send_reminder_notification(reminder, reminders_file)

                    if success:
                        # Mark as triggered
                        reminder["status"] = "triggered"
                        reminder["triggered_at"] = datetime.now().isoformat()
                        modified = True
                        logger.info(f"[ReminderScheduler] Reminder #{reminder['id']} delivered successfully")
                    else:
                        logger.error(f"[ReminderScheduler] Failed to deliver reminder #{reminder['id']}")

            # Save if modified
            if modified:
                with open(reminders_file, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"[ReminderScheduler] Updated {reminders_file}")

        except Exception as e:
            logger.error(f"[ReminderScheduler] Error processing {reminders_file}: {e}", exc_info=True)

    def _is_reminder_due(self, reminder: Dict[str, Any]) -> bool:
        """
        Check if a reminder is due to be sent.

        Args:
            reminder: Reminder dictionary

        Returns:
            True if reminder should be sent now
        """
        try:
            remind_at_str = reminder.get("remind_at", "")
            remind_time = self._parse_remind_time(remind_at_str)

            if remind_time is None:
                logger.warning(f"[ReminderScheduler] Could not parse remind_at: {remind_at_str}")
                return False

            # Reminder is due if remind_time <= now
            now = datetime.now()
            is_due = remind_time <= now

            if is_due:
                logger.debug(f"[ReminderScheduler] Reminder #{reminder['id']} is due (scheduled: {remind_time}, now: {now})")

            return is_due

        except Exception as e:
            logger.error(f"[ReminderScheduler] Error checking if reminder is due: {e}", exc_info=True)
            return False

    def _parse_remind_time(self, remind_at: str) -> Optional[datetime]:
        """
        Parse remind_at string to datetime.

        Supports:
        - ISO 8601: "2025-11-02T14:30:00"
        - Standard formats: "2025-11-02 14:30", "2025-11-02 14:30:00"
        - Natural language: "明天上午10点", "2小时后", "下周一" (basic support)

        Args:
            remind_at: Time string

        Returns:
            datetime object or None if parsing fails
        """
        if not remind_at:
            return None

        try:
            # Try ISO 8601 / standard datetime formats first
            return dateutil_parser.parse(remind_at)
        except:
            pass

        # Try natural language parsing (basic Chinese support)
        try:
            now = datetime.now()
            remind_at_lower = remind_at.lower()

            # "X小时后" / "X hours later"
            if "小时后" in remind_at or "hours later" in remind_at_lower:
                hours = int(''.join(filter(str.isdigit, remind_at)))
                return now + timedelta(hours=hours)

            # "X分钟后" / "X minutes later"
            if "分钟后" in remind_at or "minutes later" in remind_at_lower:
                minutes = int(''.join(filter(str.isdigit, remind_at)))
                return now + timedelta(minutes=minutes)

            # "明天" / "tomorrow"
            if "明天" in remind_at or "tomorrow" in remind_at_lower:
                tomorrow = now + timedelta(days=1)
                # Default to 9:00 AM tomorrow if no time specified
                return tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)

            # "下周" / "next week"
            if "下周" in remind_at or "next week" in remind_at_lower:
                next_week = now + timedelta(days=7)
                return next_week.replace(hour=9, minute=0, second=0, microsecond=0)

            # If all else fails, try dateutil's fuzzy parsing
            return dateutil_parser.parse(remind_at, fuzzy=True)

        except Exception as e:
            logger.error(f"[ReminderScheduler] Failed to parse remind_at '{remind_at}': {e}")
            return None

    def _send_reminder_notification(self, reminder: Dict[str, Any], reminders_file: Path) -> bool:
        """
        Send reminder notification to Campfire.

        Args:
            reminder: Reminder dictionary
            reminders_file: Path to reminders file (used to extract user_id)

        Returns:
            True if notification sent successfully
        """
        try:
            # Extract user_id from reminders_file path
            # Path format: /path/to/user_contexts/user_{user_id}/reminders.json
            user_id = int(reminders_file.parent.name.replace('user_', ''))

            # Get room_id from reminder (if available) or use default
            # Note: In v0.5.1, we assume reminders are sent to the room where they were created
            # Future enhancement: Store room_id in reminder data
            room_id = reminder.get("room_id", 1)  # Default to room 1 if not specified

            # Format reminder message
            message = self._format_reminder_message(reminder)

            # Send to Campfire
            return self._post_to_campfire(room_id, message)

        except Exception as e:
            logger.error(f"[ReminderScheduler] Error sending notification: {e}", exc_info=True)
            return False

    def _format_reminder_message(self, reminder: Dict[str, Any]) -> str:
        """
        Format reminder as HTML message for Campfire.

        Args:
            reminder: Reminder dictionary

        Returns:
            HTML formatted reminder message
        """
        text = reminder.get("text", "")
        remind_at = reminder.get("remind_at", "")
        created_at = reminder.get("created_at", "")

        # Parse timestamps for display
        try:
            created_time = dateutil_parser.parse(created_at).strftime("%Y-%m-%d %H:%M")
        except:
            created_time = created_at

        html = f"""
<div style="border-left: 4px solid #4CAF50; padding: 12px 16px; background: #f8f9fa; border-radius: 4px; margin: 10px 0;">
    <h3 style="margin: 0 0 8px 0; color: #4CAF50; font-size: 16px;">⏰ 提醒 / Reminder</h3>
    <p style="margin: 8px 0; font-size: 15px; color: #333;"><strong>{text}</strong></p>
    <p style="margin: 4px 0; font-size: 13px; color: #666;">
        ⏱️ 设定时间 / Scheduled: {remind_at}<br>
        📅 创建于 / Created: {created_time}
    </p>
</div>
"""
        return html.strip()

    def _post_to_campfire(self, room_id: int, message: str) -> bool:
        """
        Post message to Campfire room (synchronous version for background task).

        Args:
            room_id: Room ID to post to
            message: HTML formatted message

        Returns:
            True if post succeeded
        """
        # Skip in testing mode
        if self.testing:
            logger.info(f"[ReminderScheduler] [TEST MODE] Would post to room {room_id}: {message[:100]}...")
            return True

        try:
            url = f"{self.campfire_url}/rooms/{room_id}/{self.bot_key}/messages"

            logger.info(f"[ReminderScheduler] Posting reminder to {url}")

            # Use synchronous httpx client (APScheduler background thread)
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    url,
                    content=message.encode('utf-8'),
                    headers={
                        'Content-Type': 'text/html; charset=utf-8'
                    }
                )

                if response.status_code in [200, 201]:
                    logger.info(f"[ReminderScheduler] Successfully posted to Campfire (status: {response.status_code})")
                    return True
                else:
                    logger.error(f"[ReminderScheduler] Campfire returned status {response.status_code}: {response.text}")
                    return False

        except Exception as e:
            logger.error(f"[ReminderScheduler] Error posting to Campfire: {e}", exc_info=True)
            return False


def create_scheduler(
    context_dir: str,
    campfire_url: str,
    bot_key: str,
    testing: bool = False
) -> ReminderScheduler:
    """
    Factory function to create ReminderScheduler instance.

    Args:
        context_dir: Path to user_contexts directory
        campfire_url: Campfire base URL
        bot_key: Bot authentication key
        testing: If True, skip actual HTTP requests

    Returns:
        ReminderScheduler instance
    """
    return ReminderScheduler(
        context_dir=context_dir,
        campfire_url=campfire_url,
        bot_key=bot_key,
        testing=testing
    )
