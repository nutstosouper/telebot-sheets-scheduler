
# This file contains keyboard layouts for administrator interactions in the Telegram bot

from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    """Generate the main admin panel keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Manage Services", 
        callback_data="admin_services"
    )
    keyboard.button(
        text="Manage Appointments", 
        callback_data="admin_appointments"
    )
    keyboard.button(
        text="View Statistics", 
        callback_data="admin_stats"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_services_management_keyboard():
    """Generate a keyboard for service management options"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Add Service", 
        callback_data="add_service"
    )
    keyboard.button(
        text="📋 View All Services", 
        callback_data="view_services"
    )
    keyboard.button(
        text="🔙 Back to Admin Panel", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_service_actions_keyboard(service_id):
    """Generate a keyboard for actions on a specific service"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Edit Service", 
        callback_data=f"edit_service_{service_id}"
    )
    keyboard.button(
        text="❌ Delete Service", 
        callback_data=f"delete_service_{service_id}"
    )
    keyboard.button(
        text="🔙 Back to Services", 
        callback_data="view_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_edit_service_keyboard(service_id):
    """Generate a keyboard for editing service fields"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✏️ Edit Name", 
        callback_data=f"edit_service_name_{service_id}"
    )
    keyboard.button(
        text="✏️ Edit Description", 
        callback_data=f"edit_service_description_{service_id}"
    )
    keyboard.button(
        text="✏️ Edit Price", 
        callback_data=f"edit_service_price_{service_id}"
    )
    keyboard.button(
        text="🔙 Back to Service", 
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_services_keyboard(services):
    """Generate a keyboard listing all services"""
    keyboard = InlineKeyboardBuilder()
    for service in services:
        # Handle both naming conventions for service fields
        service_id = service.get('id', service.get('Service ID', ''))
        service_name = service.get('name', service.get('Name', 'Unknown'))
        service_price = service.get('price', service.get('Price', ''))
        
        keyboard.button(
            text=f"{service_name} - {service_price}", 
            callback_data=f"admin_view_service_{service_id}"
        )
    
    keyboard.button(
        text="🔙 Back to Services Management", 
        callback_data="admin_services"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_confirm_delete_keyboard(service_id):
    """Generate confirmation keyboard for service deletion"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Yes, Delete", 
        callback_data=f"confirm_delete_service_{service_id}"
    )
    keyboard.button(
        text="❌ No, Cancel", 
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_all_appointments_keyboard(appointments):
    """Generate a keyboard displaying all appointments"""
    keyboard = InlineKeyboardBuilder()
    for appointment in appointments:
        # Get values with fallbacks for different column naming conventions
        app_id = appointment.get('id', appointment.get('Appointment ID', 'unknown'))
        app_date = appointment.get('date', appointment.get('Date', 'unknown'))
        app_time = appointment.get('time', appointment.get('Time', 'unknown'))
        app_status = appointment.get('status', appointment.get('Status', 'unknown'))
        
        keyboard.button(
            text=f"ID: {app_id} - {app_date} {app_time} - {app_status}", 
            callback_data=f"admin_view_appointment_{app_id}"
        )
    
    keyboard.button(
        text="🔙 Back to Admin Panel", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_appointment_actions_keyboard(appointment_id, status):
    """Generate actions keyboard for a specific appointment"""
    keyboard = InlineKeyboardBuilder()
    
    # Show cancel button only if not already canceled
    if status != "canceled":
        keyboard.button(
            text="❌ Cancel Appointment", 
            callback_data=f"admin_cancel_appointment_{appointment_id}"
        )
    
    keyboard.button(
        text="🔙 Back to Appointments", 
        callback_data="admin_appointments"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_cancel_confirmation_keyboard(appointment_id):
    """Generate confirmation keyboard for appointment cancellation"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="✅ Yes, Cancel Appointment", 
        callback_data=f"confirm_admin_cancel_{appointment_id}"
    )
    keyboard.button(
        text="❌ No, Keep Appointment", 
        callback_data=f"admin_view_appointment_{appointment_id}"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_back_to_admin_keyboard():
    """Generate a keyboard to go back to admin panel"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🔙 Back to Admin Panel", 
        callback_data="back_to_admin"
    )
    
    return keyboard.as_markup()
