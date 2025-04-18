
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Copy } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

const CodePreview = () => {
  const [copied, setCopied] = useState("");

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopied(id);
    setTimeout(() => setCopied(""), 2000);
  };

  const codeSnippets = {
    main: `# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from dotenv import load_dotenv
import os

from handlers.client_handlers import register_client_handlers
from handlers.admin_handlers import register_admin_handlers
from handlers.ceo_handlers import register_ceo_handlers
from middlewares.role_middleware import RoleMiddleware
from database.sheets_manager import SheetsManager

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Initialize Google Sheets manager
sheets_manager = SheetsManager(GOOGLE_CREDENTIALS_FILE, SPREADSHEET_ID)

# Register middleware
dp.middleware.setup(RoleMiddleware(sheets_manager))

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/help", description="Show help"),
        BotCommand(command="/book", description="Book a service"),
        BotCommand(command="/appointments", description="View your appointments")
    ]
    await bot.set_my_commands(commands)

async def main():
    # Register all handlers
    register_client_handlers(dp, sheets_manager)
    register_admin_handlers(dp, sheets_manager)
    register_ceo_handlers(dp, sheets_manager)
    
    # Set bot commands
    await set_commands(bot)
    
    # Start polling
    try:
        await dp.start_polling()
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())`,

    sheetsManager: `# database/sheets_manager.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class SheetsManager:
    def __init__(self, credentials_file, spreadsheet_id):
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive']
        
        # Authenticate using the credentials
        credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        self.spreadsheet = client.open_by_key(spreadsheet_id)
        
        # Access each worksheet
        self.services_sheet = self.spreadsheet.worksheet('Services')
        self.clients_sheet = self.spreadsheet.worksheet('Clients')
        self.appointments_sheet = self.spreadsheet.worksheet('Appointments')
        self.history_sheet = self.spreadsheet.worksheet('History')
    
    # User methods
    def get_user(self, user_id):
        try:
            cell = self.clients_sheet.find(str(user_id))
            if cell:
                row = self.clients_sheet.row_values(cell.row)
                return {
                    'user_id': row[0],
                    'username': row[1],
                    'full_name': row[2],
                    'role': row[3]
                }
            return None
        except gspread.exceptions.CellNotFound:
            return None
    
    def add_user(self, user_id, username, full_name, role='client'):
        # Check if user already exists
        if self.get_user(user_id):
            return False
        
        # Add new user
        self.clients_sheet.append_row([str(user_id), username, full_name, role])
        return True
    
    def update_user_role(self, user_id, new_role):
        user = self.get_user(user_id)
        if not user:
            return False
        
        cell = self.clients_sheet.find(str(user_id))
        self.clients_sheet.update_cell(cell.row, 4, new_role)  # Assuming role is in column 4
        return True
    
    # Service methods
    def get_all_services(self):
        # Skip header row
        rows = self.services_sheet.get_all_values()[1:]
        services = []
        for row in rows:
            services.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3]
            })
        return services
    
    def get_service(self, service_id):
        try:
            cell = self.services_sheet.find(str(service_id))
            if cell:
                row = self.services_sheet.row_values(cell.row)
                return {
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3]
                }
            return None
        except gspread.exceptions.CellNotFound:
            return None
    
    def add_service(self, name, description, price):
        # Generate new ID (just increment the highest current ID)
        all_services = self.get_all_services()
        new_id = '1'
        if all_services:
            max_id = max([int(s['id']) for s in all_services])
            new_id = str(max_id + 1)
        
        # Add new service
        self.services_sheet.append_row([new_id, name, description, str(price)])
        return new_id
    
    def delete_service(self, service_id):
        try:
            cell = self.services_sheet.find(str(service_id))
            if cell:
                self.services_sheet.delete_row(cell.row)
                return True
            return False
        except gspread.exceptions.CellNotFound:
            return False
    
    # Appointment methods
    def book_appointment(self, user_id, service_id, date, time):
        # Validate service exists
        service = self.get_service(service_id)
        if not service:
            return False
        
        # Generate new appointment ID
        all_appointments = self.get_all_appointments()
        new_id = '1'
        if all_appointments:
            max_id = max([int(a['id']) for a in all_appointments])
            new_id = str(max_id + 1)
        
        # Add new appointment
        self.appointments_sheet.append_row([
            new_id, str(user_id), service_id, date, time, 'confirmed'
        ])
        
        # Add to history
        self.add_to_history(user_id, service_id, date, time, service['price'])
        
        return new_id
    
    def get_user_appointments(self, user_id):
        appointments = []
        try:
            # Find all cells with user_id
            cells = self.appointments_sheet.findall(str(user_id))
            for cell in cells:
                row = self.appointments_sheet.row_values(cell.row)
                # Make sure it's actually in the user_id column (index 1)
                if cell.col == 2:  # Column B (index 1 + 1)
                    appointments.append({
                        'id': row[0],
                        'user_id': row[1],
                        'service_id': row[2],
                        'date': row[3],
                        'time': row[4],
                        'status': row[5]
                    })
            return appointments
        except gspread.exceptions.CellNotFound:
            return []
    
    def get_all_appointments(self):
        # Skip header row
        rows = self.appointments_sheet.get_all_values()[1:]
        appointments = []
        for row in rows:
            if len(row) >= 6:  # Ensure row has enough elements
                appointments.append({
                    'id': row[0],
                    'user_id': row[1],
                    'service_id': row[2],
                    'date': row[3],
                    'time': row[4],
                    'status': row[5]
                })
        return appointments
    
    def cancel_appointment(self, appointment_id, user_id=None):
        try:
            cell = self.appointments_sheet.find(str(appointment_id))
            if cell:
                row = self.appointments_sheet.row_values(cell.row)
                # If user_id is provided, make sure it matches
                if user_id and row[1] != str(user_id):
                    return False
                
                # Update status to canceled
                self.appointments_sheet.update_cell(cell.row, 6, 'canceled')  # Assuming status is in column 6
                return True
            return False
        except gspread.exceptions.CellNotFound:
            return False
    
    # History and analytics methods
    def add_to_history(self, user_id, service_id, date, time, amount):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history_sheet.append_row([
            timestamp, str(user_id), service_id, date, time, str(amount)
        ])
    
    def get_history(self, start_date=None, end_date=None, user_id=None):
        # Skip header row
        rows = self.history_sheet.get_all_values()[1:]
        history = []
        
        for row in rows:
            # Apply filters
            if user_id and row[1] != str(user_id):
                continue
                
            timestamp = row[0]
            if start_date and timestamp < start_date:
                continue
            if end_date and timestamp > end_date:
                continue
                
            history.append({
                'timestamp': row[0],
                'user_id': row[1],
                'service_id': row[2],
                'date': row[3],
                'time': row[4],
                'amount': row[5]
            })
        
        return history
    
    def get_statistics(self, start_date=None, end_date=None):
        history = self.get_history(start_date, end_date)
        
        # Calculate statistics
        total_bookings = len(history)
        total_revenue = sum([float(entry['amount']) for entry in history])
        
        # Service popularity
        service_counts = {}
        for entry in history:
            service_id = entry['service_id']
            if service_id in service_counts:
                service_counts[service_id] += 1
            else:
                service_counts[service_id] = 1
        
        # Get most popular service
        most_popular_service = None
        if service_counts:
            most_popular_id = max(service_counts, key=service_counts.get)
            most_popular_service = self.get_service(most_popular_id)
        
        return {
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'service_popularity': service_counts,
            'most_popular_service': most_popular_service
        }`,

    clientHandlers: `# handlers/client_handlers.py
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from database.sheets_manager import SheetsManager
from keyboards.client_keyboards import get_services_keyboard, get_appointments_keyboard, get_confirmation_keyboard

class BookingStates(StatesGroup):
    waiting_for_service = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_confirmation = State()

def register_client_handlers(dp: Dispatcher, sheets_manager: SheetsManager):
    # Start command
    @dp.message_handler(commands=['start'])
    async def cmd_start(message: types.Message):
        user_id = message.from_user.id
        username = message.from_user.username or ""
        full_name = message.from_user.full_name
        
        # Register user if not already registered
        user = sheets_manager.get_user(user_id)
        if not user:
            sheets_manager.add_user(user_id, username, full_name)
            
        await message.answer(
            f"Welcome, {full_name}! 👋\n\n"
            f"This bot helps you book services. Use /book to make an appointment "
            f"or /appointments to view your existing bookings."
        )
    
    # Help command
    @dp.message_handler(commands=['help'])
    async def cmd_help(message: types.Message):
        await message.answer(
            "📋 Available commands:\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/book - Book a service\n"
            "/appointments - View your appointments\n"
        )
    
    # Book command - start booking process
    @dp.message_handler(commands=['book'])
    async def cmd_book(message: types.Message):
        services = sheets_manager.get_all_services()
        if not services:
            await message.answer("Sorry, no services are available at the moment.")
            return
        
        keyboard = get_services_keyboard(services)
        await message.answer("Please select a service:", reply_markup=keyboard)
        await BookingStates.waiting_for_service.set()
    
    # Handle service selection
    @dp.callback_query_handler(lambda c: c.data.startswith('service_'), state=BookingStates.waiting_for_service)
    async def process_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
        service_id = callback_query.data.split('_')[1]
        service = sheets_manager.get_service(service_id)
        
        if not service:
            await callback_query.message.answer("Sorry, this service is no longer available.")
            await state.finish()
            return
        
        # Store selected service
        await state.update_data(service_id=service_id, service_name=service['name'])
        
        await callback_query.message.answer(
            f"You selected: {service['name']}\n"
            f"Price: {service['price']}\n\n"
            f"Please enter the date for your appointment (YYYY-MM-DD):"
        )
        await BookingStates.waiting_for_date.set()
        await callback_query.answer()
    
    # Handle date input
    @dp.message_handler(state=BookingStates.waiting_for_date)
    async def process_date(message: types.Message, state: FSMContext):
        date = message.text.strip()
        
        # Here you would add validation for the date format and availability
        # For simplicity, we'll just accept any input
        
        await state.update_data(date=date)
        await message.answer("Please enter the time for your appointment (HH:MM):")
        await BookingStates.waiting_for_time.set()
    
    # Handle time input
    @dp.message_handler(state=BookingStates.waiting_for_time)
    async def process_time(message: types.Message, state: FSMContext):
        time = message.text.strip()
        
        # Here you would add validation for the time format and availability
        # For simplicity, we'll just accept any input
        
        user_data = await state.get_data()
        service_name = user_data['service_name']
        date = user_data['date']
        
        await state.update_data(time=time)
        
        # Ask for confirmation
        keyboard = get_confirmation_keyboard()
        await message.answer(
            f"Please confirm your booking:\n\n"
            f"Service: {service_name}\n"
            f"Date: {date}\n"
            f"Time: {time}\n\n"
            f"Is this correct?",
            reply_markup=keyboard
        )
        await BookingStates.waiting_for_confirmation.set()
    
    # Handle confirmation
    @dp.callback_query_handler(lambda c: c.data in ['confirm', 'cancel'], state=BookingStates.waiting_for_confirmation)
    async def process_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
        if callback_query.data == 'confirm':
            user_data = await state.get_data()
            user_id = callback_query.from_user.id
            service_id = user_data['service_id']
            date = user_data['date']
            time = user_data['time']
            
            # Book the appointment
            appointment_id = sheets_manager.book_appointment(user_id, service_id, date, time)
            
            if appointment_id:
                await callback_query.message.answer(
                    f"✅ Your appointment has been confirmed!\n\n"
                    f"Appointment ID: {appointment_id}\n"
                    f"You can view or cancel your appointments using the /appointments command."
                )
            else:
                await callback_query.message.answer(
                    "❌ Sorry, there was an error booking your appointment. Please try again."
                )
        else:
            await callback_query.message.answer("Booking cancelled.")
        
        await state.finish()
        await callback_query.answer()
    
    # Appointments command
    @dp.message_handler(commands=['appointments'])
    async def cmd_appointments(message: types.Message):
        user_id = message.from_user.id
        appointments = sheets_manager.get_user_appointments(user_id)
        
        if not appointments:
            await message.answer("You don't have any appointments.")
            return
        
        # Create keyboard with appointments
        keyboard = get_appointments_keyboard(appointments)
        
        await message.answer("Your appointments:", reply_markup=keyboard)
    
    # Handle appointment selection (for cancellation)
    @dp.callback_query_handler(lambda c: c.data.startswith('cancel_appointment_'))
    async def process_cancel_appointment(callback_query: types.CallbackQuery):
        appointment_id = callback_query.data.split('_')[2]
        user_id = callback_query.from_user.id
        
        success = sheets_manager.cancel_appointment(appointment_id, user_id)
        
        if success:
            await callback_query.message.answer(f"✅ Appointment {appointment_id} has been cancelled.")
        else:
            await callback_query.message.answer("❌ Failed to cancel the appointment.")
        
        await callback_query.answer()`,

    adminHandlers: `# handlers/admin_handlers.py
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.sheets_manager import SheetsManager
from keyboards.admin_keyboards import get_admin_keyboard, get_all_appointments_keyboard, get_services_management_keyboard

class ServiceStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()

def register_admin_handlers(dp: Dispatcher, sheets_manager: SheetsManager):
    # Admin command - show admin panel
    @dp.message_handler(commands=['admin'], is_admin=True)
    async def cmd_admin(message: types.Message):
        keyboard = get_admin_keyboard()
        await message.answer("Admin Panel", reply_markup=keyboard)
    
    # Handle admin panel actions
    @dp.callback_query_handler(lambda c: c.data in ['admin_services', 'admin_appointments', 'admin_stats'], is_admin=True)
    async def process_admin_actions(callback_query: types.CallbackQuery):
        if callback_query.data == 'admin_services':
            keyboard = get_services_management_keyboard()
            await callback_query.message.answer("Service Management:", reply_markup=keyboard)
        
        elif callback_query.data == 'admin_appointments':
            appointments = sheets_manager.get_all_appointments()
            if not appointments:
                await callback_query.message.answer("No appointments found.")
            else:
                keyboard = get_all_appointments_keyboard(appointments)
                await callback_query.message.answer("All Appointments:", reply_markup=keyboard)
        
        elif callback_query.data == 'admin_stats':
            stats = sheets_manager.get_statistics()
            
            # Format the statistics message
            message_text = (
                f"📊 Statistics:\n\n"
                f"Total Bookings: {stats['total_bookings']}\n"
                f"Total Revenue: {stats['total_revenue']}\n"
            )
            
            if stats['most_popular_service']:
                message_text += f"\nMost Popular Service: {stats['most_popular_service']['name']}"
            
            await callback_query.message.answer(message_text)
        
        await callback_query.answer()
    
    # Add Service - start process
    @dp.callback_query_handler(lambda c: c.data == 'add_service', is_admin=True)
    async def process_add_service(callback_query: types.CallbackQuery):
        await callback_query.message.answer("Please enter the name of the new service:")
        await ServiceStates.waiting_for_name.set()
        await callback_query.answer()
    
    # Handle service name input
    @dp.message_handler(state=ServiceStates.waiting_for_name, is_admin=True)
    async def process_service_name(message: types.Message, state: FSMContext):
        name = message.text.strip()
        await state.update_data(name=name)
        await message.answer("Please enter a description for the service:")
        await ServiceStates.waiting_for_description.set()
    
    # Handle service description input
    @dp.message_handler(state=ServiceStates.waiting_for_description, is_admin=True)
    async def process_service_description(message: types.Message, state: FSMContext):
        description = message.text.strip()
        await state.update_data(description=description)
        await message.answer("Please enter the price for the service:")
        await ServiceStates.waiting_for_price.set()
    
    # Handle service price input
    @dp.message_handler(state=ServiceStates.waiting_for_price, is_admin=True)
    async def process_service_price(message: types.Message, state: FSMContext):
        try:
            price = float(message.text.strip())
            user_data = await state.get_data()
            
            # Add the new service
            service_id = sheets_manager.add_service(
                user_data['name'],
                user_data['description'],
                price
            )
            
            await message.answer(f"✅ Service added successfully! ID: {service_id}")
        except ValueError:
            await message.answer("❌ Invalid price. Please enter a number.")
        finally:
            await state.finish()
    
    # Delete Service
    @dp.callback_query_handler(lambda c: c.data == 'delete_service', is_admin=True)
    async def process_delete_service(callback_query: types.CallbackQuery):
        services = sheets_manager.get_all_services()
        if not services:
            await callback_query.message.answer("No services available to delete.")
            await callback_query.answer()
            return
        
        # Create inline keyboard with services
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for service in services:
            keyboard.add(types.InlineKeyboardButton(
                text=f"{service['name']} - {service['price']}",
                callback_data=f"delete_service_{service['id']}"
            ))
        
        await callback_query.message.answer("Select a service to delete:", reply_markup=keyboard)
        await callback_query.answer()
    
    # Handle service deletion selection
    @dp.callback_query_handler(lambda c: c.data.startswith('delete_service_'), is_admin=True)
    async def process_delete_service_selection(callback_query: types.CallbackQuery):
        service_id = callback_query.data.split('_')[2]
        success = sheets_manager.delete_service(service_id)
        
        if success:
            await callback_query.message.answer(f"✅ Service {service_id} deleted successfully.")
        else:
            await callback_query.message.answer("❌ Failed to delete the service.")
        
        await callback_query.answer()
    
    # Handle appointment cancellation (admin)
    @dp.callback_query_handler(lambda c: c.data.startswith('admin_cancel_'), is_admin=True)
    async def process_admin_cancel_appointment(callback_query: types.CallbackQuery):
        appointment_id = callback_query.data.split('_')[2]
        success = sheets_manager.cancel_appointment(appointment_id)
        
        if success:
            await callback_query.message.answer(f"✅ Appointment {appointment_id} cancelled successfully.")
        else:
            await callback_query.message.answer("❌ Failed to cancel the appointment.")
        
        await callback_query.answer()`,

    ceoHandlers: `# handlers/ceo_handlers.py
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database.sheets_manager import SheetsManager

class AdminManagementStates(StatesGroup):
    waiting_for_user_id = State()
    waiting_for_role = State()

def register_ceo_handlers(dp: Dispatcher, sheets_manager: SheetsManager):
    # CEO command - show CEO panel
    @dp.message_handler(commands=['ceo'], is_ceo=True)
    async def cmd_ceo(message: types.Message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(text="Manage Administrators", callback_data="manage_admins"),
            types.InlineKeyboardButton(text="View Full Statistics", callback_data="full_stats")
        )
        await message.answer("CEO Panel", reply_markup=keyboard)
    
    # Handle CEO panel actions
    @dp.callback_query_handler(lambda c: c.data in ['manage_admins', 'full_stats'], is_ceo=True)
    async def process_ceo_actions(callback_query: types.CallbackQuery):
        if callback_query.data == 'manage_admins':
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                types.InlineKeyboardButton(text="Add Administrator", callback_data="add_admin"),
                types.InlineKeyboardButton(text="Remove Administrator", callback_data="remove_admin"),
                types.InlineKeyboardButton(text="List Administrators", callback_data="list_admins")
            )
            await callback_query.message.answer("Administrator Management:", reply_markup=keyboard)
        
        elif callback_query.data == 'full_stats':
            # Get statistics for all time
            stats = sheets_manager.get_statistics()
            
            # Create a detailed statistics message
            message_text = (
                f"📊 Full Statistics Report:\n\n"
                f"Total Bookings: {stats['total_bookings']}\n"
                f"Total Revenue: {stats['total_revenue']}\n\n"
            )
            
            if stats['service_popularity']:
                message_text += "Service Popularity:\n"
                for service_id, count in stats['service_popularity'].items():
                    service = sheets_manager.get_service(service_id)
                    if service:
                        message_text += f"- {service['name']}: {count} bookings\n"
            
            if stats['most_popular_service']:
                message_text += f"\nMost Popular Service: {stats['most_popular_service']['name']}"
            
            await callback_query.message.answer(message_text)
        
        await callback_query.answer()
    
    # Add Administrator - start process
    @dp.callback_query_handler(lambda c: c.data == 'add_admin', is_ceo=True)
    async def process_add_admin(callback_query: types.CallbackQuery):
        await callback_query.message.answer(
            "Please enter the Telegram user ID of the person you want to make an administrator:"
        )
        await AdminManagementStates.waiting_for_user_id.set()
        await callback_query.answer()
    
    # Handle user ID input for admin role
    @dp.message_handler(state=AdminManagementStates.waiting_for_user_id, is_ceo=True)
    async def process_admin_user_id(message: types.Message, state: FSMContext):
        try:
            user_id = int(message.text.strip())
            
            # Check if user exists
            user = sheets_manager.get_user(user_id)
            if not user:
                await message.answer(
                    "❌ This user is not registered in the system. "
                    "They need to start the bot first."
                )
                await state.finish()
                return
            
            # Store user ID and ask for role
            await state.update_data(user_id=user_id)
            
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            keyboard.add(
                types.InlineKeyboardButton(text="Admin", callback_data="set_role_admin"),
                types.InlineKeyboardButton(text="Client", callback_data="set_role_client")
            )
            
            await message.answer(
                f"User found: {user['full_name']}\n"
                f"Current role: {user['role']}\n\n"
                f"Select the new role:",
                reply_markup=keyboard
            )
            await AdminManagementStates.waiting_for_role.set()
            
        except ValueError:
            await message.answer("❌ Invalid user ID. Please enter a numeric ID.")
            await state.finish()
    
    # Handle role selection
    @dp.callback_query_handler(
        lambda c: c.data.startswith('set_role_'),
        state=AdminManagementStates.waiting_for_role,
        is_ceo=True
    )
    async def process_role_selection(callback_query: types.CallbackQuery, state: FSMContext):
        role = callback_query.data.split('_')[2]
        user_data = await state.get_data()
        user_id = user_data['user_id']
        
        # Update user role
        success = sheets_manager.update_user_role(user_id, role)
        
        if success:
            await callback_query.message.answer(f"✅ User {user_id} role updated to {role}.")
        else:
            await callback_query.message.answer("❌ Failed to update user role.")
        
        await state.finish()
        await callback_query.answer()
    
    # List Administrators
    @dp.callback_query_handler(lambda c: c.data == 'list_admins', is_ceo=True)
    async def process_list_admins(callback_query: types.CallbackQuery):
        # Ideally, add a method to sheets_manager to get all users with admin role
        # For now, we'll simulate it
        
        # This would typically call a method like:
        # admins = sheets_manager.get_users_by_role('admin')
        
        # For demonstration, we'll send a message indicating this functionality
        await callback_query.message.answer(
            "This would display a list of all administrators. "
            "You would need to implement a method in SheetsManager to get users by role."
        )
        await callback_query.answer()
    
    # Remove Administrator
    @dp.callback_query_handler(lambda c: c.data == 'remove_admin', is_ceo=True)
    async def process_remove_admin(callback_query: types.CallbackQuery):
        # This would typically call a method to get all admins and display them for selection
        # Then another handler would handle the selection and demote the admin to client role
        
        # For demonstration, we'll send a message indicating this functionality
        await callback_query.message.answer(
            "This would display a list of administrators that you can select to remove. "
            "After selection, their role would be changed to 'client'."
        )
        await callback_query.answer()`,

    middleware: `# middlewares/role_middleware.py
from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database.sheets_manager import SheetsManager

class RoleMiddleware(BaseMiddleware):
    def __init__(self, sheets_manager: SheetsManager):
        super().__init__()
        self.sheets_manager = sheets_manager
    
    async def on_process_message(self, message: types.Message, data: dict):
        # Get user from database
        user = self.sheets_manager.get_user(message.from_user.id)
        
        # If this is a new user, add them
        if not user:
            self.sheets_manager.add_user(
                message.from_user.id,
                message.from_user.username or "",
                message.from_user.full_name,
                role='client'  # Default role
            )
            user = self.sheets_manager.get_user(message.from_user.id)
        
        # Add role flags to the data dict
        if user:
            data['is_admin'] = user['role'] in ['admin', 'ceo']
            data['is_ceo'] = user['role'] == 'ceo'
        else:
            data['is_admin'] = False
            data['is_ceo'] = False
        
        # For admin and CEO commands, check permissions
        if message.get_command() in ['/admin', '/ceo']:
            required_role = 'admin' if message.get_command() == '/admin' else 'ceo'
            if user and user['role'] == required_role or user and user['role'] == 'ceo':
                return
            else:
                await message.answer("You don't have permission to use this command.")
                raise CancelHandler()
    
    async def on_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        # Get user from database
        user = self.sheets_manager.get_user(callback_query.from_user.id)
        
        # Add role flags to the data dict
        if user:
            data['is_admin'] = user['role'] in ['admin', 'ceo']
            data['is_ceo'] = user['role'] == 'ceo'
        else:
            data['is_admin'] = False
            data['is_ceo'] = False`,

    clientKeyboards: `# keyboards/client_keyboards.py
from aiogram import types
from database.sheets_manager import SheetsManager

def get_services_keyboard(services):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for service in services:
        keyboard.add(types.InlineKeyboardButton(
            text=f"{service['name']} - {service['price']}",
            callback_data=f"service_{service['id']}"
        ))
    return keyboard

def get_appointments_keyboard(appointments):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for appointment in appointments:
        # We would typically get the service name here
        # For simplicity, we'll just use the service ID
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
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(text="✅ Confirm", callback_data="confirm"),
        types.InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")
    )
    return keyboard`,

    adminKeyboards: `# keyboards/admin_keyboards.py
from aiogram import types

def get_admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Manage Services", callback_data="admin_services"),
        types.InlineKeyboardButton(text="Manage Appointments", callback_data="admin_appointments"),
        types.InlineKeyboardButton(text="View Statistics", callback_data="admin_stats")
    )
    return keyboard

def get_services_management_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton(text="Add Service", callback_data="add_service"),
        types.InlineKeyboardButton(text="Delete Service", callback_data="delete_service")
    )
    return keyboard

def get_all_appointments_keyboard(appointments):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for appointment in appointments:
        # We would typically get the client name and service name here
        # For simplicity, we'll just use IDs
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
    
    return keyboard`,

    dotenv: `# .env.example
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE=path/to/your/credentials.json
SPREADSHEET_ID=your_spreadsheet_id_here
`
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Python Code Structure</CardTitle>
          <CardDescription>
            View the full code for building your Telegram bot with Google Sheets integration
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="main" className="space-y-4">
            <TabsList className="flex flex-wrap gap-2">
              <TabsTrigger value="main">Main</TabsTrigger>
              <TabsTrigger value="sheets">Sheets Manager</TabsTrigger>
              <TabsTrigger value="client">Client Handlers</TabsTrigger>
              <TabsTrigger value="admin">Admin Handlers</TabsTrigger>
              <TabsTrigger value="ceo">CEO Handlers</TabsTrigger>
              <TabsTrigger value="middleware">Middleware</TabsTrigger>
              <TabsTrigger value="keyboards">Keyboards</TabsTrigger>
              <TabsTrigger value="dotenv">Environment</TabsTrigger>
            </TabsList>

            {Object.entries({
              main: codeSnippets.main,
              sheets: codeSnippets.sheetsManager,
              client: codeSnippets.clientHandlers,
              admin: codeSnippets.adminHandlers,
              ceo: codeSnippets.ceoHandlers,
              middleware: codeSnippets.middleware,
              keyboards: `${codeSnippets.clientKeyboards}\n\n${codeSnippets.adminKeyboards}`,
              dotenv: codeSnippets.dotenv,
            }).map(([key, code]) => (
              <TabsContent key={key} value={key}>
                <div className="bg-gray-900 text-gray-100 p-4 rounded-md font-mono text-sm overflow-auto max-h-[500px] relative">
                  <pre>{code}</pre>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="absolute top-2 right-2 h-6 w-6 text-gray-400 hover:text-white"
                    onClick={() => handleCopy(code, key)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
                {copied === key && <p className="text-green-500 text-xs mt-1">Copied to clipboard!</p>}
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Project Structure</CardTitle>
          <CardDescription>
            The recommended file organization for your Telegram bot
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-gray-100 p-4 rounded-md font-mono text-sm">
            <pre>
{`project_folder/
├── main.py               # Main entry point
├── .env                  # Environment variables
├── credentials.json      # Google API credentials
├── database/
│   └── sheets_manager.py # Google Sheets integration
├── handlers/
│   ├── client_handlers.py # Client command handlers
│   ├── admin_handlers.py  # Admin command handlers
│   └── ceo_handlers.py    # CEO command handlers
├── keyboards/
│   ├── client_keyboards.py # Client-specific keyboards
│   └── admin_keyboards.py  # Admin-specific keyboards
└── middlewares/
    └── role_middleware.py  # Role-based access control`}
            </pre>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CodePreview;
