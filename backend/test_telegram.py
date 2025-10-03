import asyncio
import os
import django
import datetime
from telegram.ext import Application
from django.conf import settings

# -------------------------------
# Setup Django
# -------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

# -------------------------------
# Main async function
# -------------------------------
async def test_notification():
    try:
        print(f"Using bot token: {settings.TELEGRAM_BOT_TOKEN[:10]}...")
        print(f"Using chat ID: {settings.TELEGRAM_CHAT_ID}")
        print(f"Using Django TIME_ZONE: {settings.TIME_ZONE}")

        # Current time (no JobQueue needed)
        from zoneinfo import ZoneInfo
        current_time = datetime.datetime.now(ZoneInfo(settings.TIME_ZONE))
        print(f"Current time: {current_time}")

        # Build Telegram application WITHOUT JobQueue
        application = Application.builder()\
            .token(settings.TELEGRAM_BOT_TOKEN)\
            .build()  # ✅ skip job_queue_timezone

        # Send test message
        await application.bot.send_message(
            chat_id=settings.TELEGRAM_CHAT_ID,
            text=f"✅ Test message from hsrr_digital at {current_time}"
        )
        print("✅ Test message sent successfully")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

# -------------------------------
# Entry point
# -------------------------------
if __name__ == "__main__":
    asyncio.run(test_notification())
