from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.db_api import service_commands, appointment_commands, master_commands
from keyboards import admin_keyboards

# Define states for admin operations
class AdminServiceStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()

class AdminMasterStates(StatesGroup):
    adding_name = State()
    adding_telegram = State()
    adding_address = State()
    adding_location = State()
    editing_name = State()
    editing_telegram = State()
    editing_address = State()
    editing_location = State()
    editing_start_time = State()
    editing_end_time = State()

async def cmd_admin(message: Message, role: str):
    """Handle the /admin command"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await message.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await message.answer(
        "Панель администратора",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )

async def back_to_admin(callback: CallbackQuery, role: str):
    """Return to the main admin panel"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Панель администратора",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )
    
    await callback.answer()

async def admin_services(callback: CallbackQuery, role: str):
    """Handle admin services menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Управление услугами",
        reply_markup=admin_keyboards.get_services_management_keyboard()
    )
    
    await callback.answer()

async def add_service_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the add service flow"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Set state to adding name
    await state.set_state(AdminServiceStates.adding_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите название новой услуги:"
    )
    
    await callback.answer()

async def add_service_name(message: Message, state: FSMContext):
    """Handle adding service name"""
    # Save the name
    await state.update_data(name=message.text)
    
    # Move to description state
    await state.set_state(AdminServiceStates.adding_description)
    
    await message.answer("Пожалуйста, введите описание услуги:")

async def add_service_description(message: Message, state: FSMContext):
    """Handle adding service description"""
    # Save the description
    await state.update_data(description=message.text)
    
    # Move to price state
    await state.set_state(AdminServiceStates.adding_price)
    
    await message.answer("Пожалуйста, введите цену услуги:")

async def add_service_price(message: Message, state: FSMContext):
    """Handle adding service price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Save the price
    await state.update_data(price=price)
    
    # Move to duration state
    await state.set_state(AdminServiceStates.adding_duration)
    
    await message.answer("Пожалуйста, введите продолжительность услуги в минутах (например, 60):")

