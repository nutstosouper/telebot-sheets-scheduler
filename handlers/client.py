
from aiogram import F, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

def register_handlers(dp: Dispatcher):
    """Register all client handlers"""
    
    # First, register other client handlers that come before book_router
    # (if there are any)
    
    # Import and register the book commands router
    from .client_book_commands import router as book_router
    dp.include_router(book_router)
    
    # Register subscription router
    from .client_subscription_commands import router as subscription_router
    dp.include_router(subscription_router)
    
    # Register finance router
    from .client_finance_commands import router as finance_router
    dp.include_router(finance_router)
    
    # Register other client handlers below book_router
    # ...
