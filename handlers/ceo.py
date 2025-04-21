
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.db_api import user_commands, service_commands, appointment_commands
from keyboards.admin_keyboards import get_back_to_admin_keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Define states for CEO operations
class CEOStates(StatesGroup):
    adding_admin = State()
    removing_admin = State()

def get_ceo_keyboard():
    """Generate the CEO panel keyboard"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="👥 Manage Admins", 
        callback_data="ceo_manage_admins"
    )
    keyboard.button(
        text="📊 Global Statistics", 
        callback_data="ceo_global_stats"
    )
    keyboard.button(
        text="🔙 Back to Admin Panel", 
        callback_data="back_to_admin"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

def get_manage_admins_keyboard():
    """Generate keyboard for admin management"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="➕ Add Admin", 
        callback_data="ceo_add_admin"
    )
    keyboard.button(
        text="❌ Remove Admin", 
        callback_data="ceo_remove_admin"
    )
    keyboard.button(
        text="👥 View Admins", 
        callback_data="ceo_view_admins"
    )
    keyboard.button(
        text="🔙 Back to CEO Panel", 
        callback_data="cmd_ceo"
    )
    
    keyboard.adjust(1)  # One button per row
    return keyboard.as_markup()

async def get_admins():
    """Get all users with admin role"""
    # This function would need to be implemented in user_commands
    # For now, we'll use a simplified approach
    all_users = [] # We would need to implement get_all_users in user_commands
    return [user for user in all_users if user.get('role') == 'admin']

async def cmd_ceo(message: Message = None, callback: CallbackQuery = None, role: str = None):
    """Handle the /ceo command - show CEO panel"""
    # Check if initiated from message or callback
    is_callback = callback is not None
    
    # Determine user role and check if CEO
    if role != "ceo":
        if is_callback:
            await callback.answer("Access denied. This command is only available to CEO.")
            return
        else:
            await message.answer("Access denied. This command is only available to CEO.")
            return
    
    text = "CEO Panel - Advanced Management"
    
    if is_callback:
        await callback.message.edit_text(text, reply_markup=get_ceo_keyboard())
        await callback.answer()
    else:
        await message.answer(text, reply_markup=get_ceo_keyboard())

async def ceo_manage_admins(callback: CallbackQuery, role: str):
    """Handle admin management section"""
    if role != "ceo":
        await callback.answer("Access denied. This command is only available to CEO.")
        return
    
    await callback.message.edit_text(
        "Admin Management",
        reply_markup=get_manage_admins_keyboard()
    )
    
    await callback.answer()

async def ceo_add_admin_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the process of adding a new admin"""
    if role != "ceo":
        await callback.answer("Access denied. This command is only available to CEO.")
        return
    
    await state.set_state(CEOStates.adding_admin)
    
    await callback.message.edit_text(
        "Please enter the Telegram User ID of the user you want to promote to admin:"
    )
    
    await callback.answer()

async def ceo_add_admin(message: Message, state: FSMContext):
    """Handle adding a new admin"""
    # Try to convert input to integer user ID
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Invalid user ID. Please enter a numeric ID.")
        return
    
    # Check if user exists
    user = await user_commands.get_user(user_id)
    
    if not user:
        await message.answer(
            f"User with ID {user_id} not found in the system.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    # Update user role to admin
    success = await user_commands.update_user_role(user_id, "admin")
    
    if success:
        await message.answer(
            f"✅ User {user['full_name']} (ID: {user_id}) has been promoted to admin.",
            reply_markup=get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to update user role. Please try again later.",
            reply_markup=get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def ceo_remove_admin_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the process of removing an admin"""
    if role != "ceo":
        await callback.answer("Access denied. This command is only available to CEO.")
        return
    
    await state.set_state(CEOStates.removing_admin)
    
    await callback.message.edit_text(
        "Please enter the Telegram User ID of the admin you want to demote to client:"
    )
    
    await callback.answer()

async def ceo_remove_admin(message: Message, state: FSMContext):
    """Handle removing an admin"""
    # Try to convert input to integer user ID
    try:
        user_id = int(message.text.strip())
    except ValueError:
        await message.answer("Invalid user ID. Please enter a numeric ID.")
        return
    
    # Check if user exists and is an admin
    user = await user_commands.get_user(user_id)
    
    if not user:
        await message.answer(
            f"User with ID {user_id} not found in the system.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    if user['role'] != 'admin':
        await message.answer(
            f"User {user['full_name']} (ID: {user_id}) is not an admin.",
            reply_markup=get_back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    # Update user role to client
    success = await user_commands.update_user_role(user_id, "client")
    
    if success:
        await message.answer(
            f"✅ Admin {user['full_name']} (ID: {user_id}) has been demoted to client.",
            reply_markup=get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Failed to update user role. Please try again later.",
            reply_markup=get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def ceo_global_stats(callback: CallbackQuery, role: str):
    """Handle viewing global statistics"""
    if role != "ceo":
        await callback.answer("Access denied. This command is only available to CEO.")
        return
    
    # Get all appointments for statistics
    appointments = await appointment_commands.get_all_appointments()
    
    # Get all services for statistics
    services = await service_commands.get_all_services()
    
    # Basic statistics
    total_appointments = len(appointments)
    confirmed_appointments = len([a for a in appointments if a['status'] == 'confirmed'])
    canceled_appointments = len([a for a in appointments if a['status'] == 'canceled'])
    
    # Calculate revenue (would need price data from history)
    total_revenue = 0
    
    # Service popularity
    service_counts = {}
    for appointment in appointments:
        service_id = appointment['service_id']
        if service_id in service_counts:
            service_counts[service_id] += 1
        else:
            service_counts[service_id] = 1
    
    # Get top services
    top_services = []
    for service_id, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
        service = next((s for s in services if str(s["id"]) == str(service_id)), None)
        if service:
            top_services.append(f"{service['name']}: {count} bookings")
    
    # Format stats message
    stats_text = f"""
📊 Global Statistics:

📋 Appointments:
- Total: {total_appointments}
- Confirmed: {confirmed_appointments}
- Canceled: {canceled_appointments}

💰 Estimated Revenue: {total_revenue}

🔝 Top Services:
"""
    
    if top_services:
        for i, service in enumerate(top_services, 1):
            stats_text += f"{i}. {service}\n"
    else:
        stats_text += "No services booked yet\n"
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_back_to_admin_keyboard()
    )
    
    await callback.answer()

def register_handlers(dp: Dispatcher):
    """Register CEO handlers"""
    # CEO command
    dp.message.register(cmd_ceo, Command("ceo"))
    dp.callback_query.register(cmd_ceo, F.data == "cmd_ceo")
    
    # CEO panel sections
    dp.callback_query.register(ceo_manage_admins, F.data == "ceo_manage_admins")
    dp.callback_query.register(ceo_global_stats, F.data == "ceo_global_stats")
    
    # Admin management
    dp.callback_query.register(ceo_add_admin_start, F.data == "ceo_add_admin")
    dp.callback_query.register(ceo_remove_admin_start, F.data == "ceo_remove_admin")
    dp.message.register(ceo_add_admin, CEOStates.adding_admin)
    dp.message.register(ceo_remove_admin, CEOStates.removing_admin)
