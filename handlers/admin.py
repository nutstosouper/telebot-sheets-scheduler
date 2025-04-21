
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.db_api import service_commands, appointment_commands
from keyboards import admin_keyboards

# Define states for admin operations
class AdminServiceStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()

async def cmd_admin(message: Message, role: str):
    """Handle the /admin command - show admin panel"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await message.answer("Access denied. This command is only available to administrators.")
        return
    
    await message.answer(
        "Admin Panel",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )

async def admin_services(callback: CallbackQuery, role: str):
    """Handle admin services menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    await callback.message.edit_text(
        "Service Management",
        reply_markup=admin_keyboards.get_services_management_keyboard()
    )
    
    await callback.answer()

async def add_service_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the add service flow"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Set state to adding name
    await state.set_state(AdminServiceStates.adding_name)
    
    await callback.message.edit_text(
        "Please enter the name of the new service:"
    )
    
    await callback.answer()

async def add_service_name(message: Message, state: FSMContext):
    """Handle adding service name"""
    # Save the name
    await state.update_data(name=message.text)
    
    # Move to description state
    await state.set_state(AdminServiceStates.adding_description)
    
    await message.answer("Please enter the description of the service:")

async def add_service_description(message: Message, state: FSMContext):
    """Handle adding service description"""
    # Save the description
    await state.update_data(description=message.text)
    
    # Move to price state
    await state.set_state(AdminServiceStates.adding_price)
    
    await message.answer("Please enter the price of the service (numbers only):")

async def add_service_price(message: Message, state: FSMContext):
    """Handle adding service price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Invalid price. Please enter a number only:")
        return
    
    # Get all data
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    
    # Add the service
    service = await service_commands.add_service(name, description, price)
    
    if service:
        await message.answer(
            f"✅ Service added successfully!\n\nName: {name}\nDescription: {description}\nPrice: {price}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to add service. Please try again later.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_services(callback: CallbackQuery, role: str):
    """Handle viewing all services"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Get all services
    services = await service_commands.get_all_services()
    
    if not services:
        await callback.message.edit_text(
            "No services found. You can add services using the Add Service button.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "All Services:",
            reply_markup=admin_keyboards.get_all_services_keyboard(services)
        )
    
    await callback.answer()

async def admin_view_service(callback: CallbackQuery, role: str):
    """Handle viewing a specific service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Get all services and find the one with matching ID
    services = await service_commands.get_all_services()
    service = next((s for s in services if str(s["id"]) == str(service_id)), None)
    
    if not service:
        await callback.message.edit_text(
            "Service not found.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Service Details:\n\nID: {service['id']}\nName: {service['name']}\nDescription: {service['description']}\nPrice: {service['price']}",
            reply_markup=admin_keyboards.get_service_actions_keyboard(service_id)
        )
    
    await callback.answer()

async def edit_service(callback: CallbackQuery, role: str):
    """Handle editing a service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "What would you like to edit?",
        reply_markup=admin_keyboards.get_edit_service_keyboard(service_id)
    )
    
    await callback.answer()

async def edit_service_name_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service name"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing name
    await state.set_state(AdminServiceStates.editing_name)
    
    await callback.message.edit_text(
        "Please enter the new name for the service:"
    )
    
    await callback.answer()

