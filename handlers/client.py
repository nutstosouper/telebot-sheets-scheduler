
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

async def cmd_start(message: Message):
    """Handle the /start command"""
    await message.answer(f"Hello, {message.from_user.first_name}! Welcome to our service bot.")

async def cmd_help(message: Message):
    """Handle the /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/book - Book a service
/appointments - View your appointments
"""
    await message.answer(help_text)

async def cmd_book(message: Message):
    """Handle the /book command"""
    await message.answer("This feature is not implemented yet. Coming soon!")

async def cmd_appointments(message: Message):
    """Handle the /appointments command"""
    await message.answer("This feature is not implemented yet. Coming soon!")

def register_handlers(dp: Dispatcher):
    """Register client handlers"""
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_book, Command("book"))
    dp.message.register(cmd_appointments, Command("appointments"))
