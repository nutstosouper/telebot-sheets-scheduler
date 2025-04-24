from aiogram import F, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from .client_book_commands import router as book_router

def register_handlers(dp: Dispatcher):
    """Register all client handlers"""
    
    # Register the book commands router
    dp.include_router(book_router)
    
    # Register other client handlers
    # ...
    
    # Add /book command handler separately if needed
    @dp.message(Command("book"))
    async def book_command_handler(message: Message):
        """Forward to the actual book command handler"""
        from .client_book_commands import book_command
        await book_command(message)
