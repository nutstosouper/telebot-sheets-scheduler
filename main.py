
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from handlers import client, admin, ceo
from middlewares.role_middleware import RoleMiddleware
from utils.db_api import google_sheets

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'))

# For aiogram 2.x:
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)  # Corrected initialization syntax

# Setup middlewares
dp.middleware.setup(RoleMiddleware())

# Register handlers
client.register_handlers(dp)
admin.register_handlers(dp)
ceo.register_handlers(dp)

# Register bot commands
async def set_commands():
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help"),
        BotCommand(command="/book", description="Book a service"),
        BotCommand(command="/appointments", description="View your appointments")
    ]
    await bot.set_my_commands(commands)

# Main function to start the bot
async def main():
    # Initialize Google Sheets
    await google_sheets.setup()
    
    # Set bot commands
    await set_commands()
    
    # Start polling
    await dp.start_polling()

if __name__ == '__main__':
    from aiogram import executor
    
    # Initialize Google Sheets before starting
    executor.start_polling(dp, on_startup=main)
