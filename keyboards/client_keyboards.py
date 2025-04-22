
# This file contains keyboard layouts for client interactions in the Telegram bot

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

def get_services_by_category_keyboard(services_by_category):
    """Generate an inline keyboard for services grouped by category"""
    keyboard = InlineKeyboardBuilder()
    
    for category, services in services_by_category.items():
        # Add category button
        keyboard.button(
            text=f"📂 {category}",
            callback_data=f"category_{category}"
        )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_services_in_category_keyboard(services, category):
    """Generate an inline keyboard for services in a specific category"""
    keyboard = InlineKeyboardBuilder()
    
    for service in services:
        keyboard.button(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"service_{service['id']}"
        )
    
    # Add back button
    keyboard.button(
        text="🔙 Назад к категориям",
        callback_data="back_to_categories"
    )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_services_keyboard(services):
    """Generate an inline keyboard for available services"""
    keyboard = InlineKeyboardBuilder()
    for service in services:
        keyboard.button(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"service_{service['id']}"
        )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_masters_keyboard(masters):
    """Generate an inline keyboard for available masters"""
    keyboard = InlineKeyboardBuilder()
    for master in masters:
        keyboard.button(
            text=f"{master['name']}",
            callback_data=f"master_{master['id']}"
        )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_master_info_keyboard(master):
    """Generate a keyboard for master info with navigation options"""
    keyboard = InlineKeyboardBuilder()
    
    # Add location button if available
    if master.get('location') and master['location'].strip():
        keyboard.button(
            text="📍 Открыть в навигаторе",
            url=master['location']
        )
    
    # Add Telegram button if available
    if master.get('telegram') and master['telegram'].strip():
        telegram = master['telegram'].replace('@', '')
        keyboard.button(
            text="💬 Написать в Telegram",
            url=f"https://t.me/{telegram}"
        )
    
    # Add book service button
    keyboard.button(
        text="📅 Записаться на услугу",
        callback_data=f"book_with_master_{master['id']}"
    )
    
    # Add back button
    keyboard.button(
        text="🔙 Назад к списку мастеров",
        callback_data="view_masters"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_special_offers_keyboard(offers, master_id):
    """Generate an inline keyboard for special offers"""
    keyboard = InlineKeyboardBuilder()
    
    for offer in offers:
        keyboard.button(
            text=f"🎁 {offer['name']} - {offer['price']}",
            callback_data=f"offer_{offer['id']}_{master_id}"
        )
    
    # Add skip button
    keyboard.button(
        text="⏭️ Перейти к обычным услугам",
        callback_data=f"skip_offers_{master_id}"
    )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_date_keyboard():
    """Generate an inline keyboard with dates for the next 7 days"""
    keyboard = InlineKeyboardBuilder()
    today = datetime.now()
    
    # Add buttons for the next 7 days
    for i in range(7):
        date = today + timedelta(days=i)
        formatted_date = date.strftime("%Y-%m-%d")
        display_date = date.strftime("%d.%m (%a)")
        keyboard.button(
            text=display_date,
            callback_data=f"date_{formatted_date}"
        )
    
    # Add cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_time_keyboard(date, master_id=None, service_id=None, duration=60):
    """Generate an inline keyboard with available time slots"""
    keyboard = InlineKeyboardBuilder()
    
    # Default time slots from 10:00 to 19:00 with intervals based on service duration
    start_hour = 10
    end_hour = 19
    duration_mins = int(duration)
    intervals_per_hour = 60 // duration_mins
    
    for hour in range(start_hour, end_hour + 1):
        for minute_idx in range(intervals_per_hour):
            if hour == end_hour and minute_idx > 0:
                continue  # Skip times after end_hour
                
            minutes = minute_idx * duration_mins
            time_slot = f"{hour}:{minutes:02d}"
            
            # Create callback data with all necessary info
            callback_data = f"time_{date}_{time_slot}"
            if master_id:
                callback_data += f"_{master_id}"
            if service_id:
                callback_data += f"_{service_id}"
                
            keyboard.button(
                text=time_slot,
                callback_data=callback_data
            )
    
    # Add back and cancel buttons
    keyboard.button(
        text="⬅️ Назад к датам",
        callback_data="back_to_dates"
    )
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(2)  # Two buttons per row for time slots
    return keyboard.as_markup()

def get_confirmation_keyboard(service_id, date, time, master_id=None):
    """Generate a confirmation inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    # Create callback data with all necessary info
    confirm_data = f"confirm_{service_id}_{date}_{time}"
    if master_id:
        confirm_data += f"_{master_id}"
    
    # Confirm button
    keyboard.button(
        text="✅ Подтвердить",
        callback_data=confirm_data
    )
    
    # Back to time selection
    keyboard.button(
        text="⬅️ Назад ко времени",
        callback_data=f"back_to_time_{date}"
    )
    
    # Cancel button
    keyboard.button(
        text="❌ Отменить",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointments_keyboard(appointments):
    """Generate an inline keyboard for user's appointments, grouped by date"""
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
    
    # Today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Add appointments for today first if exists
    if today in appointments_by_date:
        keyboard.button(
            text=f"📅 Сегодня ({today})",
            callback_data=f"date_header_{today}"
        )
        
        for appointment in appointments_by_date[today]:
            service_name = appointment.get('service_name', 'Услуга')
            status_text = {
                'confirmed': '✅ Подтверждено',
                'canceled': '❌ Отменено',
                'completed': '✓ Выполнено',
                'paid': '💰 Оплачено',
                'pending': '⏳ Ожидает подтверждения'
            }.get(appointment.get('status'), appointment.get('status', 'Неизвестно'))
            
            keyboard.button(
                text=f"{appointment.get('time')} - {service_name} - {status_text}",
                callback_data=f"view_appointment_{appointment.get('id')}"
            )
    
    # Add other dates with collapsed appointments
    for date in sorted_dates:
        if date != today:
            count = len(appointments_by_date[date])
            keyboard.button(
                text=f"📅 {date} ({count} записей)",
                callback_data=f"expand_date_{date}"
            )
    
    # Add filter buttons
    keyboard.button(
        text="🔍 Активные записи",
        callback_data="filter_active"
    )
    
    keyboard.button(
        text="📜 Все записи",
        callback_data="filter_all"
    )
    
    keyboard.button(
        text="📊 Последние 3 записи",
        callback_data="filter_recent"
    )
    
    # Add back to menu button
    keyboard.button(
        text="🔙 Вернуться в меню",
        callback_data="back_to_menu"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_date_appointments_keyboard(appointments, date):
    """Generate keyboard for appointments on a specific date"""
    keyboard = InlineKeyboardBuilder()
    
    # Add header for date
    keyboard.button(
        text=f"📅 Записи на {date}:",
        callback_data=f"date_header_{date}"
    )
    
    # Add each appointment
    for appointment in appointments:
        service_name = appointment.get('service_name', 'Услуга')
        status_text = {
            'confirmed': '✅ Подтверждено',
            'canceled': '❌ Отменено',
            'completed': '✓ Выполнено',
            'paid': '💰 Оплачено',
            'pending': '⏳ Ожидает подтверждения'
        }.get(appointment.get('status'), appointment.get('status', 'Неизвестно'))
        
        keyboard.button(
            text=f"{appointment.get('time')} - {service_name} - {status_text}",
            callback_data=f"view_appointment_{appointment.get('id')}"
        )
    
    # Add back button
    keyboard.button(
        text="🔙 Назад к списку дат",
        callback_data="view_my_appointments"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointment_actions_keyboard(appointment):
    """Generate a keyboard for appointment actions"""
    keyboard = InlineKeyboardBuilder()
    
    # Add cancel button if appointment is not already canceled or completed
    if appointment.get('status') not in ['canceled', 'completed', 'paid']:
        keyboard.button(
            text=f"❌ Отменить запись",
            callback_data=f"cancel_appointment_{appointment.get('id')}"
        )
    
    # Add "book again" button
    keyboard.button(
        text=f"🔄 Записаться снова",
        callback_data=f"book_again_{appointment.get('id')}"
    )
    
    # Add back button
    keyboard.button(
        text="🔙 Назад к списку записей",
        callback_data="view_my_appointments"
    )
    
    # Add main menu button
    keyboard.button(
        text="🏠 Главное меню",
        callback_data="back_to_menu"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_main_menu_keyboard():
    """Generate the main menu keyboard for clients"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="📅 Записаться на услугу",
        callback_data="start_booking"
    )
    keyboard.button(
        text="🗓️ Мои записи",
        callback_data="view_my_appointments"
    )
    keyboard.button(
        text="👨‍💼 Список мастеров",
        callback_data="view_masters"
    )
    keyboard.button(
        text="ℹ️ Помощь",
        callback_data="help"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_back_to_menu_keyboard():
    """Generate a keyboard to go back to main menu"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔙 Вернуться в меню",
        callback_data="back_to_menu"
    )
    return keyboard.as_markup()
