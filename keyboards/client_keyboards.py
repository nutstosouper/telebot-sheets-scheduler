
# This file contains keyboard layouts for client interactions in the Telegram bot

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta

def get_services_keyboard(services):
    """Generate an inline keyboard for available services"""
    keyboard = InlineKeyboardBuilder()
    for service in services:
        keyboard.button(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"service_{service['id']}"
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

def get_payment_method_keyboard(service_id, date, time, master_id=None):
    """Generate a keyboard for selecting payment method"""
    keyboard = InlineKeyboardBuilder()
    
    # Create base callback data
    base_data = f"{service_id}_{date}_{time}"
    if master_id:
        base_data += f"_{master_id}"
    
    # Payment method buttons
    keyboard.button(
        text="💵 Наличные",
        callback_data=f"payment_cash_{base_data}"
    )
    keyboard.button(
        text="💳 Карта/Терминал",
        callback_data=f"payment_card_{base_data}"
    )
    keyboard.button(
        text="📲 Перевод",
        callback_data=f"payment_transfer_{base_data}"
    )
    
    # Back button
    keyboard.button(
        text="⬅️ Назад",
        callback_data=f"back_to_confirmation_{base_data}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointments_keyboard(appointments):
    """Generate an inline keyboard for user's appointments"""
    keyboard = InlineKeyboardBuilder()
    for appointment in appointments:
        status_text = {
            'confirmed': '✅ Подтверждено',
            'canceled': '❌ Отменено',
            'completed': '✓ Выполнено',
            'paid': '💰 Оплачено'
        }.get(appointment.get('status'), appointment.get('status', 'Неизвестно'))
        
        keyboard.button(
            text=f"#{appointment.get('id')} - {appointment.get('date')} {appointment.get('time')} - {status_text}",
            callback_data=f"view_appointment_{appointment.get('id')}"
        )
        
        # Add cancel button if appointment is not already canceled or completed
        if appointment.get('status') not in ['canceled', 'completed', 'paid']:
            keyboard.button(
                text=f"❌ Отменить запись #{appointment.get('id')}",
                callback_data=f"cancel_appointment_{appointment.get('id')}"
            )
            
            # Add "book again" button
            keyboard.button(
                text=f"🔄 Записаться снова",
                callback_data=f"book_again_{appointment.get('id')}"
            )
    
    # Add back to menu button
    keyboard.button(
        text="🔙 Вернуться в меню",
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
