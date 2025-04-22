
# This file contains keyboard layouts for administrator interactions in the Telegram bot

from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    """Generate the main admin panel keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Управление услугами", 
        callback_data="admin_services"
    )
    keyboard.button(
        text="Управление записями", 
        callback_data="admin_appointments"
    )
    keyboard.button(
        text="Статистика", 
        callback_data="admin_stats"
    )
    keyboard.button(
        text="Управление мастерами", 
        callback_data="admin_masters"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_services_management_keyboard():
    """Generate a keyboard for service management options"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить услугу", 
        callback_data="add_service"
    )
    keyboard.button(
        text="📋 Просмотр всех услуг", 
        callback_data="view_services"
    )
    keyboard.button(
        text="🔙 Вернуться в панель администратора", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_service_actions_keyboard(service_id):
    """Generate a keyboard for actions on a specific service"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать услугу", 
        callback_data=f"edit_service_{service_id}"
    )
    keyboard.button(
        text="❌ Удалить услугу", 
        callback_data=f"delete_service_{service_id}"
    )
    keyboard.button(
        text="🔙 Вернуться к услугам", 
        callback_data="view_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_service_keyboard(service_id):
    """Generate a keyboard for editing service fields"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Изменить название", 
        callback_data=f"edit_service_name_{service_id}"
    )
    keyboard.button(
        text="✏️ Изменить описание", 
        callback_data=f"edit_service_description_{service_id}"
    )
    keyboard.button(
        text="✏️ Изменить цену", 
        callback_data=f"edit_service_price_{service_id}"
    )
    keyboard.button(
        text="✏️ Изменить длительность", 
        callback_data=f"edit_service_duration_{service_id}"
    )
    keyboard.button(
        text="🔙 Вернуться к услуге", 
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_services_keyboard(services):
    """Generate a keyboard listing all services"""
    keyboard = InlineKeyboardBuilder()
    for service in services:
        keyboard.button(
            text=f"{service['name']} - {service['price']}", 
            callback_data=f"admin_view_service_{service['id']}"
        )
    
    keyboard.button(
        text="🔙 Вернуться к управлению услугами", 
        callback_data="admin_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_confirm_delete_keyboard(service_id):
    """Generate confirmation keyboard for service deletion"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, удалить", 
        callback_data=f"confirm_delete_service_{service_id}"
    )
    keyboard.button(
        text="❌ Нет, отменить", 
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_appointments_keyboard(appointments):
    """Generate a keyboard displaying all appointments"""
    keyboard = InlineKeyboardBuilder()
    
    # Format status for display
    status_map = {
        'confirmed': '✅ Подтверждено',
        'canceled': '❌ Отменено',
        'completed': '✓ Выполнено',
        'paid': '💰 Оплачено'
    }
    
    for appointment in appointments:
        # Ensure we're using standardized keys
        appt_id = appointment.get('id')
        date = appointment.get('date')
        time = appointment.get('time')
        status = appointment.get('status')
        
        # Format status
        status_display = status_map.get(status, status) if status else "Неизвестно"
        
        if appt_id and date and time:
            keyboard.button(
                text=f"ID: {appt_id} - {date} {time} - {status_display}", 
                callback_data=f"admin_view_appointment_{appt_id}"
            )
    
    keyboard.button(
        text="🔙 Вернуться в панель администратора", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointment_actions_keyboard(appointment_id, status):
    """Generate actions keyboard for a specific appointment"""
    keyboard = InlineKeyboardBuilder()
    
    # Show different action buttons based on status
    if status == "confirmed":
        keyboard.button(
            text="✓ Отметить как выполненное", 
            callback_data=f"admin_complete_appointment_{appointment_id}"
        )
        keyboard.button(
            text="❌ Отменить запись", 
            callback_data=f"admin_cancel_appointment_{appointment_id}"
        )
    elif status == "completed":
        keyboard.button(
            text="💰 Отметить как оплаченное", 
            callback_data=f"admin_paid_appointment_{appointment_id}"
        )
    
    # Payment method options if appointment is completed or confirmed
    if status in ["confirmed", "completed"]:
        keyboard.button(
            text="💳 Изменить способ оплаты", 
            callback_data=f"admin_change_payment_{appointment_id}"
        )
    
    keyboard.button(
        text="🔙 Вернуться к записям", 
        callback_data="admin_appointments"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_payment_method_keyboard(appointment_id):
    """Generate keyboard for selecting payment method"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="💵 Наличные", 
        callback_data=f"admin_set_payment_cash_{appointment_id}"
    )
    keyboard.button(
        text="💳 Карта/Терминал", 
        callback_data=f"admin_set_payment_card_{appointment_id}"
    )
    keyboard.button(
        text="📲 Перевод", 
        callback_data=f"admin_set_payment_transfer_{appointment_id}"
    )
    keyboard.button(
        text="🔙 Назад", 
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_cancel_confirmation_keyboard(appointment_id):
    """Generate confirmation keyboard for appointment cancellation"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, отменить запись", 
        callback_data=f"confirm_admin_cancel_{appointment_id}"
    )
    keyboard.button(
        text="❌ Нет, оставить запись", 
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_complete_confirmation_keyboard(appointment_id):
    """Generate confirmation keyboard for marking appointment as completed"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, отметить выполненной", 
        callback_data=f"confirm_admin_complete_{appointment_id}"
    )
    keyboard.button(
        text="❌ Нет, оставить как есть", 
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_paid_confirmation_keyboard(appointment_id):
    """Generate confirmation keyboard for marking appointment as paid"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Да, отметить оплаченной", 
        callback_data=f"confirm_admin_paid_{appointment_id}"
    )
    keyboard.button(
        text="❌ Нет, оставить как есть", 
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_masters_management_keyboard():
    """Generate a keyboard for masters management options"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Добавить мастера", 
        callback_data="add_master"
    )
    keyboard.button(
        text="📋 Просмотр всех мастеров", 
        callback_data="view_masters"
    )
    keyboard.button(
        text="🔙 Вернуться в панель администратора", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_masters_keyboard(masters):
    """Generate a keyboard listing all masters"""
    keyboard = InlineKeyboardBuilder()
    for master in masters:
        keyboard.button(
            text=f"{master['name']}", 
            callback_data=f"admin_view_master_{master['id']}"
        )
    
    keyboard.button(
        text="🔙 Вернуться к управлению мастерами", 
        callback_data="admin_masters"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_master_actions_keyboard(master_id):
    """Generate a keyboard for actions on a specific master"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Редактировать мастера", 
        callback_data=f"edit_master_{master_id}"
    )
    keyboard.button(
        text="📅 Настроить рабочее время", 
        callback_data=f"edit_master_schedule_{master_id}"
    )
    keyboard.button(
        text="🔔 Настроить уведомления", 
        callback_data=f"edit_master_notifications_{master_id}"
    )
    keyboard.button(
        text="📊 Статистика мастера", 
        callback_data=f"master_stats_{master_id}"
    )
    keyboard.button(
        text="🔙 Вернуться к мастерам", 
        callback_data="view_masters"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_master_keyboard(master_id):
    """Generate a keyboard for editing master fields"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Изменить имя", 
        callback_data=f"edit_master_name_{master_id}"
    )
    keyboard.button(
        text="✏️ Изменить Telegram", 
        callback_data=f"edit_master_telegram_{master_id}"
    )
    keyboard.button(
        text="✏️ Изменить адрес", 
        callback_data=f"edit_master_address_{master_id}"
    )
    keyboard.button(
        text="✏️ Изменить геопозицию", 
        callback_data=f"edit_master_location_{master_id}"
    )
    keyboard.button(
        text="🔙 Вернуться к мастеру", 
        callback_data=f"admin_view_master_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_schedule_days_keyboard(master_id):
    """Generate a keyboard for selecting days to edit in schedule"""
    keyboard = InlineKeyboardBuilder()
    days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    for day in days:
        keyboard.button(
            text=day, 
            callback_data=f"edit_day_{master_id}_{day}"
        )
    
    keyboard.button(
        text="🔙 Вернуться к мастеру", 
        callback_data=f"admin_view_master_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_day_schedule_keyboard(master_id, day, current_settings):
    """Generate a keyboard for editing schedule for a specific day"""
    keyboard = InlineKeyboardBuilder()
    
    # Enable/disable day
    is_enabled = current_settings.get('enabled', True)
    status_text = "✅ Рабочий день" if is_enabled else "❌ Выходной"
    toggle_text = "Отметить как выходной" if is_enabled else "Отметить как рабочий"
    
    keyboard.button(
        text=f"Статус: {status_text}", 
        callback_data=f"view_day_status_{master_id}_{day}"
    )
    keyboard.button(
        text=toggle_text, 
        callback_data=f"toggle_day_{master_id}_{day}"
    )
    
    # Only show time settings if day is enabled
    if is_enabled:
        start_time = current_settings.get('start', '09:00')
        end_time = current_settings.get('end', '18:00')
        
        keyboard.button(
            text=f"Начало работы: {start_time}", 
            callback_data=f"edit_start_time_{master_id}_{day}"
        )
        keyboard.button(
            text=f"Конец работы: {end_time}", 
            callback_data=f"edit_end_time_{master_id}_{day}"
        )
    
    keyboard.button(
        text="🔙 Вернуться к выбору дня", 
        callback_data=f"edit_master_schedule_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_notifications_keyboard(master_id, notifications_enabled):
    """Generate a keyboard for notification settings"""
    keyboard = InlineKeyboardBuilder()
    
    status_text = "✅ Включены" if notifications_enabled else "❌ Выключены"
    toggle_text = "Выключить уведомления" if notifications_enabled else "Включить уведомления"
    
    keyboard.button(
        text=f"Статус уведомлений: {status_text}", 
        callback_data=f"view_notifications_{master_id}"
    )
    keyboard.button(
        text=toggle_text, 
        callback_data=f"toggle_notifications_{master_id}"
    )
    
    keyboard.button(
        text="🔙 Вернуться к мастеру", 
        callback_data=f"admin_view_master_{master_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_stats_period_keyboard(date_filter=None, master_id=None):
    """Generate a keyboard for selecting statistics period"""
    keyboard = InlineKeyboardBuilder()
    
    # Determine the base callback data
    base_data = ""
    if master_id:
        base_data = f"_{master_id}"
    
    # Current filter indication
    if date_filter:
        keyboard.button(
            text=f"Текущий фильтр: {date_filter}", 
            callback_data=f"current_filter{base_data}"
        )
    
    # Period options
    keyboard.button(
        text="Сегодня", 
        callback_data=f"stats_today{base_data}"
    )
    keyboard.button(
        text="Вчера", 
        callback_data=f"stats_yesterday{base_data}"
    )
    keyboard.button(
        text="Неделя", 
        callback_data=f"stats_week{base_data}"
    )
    keyboard.button(
        text="Месяц", 
        callback_data=f"stats_month{base_data}"
    )
    keyboard.button(
        text="Все время", 
        callback_data=f"stats_all{base_data}"
    )
    
    # Back button - different based on context
    if master_id:
        keyboard.button(
            text="🔙 Вернуться к мастеру", 
            callback_data=f"admin_view_master_{master_id}"
        )
    else:
        keyboard.button(
            text="🔙 Вернуться в панель администратора", 
            callback_data="back_to_admin"
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
