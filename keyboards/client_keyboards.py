
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

# Make sure to update the main menu keyboard to include a subscription button only for admins
async def get_main_menu_keyboard(user_role="client", has_subscription=True):
    """Get main menu keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="Записаться", callback_data="book_service")],
        [InlineKeyboardButton(text="Мои записи", callback_data="my_appointments")]
    ]
    
    # Добавляем кнопки для админа
    if user_role == "admin":
        if has_subscription:
            buttons.append([InlineKeyboardButton(text="📊 Финансы и аналитика", callback_data="finance_menu")])
        
        buttons.append([InlineKeyboardButton(text="📱 Подписка", callback_data="subscription_menu")])
    
    buttons.append([InlineKeyboardButton(text="Помощь", callback_data="help")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Add the missing categories keyboard function
async def get_categories_keyboard():
    """Get categories keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from utils.db_api import service_commands
    
    # Get all categories
    categories = await service_commands.get_categories()
    
    # Create buttons for each category
    buttons = []
    for category in categories:
        buttons.append([InlineKeyboardButton(
            text=category.get('name', 'Unknown'), 
            callback_data=category.get('name', 'unknown')
        )])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Add other missing keyboard functions 
async def get_services_keyboard(services):
    """Get services keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    # Add a button for each service
    for service in services:
        service_id = service.get('id')
        service_name = service.get('name')
        service_price = service.get('price', '0')
        
        button_text = f"{service_name} - {service_price} руб."
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=service_id)])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_masters_keyboard(masters):
    """Get masters keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    # Add a button for each master
    for master in masters:
        master_id = master.get('id')
        master_name = master.get('name')
        
        buttons.append([InlineKeyboardButton(text=master_name, callback_data=master_id)])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_services")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_times_keyboard(times):
    """Get available times keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    # Add a button for each time
    for time in times:
        buttons.append([InlineKeyboardButton(text=time, callback_data=time)])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_date")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_confirmation_keyboard():
    """Get confirmation keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = [
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_appointments_keyboard(appointments):
    """Get appointments keyboard"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    buttons = []
    
    # Group appointments by date
    appointments_by_date = {}
    for appointment in appointments:
        date = appointment.get('date')
        if date not in appointments_by_date:
            appointments_by_date[date] = []
        appointments_by_date[date].append(appointment)
    
    # Sort dates
    sorted_dates = sorted(appointments_by_date.keys())
    
    # Add a button for each date
    for date in sorted_dates:
        date_appointments = appointments_by_date[date]
        button_text = f"{date} ({len(date_appointments)} записей)"
        buttons.append([InlineKeyboardButton(text=button_text, callback_data=f"date_{date}")])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
