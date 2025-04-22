
# This file contains keyboard layouts for admin interactions in the Telegram bot

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    """Generate the main admin keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🛠️ Управление услугами",
        callback_data="admin_services"
    )
    keyboard.button(
        text="👨‍💼 Управление мастерами",
        callback_data="admin_masters"
    )
    keyboard.button(
        text="📅 Управление записями",
        callback_data="admin_appointments"
    )
    keyboard.button(
        text="🎁 Управление спец. предложениями",
        callback_data="admin_offers"
    )
    keyboard.button(
        text="📊 Статистика",
        callback_data="admin_statistics"
    )
    keyboard.button(
        text="📁 Управление категориями",
        callback_data="admin_categories"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_services_management_keyboard():
    """Generate services management keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить услугу",
        callback_data="add_service"
    )
    keyboard.button(
        text="📋 Просмотреть услуги",
        callback_data="view_services"
    )
    keyboard.button(
        text="🔙 Назад в панель администратора",
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_offers_management_keyboard():
    """Generate special offers management keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить спец. предложение",
        callback_data="add_offer"
    )
    keyboard.button(
        text="📋 Просмотреть спец. предложения",
        callback_data="view_offers"
    )
    keyboard.button(
        text="🔙 Назад в панель администратора",
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_categories_management_keyboard():
    """Generate categories management keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить категорию",
        callback_data="add_category"
    )
    keyboard.button(
        text="📋 Просмотреть категории",
        callback_data="view_categories"
    )
    keyboard.button(
        text="🔙 Назад в панель администратора",
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_services_keyboard(services):
    """Generate a keyboard with all services"""
    keyboard = InlineKeyboardBuilder()
    for service in services:
        keyboard.button(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"admin_view_service_{service['id']}"
        )
    
    keyboard.button(
        text="🔙 Назад",
        callback_data="admin_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_offers_keyboard(offers):
    """Generate a keyboard with all special offers"""
    keyboard = InlineKeyboardBuilder()
    for offer in offers:
        keyboard.button(
            text=f"{offer['name']} - {offer['price']}",
            callback_data=f"admin_view_offer_{offer['id']}"
        )
    
    keyboard.button(
        text="🔙 Назад",
        callback_data="admin_offers"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_categories_keyboard(categories):
    """Generate a keyboard with all categories"""
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.button(
            text=f"{category['name']}",
            callback_data=f"admin_view_category_{category['id']}"
        )
    
    keyboard.button(
        text="🔙 Назад",
        callback_data="admin_categories"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_service_actions_keyboard(service_id):
    """Generate actions keyboard for a service"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать",
        callback_data=f"edit_service_{service_id}"
    )
    keyboard.button(
        text="❌ Удалить",
        callback_data=f"delete_service_confirm_{service_id}"
    )
    keyboard.button(
        text="🔙 Назад к списку услуг",
        callback_data="view_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_offer_actions_keyboard(offer_id):
    """Generate actions keyboard for a special offer"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать",
        callback_data=f"edit_offer_{offer_id}"
    )
    keyboard.button(
        text="❌ Удалить",
        callback_data=f"delete_offer_confirm_{offer_id}"
    )
    keyboard.button(
        text="🔙 Назад к списку предложений",
        callback_data="view_offers"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_category_actions_keyboard(category_id):
    """Generate actions keyboard for a category"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать",
        callback_data=f"edit_category_{category_id}"
    )
    keyboard.button(
        text="❌ Удалить",
        callback_data=f"delete_category_confirm_{category_id}"
    )
    keyboard.button(
        text="🔙 Назад к списку категорий",
        callback_data="view_categories"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_service_keyboard(service_id):
    """Generate edit options keyboard for a service"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Название",
        callback_data=f"edit_service_name_{service_id}"
    )
    keyboard.button(
        text="✏️ Описание",
        callback_data=f"edit_service_description_{service_id}"
    )
    keyboard.button(
        text="✏️ Цена",
        callback_data=f"edit_service_price_{service_id}"
    )
    keyboard.button(
        text="✏️ Длительность",
        callback_data=f"edit_service_duration_{service_id}"
    )
    keyboard.button(
        text="✏️ Категория",
        callback_data=f"edit_service_category_{service_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_offer_keyboard(offer_id):
    """Generate edit options keyboard for an offer"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Название",
        callback_data=f"edit_offer_name_{offer_id}"
    )
    keyboard.button(
        text="✏️ Описание",
        callback_data=f"edit_offer_description_{offer_id}"
    )
    keyboard.button(
        text="✏️ Цена",
        callback_data=f"edit_offer_price_{offer_id}"
    )
    keyboard.button(
        text="✏️ Длительность",
        callback_data=f"edit_offer_duration_{offer_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_offer_{offer_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_category_keyboard(category_id):
    """Generate edit options keyboard for a category"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Название",
        callback_data=f"edit_category_name_{category_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_category_{category_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_confirm_delete_keyboard(item_id, item_type="service"):
    """Generate confirmation keyboard for deletion"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, удалить",
        callback_data=f"confirm_delete_{item_type}_{item_id}"
    )
    keyboard.button(
        text="❌ Нет, отмена",
        callback_data=f"admin_view_{item_type}_{item_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_masters_management_keyboard():
    """Generate masters management keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить мастера",
        callback_data="add_master"
    )
    keyboard.button(
        text="📋 Просмотреть мастеров",
        callback_data="view_masters_admin"
    )
    keyboard.button(
        text="🔙 Назад в панель администратора",
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_masters_keyboard(masters):
    """Generate a keyboard with all masters"""
    keyboard = InlineKeyboardBuilder()
    for master in masters:
        keyboard.button(
            text=f"{master['name']}",
            callback_data=f"admin_view_master_{master['id']}"
        )
    
    keyboard.button(
        text="🔙 Назад",
        callback_data="admin_masters"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_master_actions_keyboard(master_id):
    """Generate actions keyboard for a master"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать",
        callback_data=f"edit_master_{master_id}"
    )
    keyboard.button(
        text="📊 Статистика",
        callback_data=f"master_statistics_{master_id}"
    )
    keyboard.button(
        text="📱 Управление уведомлениями",
        callback_data=f"master_notifications_{master_id}"
    )
    keyboard.button(
        text="📅 Управление расписанием",
        callback_data=f"master_schedule_{master_id}"
    )
    keyboard.button(
        text="❌ Удалить",
        callback_data=f"delete_master_confirm_{master_id}"
    )
    keyboard.button(
        text="🔙 Назад к списку мастеров",
        callback_data="view_masters_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_master_keyboard(master_id):
    """Generate edit options keyboard for a master"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Имя",
        callback_data=f"edit_master_name_{master_id}"
    )
    keyboard.button(
        text="✏️ Telegram",
        callback_data=f"edit_master_telegram_{master_id}"
    )
    keyboard.button(
        text="✏️ Адрес",
        callback_data=f"edit_master_address_{master_id}"
    )
    keyboard.button(
        text="📍 Геолокация",
        callback_data=f"edit_master_location_{master_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_master_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_master_notification_keyboard(master):
    """Generate notification settings keyboard for a master"""
    status = "Выключить" if master.get('notification_enabled', True) else "Включить"
    callback = "disable" if master.get('notification_enabled', True) else "enable"
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text=f"🔔 {status} уведомления",
        callback_data=f"{callback}_notifications_{master['id']}"
    )
    keyboard.button(
        text="⏰ Настроить время напоминаний",
        callback_data=f"configure_reminders_{master['id']}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_master_{master['id']}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_reminder_settings_keyboard(master_id):
    """Generate reminder settings keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="⏰ 1 час до записи",
        callback_data=f"toggle_reminder_1h_{master_id}"
    )
    keyboard.button(
        text="⏰ 2 часа до записи",
        callback_data=f"toggle_reminder_2h_{master_id}"
    )
    keyboard.button(
        text="⏰ 1 день до записи",
        callback_data=f"toggle_reminder_1d_{master_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"master_notifications_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_master_schedule_keyboard(master_id):
    """Generate schedule management keyboard for a master"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="⏰ Установить рабочее время",
        callback_data=f"set_working_hours_{master_id}"
    )
    keyboard.button(
        text="📅 Добавить выходной день",
        callback_data=f"add_day_off_{master_id}"
    )
    keyboard.button(
        text="📆 Управление выходными",
        callback_data=f"manage_days_off_{master_id}"
    )
    keyboard.button(
        text="🔙 Назад",
        callback_data=f"admin_view_master_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_appointments_keyboard(appointments):
    """Generate a keyboard with all appointments grouped by date"""
    keyboard = InlineKeyboardBuilder()
    
    # Group appointments by date
    appointments_by_date = {}
    for appointment in appointments:
        date = appointment.get('date')
        if date not in appointments_by_date:
            appointments_by_date[date] = []
        appointments_by_date[date].append(appointment)
    
    # Sort dates
    sorted_dates = sorted(appointments_by_date.keys())
    
    # Add date buttons
    for date in sorted_dates:
        count = len(appointments_by_date[date])
        keyboard.button(
            text=f"📅 {date} ({count} записей)",
            callback_data=f"admin_appointments_date_{date}"
        )
    
    keyboard.button(
        text="🔙 Назад в панель администратора",
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_date_appointments_admin_keyboard(appointments, date):
    """Generate a keyboard with appointments for a specific date"""
    keyboard = InlineKeyboardBuilder()
    
    for appointment in appointments:
        status_text = {
            'confirmed': '✅ Подтверждено',
            'canceled': '❌ Отменено',
            'completed': '✓ Выполнено',
            'paid': '💰 Оплачено',
            'pending': '⏳ Ожидает подтверждения'
        }.get(appointment.get('status'), appointment.get('status', 'Неизвестно'))
        
        # Get time and client info
        time = appointment.get('time', 'Нет времени')
        user_id = appointment.get('user_id', 'Нет ID')
        
        keyboard.button(
            text=f"{time} - {status_text} (Клиент: {user_id})",
            callback_data=f"admin_view_appointment_{appointment.get('id')}"
        )
    
    keyboard.button(
        text="🔙 Назад к списку дат",
        callback_data="admin_appointments"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointment_actions_keyboard(appointment_id, status):
    """Generate actions keyboard for an appointment"""
    keyboard = InlineKeyboardBuilder()
    
    # Add status change buttons based on current status
    if status != 'canceled':
        keyboard.button(
            text="❌ Отменить запись",
            callback_data=f"admin_cancel_appointment_{appointment_id}"
        )
    
    if status != 'completed' and status != 'canceled':
        keyboard.button(
            text="✓ Отметить как выполненную",
            callback_data=f"mark_completed_{appointment_id}"
        )
    
    if status == 'completed' and status != 'paid':
        keyboard.button(
            text="💰 Отметить как оплаченную",
            callback_data=f"mark_paid_{appointment_id}"
        )
    
    if status == 'pending':
        keyboard.button(
            text="✅ Подтвердить запись",
            callback_data=f"admin_confirm_appointment_{appointment_id}"
        )
    
    # Set payment method buttons
    if status != 'canceled' and status != 'paid':
        keyboard.button(
            text="💵 Оплата наличными",
            callback_data=f"set_payment_cash_{appointment_id}"
        )
        keyboard.button(
            text="💳 Оплата картой",
            callback_data=f"set_payment_card_{appointment_id}"
        )
        keyboard.button(
            text="📱 Оплата переводом",
            callback_data=f"set_payment_transfer_{appointment_id}"
        )
    
    keyboard.button(
        text="🔙 Назад к списку записей",
        callback_data="admin_appointments"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_cancel_confirmation_keyboard(appointment_id):
    """Generate confirmation keyboard for appointment cancellation"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, отменить запись",
        callback_data=f"confirm_cancel_{appointment_id}"
    )
    keyboard.button(
        text="❌ Нет, оставить как есть",
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_back_to_admin_keyboard():
    """Generate a keyboard to go back to admin panel"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔙 Вернуться в панель администратора",
        callback_data="back_to_admin"
    )
    return keyboard.as_markup()
