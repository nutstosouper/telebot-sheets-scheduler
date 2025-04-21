
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
        text="❌ Cancel",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_time_keyboard(date):
    """Generate an inline keyboard with available time slots"""
    keyboard = InlineKeyboardBuilder()
    
    # Add time slots from 10:00 to 19:00 with 1-hour intervals
    for hour in range(10, 20):
        time_slot = f"{hour}:00"
        keyboard.button(
            text=time_slot,
            callback_data=f"time_{date}_{time_slot}"
        )
    
    # Add back and cancel buttons
    keyboard.button(
        text="⬅️ Back to dates",
        callback_data="back_to_dates"
    )
    keyboard.button(
        text="❌ Cancel",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(2)  # Two buttons per row for time slots
    return keyboard.as_markup()

def get_confirmation_keyboard(service_id, date, time):
    """Generate a confirmation inline keyboard"""
    keyboard = InlineKeyboardBuilder()
    
    # Confirm button
    keyboard.button(
        text="✅ Confirm",
        callback_data=f"confirm_{service_id}_{date}_{time}"
    )
    
    # Back to time selection
    keyboard.button(
        text="⬅️ Back to time",
        callback_data=f"back_to_time_{date}"
    )
    
    # Cancel button
    keyboard.button(
        text="❌ Cancel",
        callback_data="cancel_booking"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointments_keyboard(appointments):
    """Generate an inline keyboard for user's appointments"""
    keyboard = InlineKeyboardBuilder()
    for appointment in appointments:
        keyboard.button(
            text=f"ID: {appointment['id']} - {appointment['date']} {appointment['time']} - {appointment['status']}",
            callback_data=f"view_appointment_{appointment['id']}"
        )
        
        # Add cancel button if appointment is not already canceled
        if appointment['status'] != 'canceled':
            keyboard.button(
                text=f"❌ Cancel appointment {appointment['id']}",
                callback_data=f"cancel_appointment_{appointment['id']}"
            )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_back_to_menu_keyboard():
    """Generate a keyboard to go back to main menu"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔙 Back to Menu",
        callback_data="back_to_menu"
    )
    return keyboard.as_markup()
