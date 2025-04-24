
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import modules
from handlers import client, admin, ceo
from middlewares.role_middleware import RoleMiddleware
from utils.db_api import google_sheets, service_commands
from utils.appointment_reminders import start_reminder_scheduler

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())

# Setup middlewares
dp.message.middleware(RoleMiddleware())
dp.callback_query.middleware(RoleMiddleware())

# Register bot commands
async def set_commands():
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help"),
        BotCommand(command="/book", description="Book a service"),
        BotCommand(command="/appointments", description="View your appointments"),
        BotCommand(command="/admin", description="Admin panel (restricted)"),
        BotCommand(command="/ceo", description="CEO panel (restricted)")
    ]
    await bot.set_my_commands(commands)

# Register handlers
async def register_all_handlers():
    client.register_handlers(dp)
    admin.register_handlers(dp)
    ceo.register_handlers(dp)

# Main function to start the bot
async def main():
    try:
        # Initialize Google Sheets
        logging.info("Initializing Google Sheets connection...")
        await google_sheets.setup()
        logging.info("Google Sheets connection established successfully")
        
        # Initialize template data for services
        logging.info("Initializing template service data...")
        await service_commands.initialize_template_data()
        logging.info("Template service data initialized successfully")
        
        # Register all handlers
        await register_all_handlers()
        
        # Set bot commands
        await set_commands()
        
        # Start appointment reminder scheduler
        # Get admin IDs from environment variable (comma-separated list)
        admin_ids = os.getenv('ADMIN_IDS', '').split(',')
        admin_ids = [int(admin_id.strip()) for admin_id in admin_ids if admin_id.strip().isdigit()]
        
        if admin_ids:
            logging.info(f"Starting appointment reminder scheduler for admins: {admin_ids}")
            asyncio.create_task(start_reminder_scheduler(bot, admin_ids))
        else:
            logging.warning("No admin IDs configured for appointment reminders. Set ADMIN_IDS in .env file.")
        
        # Start polling
        logging.info("Starting bot")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error starting bot: {str(e)}")
        if "MalformedError" in str(e):
            logging.error("Your Google credentials file appears to be invalid. Please verify it contains all required fields.")
            logging.error("Run the verify_credentials.py script to check your credentials file")
        elif "FileNotFoundError" in str(e):
            logging.error("Make sure your .env file contains the correct path to your credentials file")
        elif "SPREADSHEET_ID" in str(e):
            logging.error("Make sure your .env file contains your Google Spreadsheet ID")
        else:
            logging.error("If the error persists, check your internet connection and Google API access")

if __name__ == '__main__':
    asyncio.run(main())
