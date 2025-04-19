
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Import modules
from handlers import client, admin, ceo
from middlewares.role_middleware import RoleMiddleware
from utils.db_api import google_sheets

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()  # В aiogram 3.x инициализация диспетчера изменилась

# Setup middlewares
dp.message.middleware(RoleMiddleware())
dp.callback_query.middleware(RoleMiddleware())

# Register bot commands
async def set_commands():
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Get help"),
        BotCommand(command="/book", description="Book a service"),
        BotCommand(command="/appointments", description="View your appointments")
    ]
    await bot.set_my_commands(commands)

# Register handlers
async def register_all_handlers():
    client.register_handlers(dp)
    admin.register_handlers(dp)
    ceo.register_handlers(dp)

# Main function to start the bot
async def main():
    # Initialize Google Sheets
    await google_sheets.setup()
    
    # Register all handlers
    await register_all_handlers()
    
    # Set bot commands
    await set_commands()
    
    # Start polling
    logging.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
