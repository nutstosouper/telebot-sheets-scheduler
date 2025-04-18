
# This file contains keyboard layouts for administrator interactions in the Telegram bot

from aiogram import types

def get_admin_keyboard():
    """Generate the main admin panel keyboard"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Manage Services", callback_data="admin_services"),
        types.InlineKeyboardButton(text="Manage Appointments", callback_data="admin_appointments"),
        types.InlineKeyboardButton(text="View Statistics", callback_data="admin_stats")
    )
    return keyboard

def get_services_management_keyboard():
    """Generate a keyboard for service management options"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Add Service", callback_data="add_service"),
        types.InlineKeyboardButton(text="Delete Service", callback_data="delete_service")
    )
    return keyboard

def get_all_appointments_keyboard(appointments):
    """Generate a keyboard displaying all appointments"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for appointment in appointments:
        keyboard.add(types.InlineKeyboardButton(
            text=f"ID: {appointment['id']} - User: {appointment['user_id']} - {appointment['date']} {appointment['time']} - {appointment['status']}",
            callback_data=f"view_appointment_{appointment['id']}"
        ))
        
        # Add cancel button if appointment is not already canceled
        if appointment['status'] != 'canceled':
            keyboard.add(types.InlineKeyboardButton(
                text=f"❌ Cancel appointment {appointment['id']}",
                callback_data=f"admin_cancel_{appointment['id']}"
            ))
    
    return keyboard
