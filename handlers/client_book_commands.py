
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from keyboards.client_keyboards import get_main_menu_keyboard

# Create router
router = Router()

@router.message(Command("book"))
async def book_command(message: Message):
    """Handle /book command to start booking process"""
    await message.answer(
        "Добро пожаловать в систему записи на услуги. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
