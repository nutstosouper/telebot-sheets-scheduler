
# Add these functions to the client_keyboards.py file

async def get_subscription_menu_keyboard(has_active_subscription=False):
    """Get subscription menu keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    # Status button
    buttons.append([InlineKeyboardButton(text="📅 Статус подписки", callback_data="subscription_status")])
    
    # Buy button (if no active subscription)
    if not has_active_subscription:
        buttons.append([InlineKeyboardButton(text="💳 Приобрести подписку", callback_data="buy_subscription")])
    
    # Referral program
    buttons.append([InlineKeyboardButton(text="🎁 Реферальная программа", callback_data="referral_program")])
    
    # Enter referral code
    buttons.append([InlineKeyboardButton(text="📝 Ввести реферальный код", callback_data="enter_referral")])
    
    # Back to main menu
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_back_to_subscription_keyboard():
    """Get back to subscription keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_subscription")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subscription_plans_keyboard():
    """Get subscription plans keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="1 месяц - 1999 руб", callback_data="plan_1")],
        [InlineKeyboardButton(text="2 месяца - 3998 руб", callback_data="plan_2")],
        [InlineKeyboardButton(text="3 месяца - 5697 руб (-5%)", callback_data="plan_3")],
        [InlineKeyboardButton(text="6 месяцев - 10794 руб (-10%)", callback_data="plan_6")],
        [InlineKeyboardButton(text="12 месяцев - 19190 руб (-20%)", callback_data="plan_12")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_subscription")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_subscription_confirm_keyboard():
    """Get subscription confirmation keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_subscription")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="back_to_subscription")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Make sure to update the main menu keyboard to include a subscription button
async def get_main_menu_keyboard():
    """Get main menu keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from utils.db_api import user_commands
    
    buttons = [
        [InlineKeyboardButton(text="Записаться", callback_data="book_service")],
        [InlineKeyboardButton(text="Мои записи", callback_data="my_appointments")]
    ]
    
    # Проверяем роль пользователя, чтобы добавить соответствующие кнопки
    try:
        user_id = None
        # Этот код будет заменен на получение user_id из контекста
        # Для работы этой функции предполагается, что user_id передается при вызове
        
        if user_id:
            user = await user_commands.get_user(user_id)
            if user and user.get("role") == "admin":
                buttons.append([InlineKeyboardButton(text="📊 Финансы и аналитика", callback_data="finance_menu")])
                buttons.append([InlineKeyboardButton(text="📱 Подписка", callback_data="subscription_menu")])
    except:
        pass
        
    buttons.append([InlineKeyboardButton(text="Помощь", callback_data="help")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
