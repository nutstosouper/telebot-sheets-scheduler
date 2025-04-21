
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.db_api import service_commands, appointment_commands
from keyboards import client_keyboards

# Define states for booking flow
class BookingStates(StatesGroup):
    selecting_service = State()
    selecting_date = State()
    selecting_time = State()
    confirming = State()

async def cmd_start(message: Message):
    """Handle the /start command"""
    await message.answer(f"Hello, {message.from_user.first_name}! Welcome to our service booking bot.\n\nUse /help to see available commands.")

async def cmd_help(message: Message):
    """Handle the /help command"""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/book - Book a service
/appointments - View your appointments
"""
    await message.answer(help_text)

async def cmd_book(message: Message, state: FSMContext):
    """Handle the /book command - start booking flow"""
    # Reset state
    await state.clear()
    
    # Get available services
    services = await service_commands.get_all_services()
    
    if not services:
        await message.answer("Sorry, there are no services available at the moment. Please try again later.")
        return
    
    # Set state to selecting service
    await state.set_state(BookingStates.selecting_service)
    
    # Show services keyboard
    await message.answer(
        "Please select a service:",
        reply_markup=client_keyboards.get_services_keyboard(services)
    )

async def service_selected(callback: CallbackQuery, state: FSMContext):
    """Handle service selection"""
    # Extract service ID from callback data
    service_id = callback.data.split('_')[1]
    
    # Store selected service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to selecting date
    await state.set_state(BookingStates.selecting_date)
    
    # Show date selection keyboard
    await callback.message.edit_text(
        "Please select a date for your appointment:",
        reply_markup=client_keyboards.get_date_keyboard()
    )
    
    # Answer callback query
    await callback.answer()

async def date_selected(callback: CallbackQuery, state: FSMContext):
    """Handle date selection"""
    # Extract date from callback data
    date = callback.data.split('_')[1]
    
    # Store selected date in state
    await state.update_data(date=date)
    
    # Set state to selecting time
    await state.set_state(BookingStates.selecting_time)
    
    # Show time selection keyboard
    await callback.message.edit_text(
        f"Selected date: {date}\nPlease select a time:",
        reply_markup=client_keyboards.get_time_keyboard(date)
    )
    
    # Answer callback query
    await callback.answer()

async def time_selected(callback: CallbackQuery, state: FSMContext):
    """Handle time selection"""
    # Extract date and time from callback data
    parts = callback.data.split('_')
    date = parts[1]
    time = parts[2]
    
    # Store selected time in state
    await state.update_data(time=time)
    
    # Get all stored data
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Get service details
    services = await service_commands.get_all_services()
    service = next((s for s in services if str(s["id"]) == str(service_id)), None)
    
    if not service:
        await callback.message.edit_text("Sorry, the selected service is no longer available.")
        await state.clear()
        await callback.answer()
        return
    
    # Set state to confirming
    await state.set_state(BookingStates.confirming)
    
    # Show confirmation message and keyboard
    confirmation_text = f"""
Please confirm your booking:

