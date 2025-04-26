
from aiogram import F, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

def register_handlers(dp: Dispatcher):
    """Register all client handlers"""
    
    # Import and register main client handlers
    main_router = Router()
    
    @main_router.message(Command("start"))
    async def cmd_start(message: Message, user: dict):
        """Handle /start command"""
        from keyboards import client_keyboards
        
        # Check if user is admin for subscription status
        has_subscription = True
        if user["role"] == "admin":
            from utils.db_api import subscription_commands
            subscription_status = await subscription_commands.check_subscription_status(message.from_user.id)
            has_subscription = subscription_status["active"]
        
        greeting = f"Добро пожаловать, {user['full_name']}!"
        
        if user["role"] == "admin":
            if has_subscription:
                greeting += "\nУ вас активная подписка."
            else:
                greeting += "\nУ вас нет активной подписки."
        
        await message.answer(greeting, 
                            reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], has_subscription))
    
    @main_router.message(Command("help"))
    async def cmd_help(message: Message, user: dict):
        """Handle /help command"""
        from keyboards import client_keyboards
        
        help_text = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать справку\n"
            "/book - Записаться на услугу\n"
            "/appointments - Посмотреть свои записи\n"
        )
        
        if user["role"] == "admin":
            help_text += (
                "/subscription - Управление подпиской\n"
                "/admin - Панель администратора\n"
            )
        
        # Check if user is admin for subscription status
        has_subscription = True
        if user["role"] == "admin":
            from utils.db_api import subscription_commands
            subscription_status = await subscription_commands.check_subscription_status(message.from_user.id)
            has_subscription = subscription_status["active"]
        
        await message.answer(help_text, 
                            reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], has_subscription))
    
    @main_router.callback_query(F.data == "help")
    async def help_button(callback: CallbackQuery, user: dict):
        """Handle help button"""
        help_text = (
            "Доступные команды:\n"
            "/start - Начать работу с ботом\n"
            "/help - Показать справку\n"
            "/book - Записаться на услугу\n"
            "/appointments - Посмотреть свои записи\n"
        )
        
        if user["role"] == "admin":
            help_text += (
                "/subscription - Управление подпиской\n"
                "/admin - Панель администратора\n"
            )
        
        await callback.message.edit_text(help_text)
        await callback.answer()
    
    @main_router.callback_query(F.data == "back_to_main")
    async def back_to_main(callback: CallbackQuery, user: dict, has_subscription: bool):
        """Handle back to main menu button"""
        from keyboards import client_keyboards
        
        await callback.message.edit_text("Главное меню:", 
                                      reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], has_subscription))
        await callback.answer()
    
    dp.include_router(main_router)
    
    # Register the book commands router
    from .client_book_commands import router as book_router
    dp.include_router(book_router)
    
    # Register subscription router - ONLY FOR ADMINS
    from .client_subscription_commands import router as subscription_router
    dp.include_router(subscription_router)
    
    # Register finance router - ONLY FOR ADMINS
    from .client_finance_commands import router as finance_router
    dp.include_router(finance_router)