async def add_service_duration(message: Message, state: FSMContext):
    """Handle adding service duration"""
    # Validate duration
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Неверный формат продолжительности. Пожалуйста, введите целое число.")
        return
    
    # Save the duration
    await state.update_data(duration=duration)
    
    # Get all data
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    duration = data["duration"]
    
    # Add the service
    service = await service_commands.add_service(name, description, price, duration)
    
    if service:
        await message.answer(
            f"✅ Услуга добавлена успешно!\n\nНазвание: {name}\nОписание: {description}\nЦена: {price}\nПродолжительность: {duration}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить услугу. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_services(callback: CallbackQuery, role: str):
    """Handle viewing all services"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all services
    services = await service_commands.get_all_services()
    
    if not services:
        await callback.message.edit_text(
            "Услуги не найдены. Вы можете добавить услуги, используя кнопку 'Добавить услугу'.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Все услуги:",
            reply_markup=admin_keyboards.get_all_services_keyboard(services)
        )
    
    await callback.answer()

async def admin_view_service(callback: CallbackQuery, role: str):
    """Handle viewing a specific service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Get service details
    service = await service_commands.get_service(service_id)
    
    if not service:
        await callback.message.edit_text(
            "Услуга не найдена.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Данные услуги:\n\nID: {service['id']}\nНазвание: {service['name']}\nОписание: {service['description']}\nЦена: {service['price']}\nПродолжительность: {service['duration']} минут",
            reply_markup=admin_keyboards.get_service_actions_keyboard(service_id)
        )
    
    await callback.answer()

async def edit_service(callback: CallbackQuery, role: str):
    """Handle editing a service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=admin_keyboards.get_edit_service_keyboard(service_id)
    )
    
    await callback.answer()

async def edit_service_name_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service name"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing name
    await state.set_state(AdminServiceStates.editing_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое название для услуги:"
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
            f"✅ Название услуги обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить название услуги. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_description_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service description"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing description
    await state.set_state(AdminServiceStates.editing_description)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое описание для услуги:"
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
            f"✅ Описание услуги обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить описание услуги. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_price_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service price"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing price
    await state.set_state(AdminServiceStates.editing_price)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новую цену для услуги:"
    )
    
    await callback.answer()

async def edit_service_price(message: Message, state: FSMContext):
    """Handle updating service price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update the service price
    success = await service_commands.update_service(service_id, price=price)
    
    if success:
        await message.answer(
            f"✅ Цена услуги обновлена: {price}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить цену услуги. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_duration_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service duration"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Set state to editing duration
    await state.set_state(AdminServiceStates.editing_duration)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новую продолжительность для услуги в минутах:"
    )
    
    await callback.answer()

async def edit_service_duration(message: Message, state: FSMContext):
    """Handle updating service duration"""
    # Validate duration
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Неверный формат продолжительности. Пожалуйста, введите целое число.")
        return
    
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update the service duration
    success = await service_commands.update_service(service_id, duration=duration)
    
    if success:
        await message.answer(
            f"✅ Продолжительность услуги обновлена: {duration} минут",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить продолжительность услуги. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_service_confirm(callback: CallbackQuery, role: str):
    """Confirm service deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту услугу?",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(service_id)
    )
    
    await callback.answer()

async def delete_service(callback: CallbackQuery, role: str):
    """Handle service deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Delete the service
    success = await service_commands.delete_service(service_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Услуга успешно удалена!",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить услугу. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_appointments(callback: CallbackQuery, role: str):
    """Handle admin appointments menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all appointments
    appointments = await appointment_commands.get_all_appointments()
    
    if not appointments:
        await callback.message.edit_text(
            "Записи не найдены.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Все записи:",
            reply_markup=admin_keyboards.get_all_appointments_keyboard(appointments)
        )
    
    await callback.answer()

async def admin_view_appointment(callback: CallbackQuery, role: str):
    """Handle viewing a specific appointment"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Запись не найдена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        # Format details
        await callback.message.edit_text(
            f"Данные записи:\n\nID: {appointment['id']}\nДата: {appointment['date']}\nВремя: {appointment['time']}\nСтатус: {appointment['status']}",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, appointment['status'])
        )
    
    await callback.answer()

async def admin_cancel_appointment_confirm(callback: CallbackQuery, role: str):
    """Confirm appointment cancellation"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите отменить эту запись?",
        reply_markup=admin_keyboards.get_cancel_confirmation_keyboard(appointment_id)
    )
    
    await callback.answer()

async def admin_cancel_appointment(callback: CallbackQuery, role: str):
    """Handle appointment cancellation"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[3]
    
    # Cancel the appointment
    success = await appointment_commands.cancel_appointment(appointment_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Запись успешно отменена!",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отменить запись. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_masters(callback: CallbackQuery, role: str):
    """Handle admin masters menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Управление мастерами",
        reply_markup=admin_keyboards.get_masters_management_keyboard()
    )
    
    await callback.answer()

async def add_master_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the add master flow"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Set state to adding name
    await state.set_state(AdminMasterStates.adding_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите имя нового мастера:"
    )
    
    await callback.answer()

async def add_master_name(message: Message, state: FSMContext):
    """Handle adding master name"""
    # Save the name
    await state.update_data(name=message.text)
    
    # Move to telegram state
    await state.set_state(AdminMasterStates.adding_telegram)
    
    await message.answer("Пожалуйста, введите Telegram мастера (с @ или без):")

async def add_master_telegram(message: Message, state: FSMContext):
    """Handle adding master telegram"""
    # Format telegram username
    telegram = message.text
    if telegram and not telegram.startswith('@') and telegram != "":
        telegram = '@' + telegram
    
    # Save the telegram
    await state.update_data(telegram=telegram)
    
    # Move to address state
    await state.set_state(AdminMasterStates.adding_address)
    
    await message.answer("Пожалуйста, введите адрес мастера (где принимает клиентов):")

async def add_master_address(message: Message, state: FSMContext):
    """Handle adding master address"""
    # Save the address
    await state.update_data(address=message.text)
    
    # Move to location state
    await state.set_state(AdminMasterStates.adding_location)
    
    await message.answer("Пожалуйста, отправьте геолокацию (необязательно, можно отправить '-' чтобы пропустить):")

async def add_master_location(message: Message, state: FSMContext):
    """Handle adding master location"""
    location = ""
    
    # Check if it's a location message
    if message.location:
        location = f"{message.location.latitude},{message.location.longitude}"
    elif message.text != "-":
        location = message.text
    
    # Save the location
    await state.update_data(location=location)
    
    # Get all data
    data = await state.get_data()
    name = data["name"]
    telegram = data["telegram"]
    address = data["address"]
    
    # Add the master, linking it to the current user ID (admin)
    user_id = message.from_user.id
    master = await master_commands.add_master(user_id, name, telegram, address, location)
    
    if master:
        await message.answer(
            f"✅ Мастер добавлен успешно!\n\nИмя: {name}\nTelegram: {telegram}\nАдрес: {address}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить мастера. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_masters(callback: CallbackQuery, role: str):
    """Handle viewing all masters"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all masters
    masters = await master_commands.get_all_masters()
    
    if not masters:
        await callback.message.edit_text(
            "Мастера не найдены. Вы можете добавить мастеров, используя кнопку 'Добавить мастера'.",
            reply_markup=admin_keyboards.get_masters_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Все мастера:",
            reply_markup=admin_keyboards.get_all_masters_keyboard(masters)
        )
    
    await callback.answer()

async def admin_view_master(callback: CallbackQuery, role: str):
    """Handle viewing a specific master"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Get master details
    master = await master_commands.get_master(master_id)
    
    if not master:
        await callback.message.edit_text(
            "Мастер не найден.",
            reply_markup=admin_keyboards.get_masters_management_keyboard()
        )
    else:
        # Format details
        notification_status = "Включены" if master.get('notification_enabled', True) else "Выключены"
        
        await callback.message.edit_text(
            f"Данные мастера:\n\nID: {master['id']}\nИмя: {master['name']}\nTelegram: {master['telegram']}\nАдрес: {master['address']}\nУведомления: {notification_status}",
            reply_markup=admin_keyboards.get_master_actions_keyboard(master_id)
        )
    
    await callback.answer()

async def edit_master(callback: CallbackQuery, role: str):
    """Handle editing a master"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=admin_keyboards.get_edit_master_keyboard(master_id)
    )
    
    await callback.answer()

async def edit_master_name_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing master name"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Save master ID in state
    await state.update_data(master_id=master_id)
    
    # Set state to editing name
    await state.set_state(AdminMasterStates.editing_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое имя для мастера:"
    )
    
    await callback.answer()

async def edit_master_name(message: Message, state: FSMContext):
    """Handle updating master name"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update the master name
    success = await master_commands.update_master(master_id, name=message.text)
    
    if success:
        await message.answer(
            f"✅ Имя мастера обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить имя мастера. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_telegram_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing master telegram"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Save master ID in state
    await state.update_data(master_id=master_id)
    
    # Set state to editing telegram
    await state.set_state(AdminMasterStates.editing_telegram)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новый Telegram для мастера:"
    )
    
    await callback.answer()

async def edit_master_telegram(message: Message, state: FSMContext):
    """Handle updating master telegram"""
    # Format telegram username
    telegram = message.text
    if telegram and not telegram.startswith('@') and telegram != "":
        telegram = '@' + telegram
    
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update the master telegram
    success = await master_commands.update_master(master_id, telegram=telegram)
    
    if success:
        await message.answer(
            f"✅ Telegram мастера обновлен: {telegram}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить Telegram мастера. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_address_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing master address"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Save master ID in state
    await state.update_data(master_id=master_id)
    
    # Set state to editing address
    await state.set_state(AdminMasterStates.editing_address)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новый адрес для мастера:"
    )
    
    await callback.answer()

async def edit_master_address(message: Message, state: FSMContext):
    """Handle updating master address"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update the master address
    success = await master_commands.update_master(master_id, address=message.text)
    
    if success:
        await message.answer(
            f"✅ Адрес мастера обновлен: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить адрес мастера. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_location_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing master location"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Save master ID in state
    await state.update_data(master_id=master_id)
    
    # Set state to editing location
    await state.set_state(AdminMasterStates.editing_location)
    
    await callback.message.edit_
