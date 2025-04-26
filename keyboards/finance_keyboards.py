
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_finance_main_menu():
    """Get finance main menu keyboard"""
    buttons = [
        [InlineKeyboardButton(text="📊 Доход и прибыль", callback_data="finance_income")],
        [InlineKeyboardButton(text="💰 Расходы на услуги", callback_data="finance_services")],
        [InlineKeyboardButton(text="👥 Статистика клиентов", callback_data="finance_clients")],
        [InlineKeyboardButton(text="🔮 Прогноз доходов", callback_data="finance_forecast")],
        [InlineKeyboardButton(text="📈 Советы по бизнесу", callback_data="finance_tips")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_admin")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_period_menu():
    """Get finance period selection menu"""
    buttons = [
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="finance_period_today")],
        [InlineKeyboardButton(text="📅 Вчера", callback_data="finance_period_yesterday")],
        [InlineKeyboardButton(text="📅 Текущая неделя", callback_data="finance_period_week")],
        [InlineKeyboardButton(text="📅 Текущий месяц", callback_data="finance_period_month")],
        [InlineKeyboardButton(text="📅 Последние 30 дней", callback_data="finance_period_30days")],
        [InlineKeyboardButton(text="🗓 Выбрать другой период", callback_data="finance_period_custom")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_services_menu(services):
    """Get finance services menu"""
    buttons = []
    
    # Display services in chunks of up to 5
    for i in range(0, len(services), 5):
        chunk = services[i:i+5]
        row = []
        for service in chunk:
            service_id = service["id"]
            service_name = service["name"]
            # Truncate long service names
            if len(service_name) > 30:
                service_name = service_name[:27] + "..."
            row.append(InlineKeyboardButton(text=service_name, callback_data=f"finance_service_{service_id}"))
        buttons.append(row)
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_service_cost_menu(service_id):
    """Get finance service cost menu"""
    buttons = [
        [InlineKeyboardButton(text="✏️ Стоимость материалов", callback_data=f"edit_material_cost_{service_id}")],
        [InlineKeyboardButton(text="✏️ Стоимость времени", callback_data=f"edit_time_cost_{service_id}")],
        [InlineKeyboardButton(text="✏️ Другие расходы", callback_data=f"edit_other_cost_{service_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к услугам", callback_data="back_to_finance_services")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_clients_menu():
    """Get finance clients menu"""
    buttons = [
        [InlineKeyboardButton(text="👑 VIP клиенты", callback_data="finance_vip_clients")],
        [InlineKeyboardButton(text="📊 Активность клиентов", callback_data="finance_client_activity")],
        [InlineKeyboardButton(text="🔍 Найти клиента", callback_data="finance_find_client")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_vip_clients_menu(vip_clients):
    """Get VIP clients menu"""
    buttons = []
    
    # Display VIP clients in chunks of up to 5
    for i in range(0, len(vip_clients), 5):
        chunk = vip_clients[i:i+5]
        row = []
        for client in chunk:
            client_id = client["client_id"]
            client_name = client["name"]
            # Truncate long client names
            if len(client_name) > 30:
                client_name = client_name[:27] + "..."
            row.append(InlineKeyboardButton(text=client_name, callback_data=f"finance_client_{client_id}"))
        buttons.append(row)
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance_clients")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_client_stats_menu(client_id):
    """Get client stats menu"""
    buttons = [
        [InlineKeyboardButton(text="📝 Добавить заметку", callback_data=f"add_client_note_{client_id}")],
        [InlineKeyboardButton(text="🔔 Отправить напоминание", callback_data=f"send_client_reminder_{client_id}")],
        [InlineKeyboardButton(text="⬅️ Назад к VIP клиентам", callback_data="back_to_finance_vip")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_tips_menu():
    """Get finance tips menu"""
    buttons = [
        [InlineKeyboardButton(text="🚀 Как увеличить прибыль", callback_data="tip_increase_profit")],
        [InlineKeyboardButton(text="💼 Как оптимизировать расходы", callback_data="tip_optimize_costs")],
        [InlineKeyboardButton(text="👥 Как удержать клиентов", callback_data="tip_retain_clients")],
        [InlineKeyboardButton(text="🔄 Как получать больше отзывов", callback_data="tip_get_reviews")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_finance_forecast_menu():
    """Get finance forecast menu"""
    buttons = [
        [InlineKeyboardButton(text="📅 30 дней", callback_data="forecast_30_days")],
        [InlineKeyboardButton(text="📅 60 дней", callback_data="forecast_60_days")],
        [InlineKeyboardButton(text="📅 90 дней", callback_data="forecast_90_days")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def get_back_to_finance_keyboard():
    """Get back to finance keyboard"""
    buttons = [
        [InlineKeyboardButton(text="⬅️ Назад в финансовый раздел", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Меню напоминаний
async def get_reminder_menu(client_id):
    """Get reminder menu options"""
    buttons = [
        [InlineKeyboardButton(text="✅ Позвонил(а)", callback_data=f"reminder_called_{client_id}")],
        [InlineKeyboardButton(text="📱 Написал(а) в WhatsApp", callback_data=f"reminder_messaged_{client_id}")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data=f"reminder_cancel_{client_id}")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Меню бота-консультанта
async def get_finance_setup_menu():
    """Get finance setup menu"""
    buttons = [
        [InlineKeyboardButton(text="▶️ Начать настройку", callback_data="start_finance_setup")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Меню для этапов настройки
async def get_setup_step_menu(current_step):
    """Get setup step menu"""
    buttons = [
        [InlineKeyboardButton(text="▶️ Продолжить", callback_data=f"setup_continue_{current_step}")],
        [InlineKeyboardButton(text="⏭ Пропустить этот шаг", callback_data=f"setup_skip_{current_step}")],
        [InlineKeyboardButton(text="❌ Отмена настройки", callback_data="back_to_finance")]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
