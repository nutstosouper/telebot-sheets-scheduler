
# This file contains keyboard layouts for client interactions in the Telegram bot

from aiogram import types

def get_services_keyboard(services):
    """Generate an inline keyboard for available services"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for service in services:
        keyboard.add(types.InlineKeyboardButton(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"service_{service['id']}"
        ))
    return keyboard

def get_appointments_keyboard(appointments):
    """Generate an inline keyboard for user's appointments"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for appointment in appointments:
        keyboard.add(types.InlineKeyboardButton(
            text=f"ID: {appointment['id']} - {appointment['date']} {appointment['time']} - {appointment['status']}",
            callback_data=f"view_appointment_{appointment['id']}"
        ))
        
        # Add cancel button if appointment is not already canceled
        if appointment['status'] != 'canceled':
            keyboard.add(types.InlineKeyboardButton(
                text=f"❌ Cancel appointment {appointment['id']}",
                callback_data=f"cancel_appointment_{appointment['id']}"
            ))
    
    return keyboard

def get_confirmation_keyboard():
    """Generate a confirmation inline keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="✅ Confirm", callback_data="confirm"),
        types.InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
    )
    return keyboard