async def edit_service_name(message: Message, state: FSMContext):
    """Handle updating service name"""
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update the service name
    success = await service_commands.update_service(service_id, name=message.text)
    
    if success:
        await message.answer(
            f"✅ Service name updated to: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to update service name. Please try again later.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_description_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service description"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing description
    await state.set_state(AdminServiceStates.editing_description)
    
    await callback.message.edit_text(
        "Please enter the new description for the service:"
    )
    
    await callback.answer()

async def edit_service_description(message: Message, state: FSMContext):
    """Handle updating service description"""
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update the service description
    success = await service_commands.update_service(service_id, description=message.text)
    
    if success:
        await message.answer(
            f"✅ Service description updated to: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to update service description. Please try again later.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_price_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service price"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing price
    await state.set_state(AdminServiceStates.editing_price)
    
    await callback.message.edit_text(
        "Please enter the new price for the service (numbers only):"
    )
    
    await callback.answer()

async def edit_service_price(message: Message, state: FSMContext):
    """Handle updating service price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Invalid price. Please enter a number only:")
        return
    
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update the service price
    success = await service_commands.update_service(service_id, price=price)
    
    if success:
        await message.answer(
            f"✅ Service price updated to: {price}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to update service price. Please try again later.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_service_confirm(callback: CallbackQuery, role: str):
    """Ask for confirmation before deleting a service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[2]
    
    # Get service details
    services = await service_commands.get_all_services()
    service = next((s for s in services if str(s["id"]) == str(service_id)), None)
    
    if not service:
        await callback.message.edit_text(
            "Service not found.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Are you sure you want to delete this service?\n\nID: {service['id']}\nName: {service['name']}\nDescription: {service['description']}\nPrice: {service['price']}",
            reply_markup=admin_keyboards.get_confirm_delete_keyboard(service_id)
        )
    
    await callback.answer()

async def delete_service(callback: CallbackQuery, role: str):
    """Handle deleting a service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Delete the service
    success = await service_commands.delete_service(service_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Service deleted successfully.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Failed to delete service. Please try again later.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    
    await callback.answer()

async def admin_appointments(callback: CallbackQuery, role: str):
    """Handle admin appointments menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Get all appointments
    appointments = await appointment_commands.get_all_appointments()
    
    if not appointments:
        await callback.message.edit_text(
            "No appointments found.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "All Appointments:",
            reply_markup=admin_keyboards.get_all_appointments_keyboard(appointments)
        )
    
    await callback.answer()

async def admin_view_appointment(callback: CallbackQuery, role: str):
    """Handle viewing a specific appointment as admin"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Appointment not found.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        # Get service details
        services = await service_commands.get_all_services()
        service = next((s for s in services if str(s["id"]) == str(appointment["service_id"])), None)
        
        service_name = "Unknown Service"
        if service:
            service_name = service["name"]
        
        await callback.message.edit_text(
            f"Appointment Details:\n\nID: {appointment['id']}\nUser ID: {appointment['user_id']}\nService: {service_name}\nDate: {appointment['date']}\nTime: {appointment['time']}\nStatus: {appointment['status']}",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, appointment['status'])
        )
    
    await callback.answer()

async def admin_cancel_appointment_confirm(callback: CallbackQuery, role: str):
    """Ask for confirmation before canceling an appointment"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Appointment not found.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Are you sure you want to cancel this appointment?\n\nID: {appointment['id']}\nDate: {appointment['date']}\nTime: {appointment['time']}",
            reply_markup=admin_keyboards.get_cancel_confirmation_keyboard(appointment_id)
        )
    
    await callback.answer()

async def admin_cancel_appointment(callback: CallbackQuery, role: str):
    """Handle canceling an appointment as admin"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    # Update appointment status
    success = await appointment_commands.update_appointment_status(appointment_id, "canceled")
    
    if success:
        await callback.message.edit_text(
            f"✅ Appointment {appointment_id} has been canceled.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Failed to cancel appointment. Please try again later.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def back_to_admin(callback: CallbackQuery, role: str):
    """Handle returning to admin panel"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    await callback.message.edit_text(
        "Admin Panel",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )
    
    await callback.answer()

async def admin_stats(callback: CallbackQuery, role: str):
    """Handle viewing admin statistics"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Access denied. This action is only available to administrators.")
        return
    
    # Get all appointments
    appointments = await appointment_commands.get_all_appointments()
    
    # Count by status
    total = len(appointments)
    confirmed = len([a for a in appointments if a['status'] == 'confirmed'])
    canceled = len([a for a in appointments if a['status'] == 'canceled'])
    
    # Format stats message
    stats_text = f"""
Admin Statistics:

Total Appointments: {total}
Confirmed: {confirmed}
Canceled: {canceled}

Feature will be enhanced in future updates.
"""
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=admin_keyboards.get_back_to_admin_keyboard()
    )
    
    await callback.answer()

def register_handlers(dp: Dispatcher):
    """Register admin handlers"""
    # Admin command
    dp.message.register(cmd_admin, Command("admin"))
    
    # Admin panel navigation
    dp.callback_query.register(admin_services, F.data == "admin_services")
    dp.callback_query.register(admin_appointments, F.data == "admin_appointments")
    dp.callback_query.register(back_to_admin, F.data == "back_to_admin")
    dp.callback_query.register(admin_stats, F.data == "admin_stats")
    
    # Service management
    dp.callback_query.register(add_service_start, F.data == "add_service")
    dp.callback_query.register(view_services, F.data == "view_services")
    dp.message.register(add_service_name, AdminServiceStates.adding_name)
    dp.message.register(add_service_description, AdminServiceStates.adding_description)
    dp.message.register(add_service_price, AdminServiceStates.adding_price)
    dp.callback_query.register(admin_view_service, F.data.startswith("admin_view_service_"))
    
    # Service editing
    dp.callback_query.register(edit_service, F.data.startswith("edit_service_") & ~F.data.startswith("edit_service_name_") & ~F.data.startswith("edit_service_description_") & ~F.data.startswith("edit_service_price_"))
    dp.callback_query.register(edit_service_name_start, F.data.startswith("edit_service_name_"))
    dp.callback_query.register(edit_service_description_start, F.data.startswith("edit_service_description_"))
    dp.callback_query.register(edit_service_price_start, F.data.startswith("edit_service_price_"))
    dp.message.register(edit_service_name, AdminServiceStates.editing_name)
    dp.message.register(edit_service_description, AdminServiceStates.editing_description)
    dp.message.register(edit_service_price, AdminServiceStates.editing_price)
    
    # Service deletion
    dp.callback_query.register(delete_service_confirm, F.data.startswith("delete_service_"))
    dp.callback_query.register(delete_service, F.data.startswith("confirm_delete_service_"))
    
    # Appointment management
    dp.callback_query.register(admin_view_appointment, F.data.startswith("admin_view_appointment_"))
    dp.callback_query.register(admin_cancel_appointment_confirm, F.data.startswith("admin_cancel_appointment_"))
    dp.callback_query.register(admin_cancel_appointment, F.data.startswith("confirm_admin_cancel_"))