Service: {service['name']}
Price: {service['price']}
Date: {date}
Time: {time}
"""
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=client_keyboards.get_confirmation_keyboard(service_id, date, time)
    )
    
    # Answer callback query
    await callback.answer()

async def booking_confirmed(callback: CallbackQuery, state: FSMContext):
    """Handle booking confirmation"""
    # Extract data from callback
    parts = callback.data.split('_')
    service_id = parts[1]
    date = parts[2]
    time = parts[3]
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Create appointment
    appointment = await appointment_commands.add_appointment(
        user_id=user_id,
        service_id=service_id,
        date=date,
        time=time
    )
    
    if appointment:
        await callback.message.edit_text(
            f"✅ Your appointment has been confirmed!\n\nID: {appointment['id']}\nDate: {date}\nTime: {time}\n\nYou can view or cancel your appointments using /appointments",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Sorry, there was an error booking your appointment. Please try again later.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    
    # Clear state
    await state.clear()
    
    # Answer callback query
    await callback.answer()

async def booking_canceled(callback: CallbackQuery, state: FSMContext):
    """Handle booking cancellation"""
    await callback.message.edit_text(
        "Booking canceled. You can start a new booking with /book",
        reply_markup=client_keyboards.get_back_to_menu_keyboard()
    )
    
    # Clear state
    await state.clear()
    
    # Answer callback query
    await callback.answer()

async def back_to_dates(callback: CallbackQuery, state: FSMContext):
    """Handle going back to date selection"""
    # Set state to selecting date
    await state.set_state(BookingStates.selecting_date)
    
    # Show date selection keyboard
    await callback.message.edit_text(
        "Please select a date for your appointment:",
        reply_markup=client_keyboards.get_date_keyboard()
    )
    
    # Answer callback query
    await callback.answer()

async def back_to_time(callback: CallbackQuery, state: FSMContext):
    """Handle going back to time selection"""
    # Extract date from callback data
    date = callback.data.split('_')[3]
    
    # Update state data
    await state.update_data(date=date)
    
    # Set state to selecting time
    await state.set_state(BookingStates.selecting_time)
    
    # Show time selection keyboard
    await callback.message.edit_text(
        f"Selected date: {date}\nPlease select a time:",
        reply_markup=client_keyboards.get_time_keyboard(date)
    )
    
    # Answer callback query
    await callback.answer()

async def cmd_appointments(message: Message):
    """Handle the /appointments command"""
    user_id = message.from_user.id
    
    # Get user appointments
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    if not appointments:
        await message.answer("You don't have any appointments.")
        return
    
    # Show appointments
    await message.answer(
        "Your appointments:",
        reply_markup=client_keyboards.get_appointments_keyboard(appointments)
    )

async def view_appointment(callback: CallbackQuery):
    """Handle viewing appointment details"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[2]
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Sorry, this appointment is no longer available.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Get service details
    services = await service_commands.get_all_services()
    service = next((s for s in services if str(s["id"]) == str(appointment["service_id"])), None)
    
    service_name = "Unknown Service"
    if service:
        service_name = service["name"]
    
    # Show appointment details
    details_text = f"""
Appointment Details:

ID: {appointment['id']}
Service: {service_name}
Date: {appointment['date']}
Time: {appointment['time']}
Status: {appointment['status']}
"""
    await callback.message.edit_text(
        details_text,
        reply_markup=client_keyboards.get_appointments_keyboard([appointment])
    )
    
    # Answer callback query
    await callback.answer()

async def cancel_appointment(callback: CallbackQuery):
    """Handle canceling an appointment"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[2]
    
    # Update appointment status
    success = await appointment_commands.update_appointment_status(appointment_id, "canceled")
    
    if success:
        await callback.message.edit_text(
            f"✅ Appointment {appointment_id} has been canceled.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Failed to cancel appointment. Please try again later.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    
    # Answer callback query
    await callback.answer()

async def back_to_menu(callback: CallbackQuery):
    """Handle going back to main menu"""
    await callback.message.edit_text(
        "Main Menu:\n\n/book - Book a service\n/appointments - View your appointments",
    )
    
    # Answer callback query
    await callback.answer()

def register_handlers(dp: Dispatcher):
    """Register client handlers"""
    # Command handlers
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_book, Command("book"))
    dp.message.register(cmd_appointments, Command("appointments"))
    
    # Booking flow handlers
    dp.callback_query.register(service_selected, F.data.startswith("service_"))
    dp.callback_query.register(date_selected, F.data.startswith("date_"))
    dp.callback_query.register(time_selected, F.data.startswith("time_"))
    dp.callback_query.register(booking_confirmed, F.data.startswith("confirm_"))
    dp.callback_query.register(booking_canceled, F.data == "cancel_booking")
    dp.callback_query.register(back_to_dates, F.data == "back_to_dates")
    dp.callback_query.register(back_to_time, F.data.startswith("back_to_time_"))
    
    # Appointment management handlers
    dp.callback_query.register(view_appointment, F.data.startswith("view_appointment_"))
    dp.callback_query.register(cancel_appointment, F.data.startswith("cancel_appointment_"))
    dp.callback_query.register(back_to_menu, F.data == "back_to_menu")
