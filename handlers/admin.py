
# Adding template-based service creation functionality

from aiogram import Dispatcher, F, Bot
from aiogram import types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.db_api import service_commands, appointment_commands, master_commands
from keyboards import admin_keyboards

# Define states for admin operations
class AdminServiceStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    adding_category = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()
    editing_category = State()
    updating_price = State()  # State for bulk price update

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

class AdminCategoryStates(StatesGroup):
    adding_name = State()
    editing_name = State()

class AdminOfferStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()

async def cmd_admin(message: Message, role: str):
    """Admin command handler"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await message.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await message.answer(
        "Панель администратора. Выберите действие:",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )

async def back_to_admin(callback: CallbackQuery, role: str):
    """Handle back to admin menu button"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Панель администратора. Выберите действие:",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )
    
    await callback.answer()

# Admin services menu
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

# Template-based service creation functionality
async def admin_template_categories(callback: CallbackQuery, role: str):
    """Show template categories for quick service creation"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all template categories
    categories = await service_commands.get_all_template_categories()
    
    if not categories:
        await callback.message.edit_text(
            "Шаблоны категорий не найдены. Пожалуйста, проверьте настройки таблицы.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Выберите категорию услуг, которую вы хотите добавить в свой бизнес:",
            reply_markup=admin_keyboards.get_template_categories_keyboard(categories)
        )
    
    await callback.answer()

async def admin_add_category_services(callback: CallbackQuery, role: str):
    """Add all template services for a category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category name from callback data
    category_name = callback.data.split('_', 3)[3]
    
    # Add template services for this category
    success, message = await service_commands.add_template_services_to_category(category_name)
    
    if success:
        # Get services added to display
        category = await service_commands.get_category_by_name(category_name)
        if category:
            services = await service_commands.get_services_in_category(category['id'])
            
            # Create message with all services that need price setting
            if services:
                service_list = "\n".join([f"• {s['name']}" for s in services])
                await callback.message.edit_text(
                    f"{message}\n\nСписок услуг в категории '{category_name}':\n{service_list}\n\nТеперь вам нужно установить цены для этих услуг.",
                    reply_markup=admin_keyboards.get_category_services_price_keyboard(category['id'])
                )
            else:
                await callback.message.edit_text(
                    f"{message}\n\nНо услуги не были добавлены. Пожалуйста, попробуйте еще раз.",
                    reply_markup=admin_keyboards.get_back_to_admin_keyboard()
                )
        else:
            await callback.message.edit_text(
                f"{message}",
                reply_markup=admin_keyboards.get_back_to_admin_keyboard()
            )
    else:
        await callback.message.edit_text(
            f"Ошибка: {message}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def update_category_services_price(callback: CallbackQuery, state: FSMContext, role: str):
    """Update prices for all services in a category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[3]
    
    # Save category ID in state
    await state.update_data(category_id=category_id)
    
    # Get the category and its services
    category = await service_commands.get_category(category_id)
    if not category:
        await callback.message.edit_text(
            "Категория не найдена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
        return
    
    services = await service_commands.get_services_in_category(category_id)
    if not services:
        await callback.message.edit_text(
            f"В категории '{category['name']}' нет услуг.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
        return
    
    # Create list of services
    service_list = "\n".join([f"• {s['name']}" for s in services])
    
    # Set state for bulk price update
    await state.set_state(AdminServiceStates.updating_price)
    
    await callback.message.edit_text(
        f"Установка цен для услуг в категории '{category['name']}':\n\n{service_list}\n\nПожалуйста, введите цену для всех услуг в этой категории:"
    )
    
    await callback.answer()

async def process_category_services_price(message: Message, state: FSMContext):
    """Process bulk price update for services in a category"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Get category ID from state
    data = await state.get_data()
    category_id = data.get("category_id")
    
    if not category_id:
        await message.answer(
            "Ошибка: не найден ID категории.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    # Get services in this category
    services = await service_commands.get_services_in_category(category_id)
    if not services:
        await message.answer(
            "В выбранной категории нет услуг.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
        await state.clear()
        return
    
    # Update price for all services
    updated_count = 0
    for service in services:
        success = await service_commands.update_service(service.get('id'), price=price)
        if success:
            updated_count += 1
    
    # Get category name
    category = await service_commands.get_category(category_id)
    category_name = category.get('name', 'Неизвестная категория') if category else 'Неизвестная категория'
    
    await message.answer(
        f"✅ Цены обновлены для {updated_count} услуг в категории '{category_name}'.",
        reply_markup=admin_keyboards.get_back_to_admin_keyboard()
    )
    
    await state.clear()

# Regular service management
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
    
    await message.answer("Пожалуйста, введите продолжительность услуги в минутах (например, 15, 30, 60):")

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
    
    # Get categories for selection
    categories = await service_commands.get_all_categories()
    
    if categories:
        # Create a keyboard for category selection
        keyboard = InlineKeyboardBuilder()
        for category in categories:
            keyboard.button(
                text=f"{category['name']}",
                callback_data=f"add_service_category_{category['id']}"
            )
        
        keyboard.button(
            text="Без категории",
            callback_data="add_service_category_none"
        )
        
        keyboard.adjust(1)  # One button per row
        
        # Move to category state
        await state.set_state(AdminServiceStates.adding_category)
        
        await message.answer(
            "Пожалуйста, выберите категорию для услуги:",
            reply_markup=keyboard.as_markup()
        )
    else:
        # No categories, add service without a category
        await add_service_final(message, state, None)

async def add_service_category(callback: CallbackQuery, state: FSMContext):
    """Handle category selection for a new service"""
    # Extract category ID from callback data
    category_id = None
    if callback.data != "add_service_category_none":
        category_id = callback.data.split('_')[3]
    
    await add_service_final(callback.message, state, category_id)
    await callback.answer()

async def add_service_final(message, state: FSMContext, category_id=None):
    """Finalize adding a service"""
    # Get all data
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    duration = data["duration"]
    
    # Add the service
    service = await service_commands.add_service(name, description, price, duration, category_id)
    
    category_text = ""
    if category_id:
        category = await service_commands.get_category(category_id)
        if category:
            category_text = f"\nКатегория: {category['name']}"
    
    if service:
        await message.answer(
            f"✅ Услуга добавлена успешно!\n\nНазвание: {name}\nОписание: {description}\nЦена: {price}\nПродолжительность: {duration}{category_text}",
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
    
    # Get services by category
    services_by_category = await service_commands.get_services_by_category()
    
    if not services_by_category:
        await callback.message.edit_text(
            "Услуги не найдены. Вы можете добавить услуги, используя кнопку 'Быстрое создание услуг' или 'Добавить услугу'.",
            reply_markup=admin_keyboards.get_services_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Выберите категорию для просмотра услуг:",
            reply_markup=admin_keyboards.get_service_categories_keyboard(services_by_category)
        )
    
    await callback.answer()

async def view_category_services(callback: CallbackQuery, role: str):
    """Handle viewing services in a category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category name from callback data
    category_name = callback.data.split('_', 3)[3]
    
    # Get services by category
    services_by_category = await service_commands.get_services_by_category()
    
    if category_name in services_by_category and services_by_category[category_name]:
        await callback.message.edit_text(
            f"Услуги в категории '{category_name}':",
            reply_markup=admin_keyboards.get_category_services_keyboard(services_by_category[category_name], category_name)
        )
    else:
        await callback.message.edit_text(
            f"В категории '{category_name}' нет услуг.",
            reply_markup=admin_keyboards.get_back_to_services_keyboard()
        )
    
    await callback.answer()

async def back_to_services(callback: CallbackQuery, role: str):
    """Handle back to services menu button"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Управление услугами",
        reply_markup=admin_keyboards.get_services_management_keyboard()
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
            reply_markup=admin_keyboards.get_back_to_services_keyboard()
        )
    else:
        # Get category if exists
        category_text = ""
        if 'category_id' in service:
            category = await service_commands.get_category(service['category_id'])
            if category:
                category_text = f"\nКатегория: {category['name']}"
        
        await callback.message.edit_text(
            f"Данные услуги:\n\nID: {service['id']}\nНазвание: {service['name']}\nОписание: {service['description']}\nЦена: {service['price']}\nПродолжительность: {service['duration']}{category_text}",
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
        "Пожалуйста, введите новую продолжительность для услуги (в минутах):"
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

async def edit_service_category_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing service category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[3]
    
    # Save service ID in state
    await state.update_data(service_id=service_id)
    
    # Get all categories for selection
    categories = await service_commands.get_all_categories()
    
    if not categories:
        await callback.message.edit_text(
            "Нет доступных категорий. Сначала создайте категории.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
        await callback.answer()
        return
    
    # Create keyboard with categories
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.button(
            text=category.get('name', 'Без названия'),
            callback_data=f"set_service_category_{service_id}_{category['id']}"
        )
    
    keyboard.button(
        text="Без категории",
        callback_data=f"set_service_category_{service_id}_none"
    )
    
    keyboard.button(
        text="Назад",
        callback_data=f"admin_view_service_{service_id}"
    )
    
    keyboard.adjust(1)
    
    await callback.message.edit_text(
        "Выберите категорию для услуги:",
        reply_markup=keyboard.as_markup()
    )
    
    await callback.answer()

async def set_service_category(callback: CallbackQuery, role: str):
    """Set the category for a service"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract data from callback
    parts = callback.data.split('_')
    service_id = parts[3]
    category_id = None
    if parts[4] != "none":
        category_id = parts[4]
    
    # Update service category
    success = await service_commands.update_service(service_id, category_id=category_id)
    
    if success:
        # Get updated category info
        category_text = "Без категории"
        if category_id:
            category = await service_commands.get_category(category_id)
            if category:
                category_text = category.get('name', 'Неизвестная категория')
        
        await callback.message.edit_text(
            f"✅ Категория услуги обновлена на: {category_text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось обновить категорию услуги. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def delete_service_confirm(callback: CallbackQuery, role: str):
    """Confirm service deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract service ID from callback data
    service_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту услугу? Это действие нельзя отменить.",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(service_id, "service")
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

# Category management
async def admin_categories(callback: CallbackQuery, role: str):
    """Handle admin categories menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Управление категориями услуг",
        reply_markup=admin_keyboards.get_categories_management_keyboard()
    )
    
    await callback.answer()

async def add_category_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the add category flow"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Set state to adding name
    await state.set_state(AdminCategoryStates.adding_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите название новой категории услуг:"
    )
    
    await callback.answer()

async def add_category_name(message: Message, state: FSMContext):
    """Handle adding category name"""
    # Save the name
    name = message.text
    
    # Add the category
    category = await service_commands.add_category(name)
    
    if category:
        await message.answer(
            f"✅ Категория добавлена успешно!\n\nНазвание: {name}\n\nВы можете добавить услуги в эту категорию с помощью функции 'Быстрое создание услуг'",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить категорию. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_categories(callback: CallbackQuery, role: str):
    """Handle viewing all categories"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all categories
    categories = await service_commands.get_all_categories()
    
    if not categories:
        await callback.message.edit_text(
            "Категории не найдены. Вы можете добавить категории, используя кнопку 'Добавить категорию'.",
            reply_markup=admin_keyboards.get_categories_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Все категории:",
            reply_markup=admin_keyboards.get_all_categories_keyboard(categories)
        )
    
    await callback.answer()

async def admin_view_category(callback: CallbackQuery, role: str):
    """Handle viewing a specific category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[3]
    
    # Get category details
    category = await service_commands.get_category(category_id)
    
    if not category:
        await callback.message.edit_text(
            "Категория не найдена.",
            reply_markup=admin_keyboards.get_categories_management_keyboard()
        )
    else:
        # Get services in this category
        services = await service_commands.get_services_in_category(category_id)
        service_count = len(services)
        
        await callback.message.edit_text(
            f"Данные категории:\n\nID: {category['id']}\nНазвание: {category['name']}\nКоличество услуг: {service_count}",
            reply_markup=admin_keyboards.get_category_actions_keyboard(category_id)
        )
    
    await callback.answer()

async def edit_category(callback: CallbackQuery, role: str):
    """Handle editing a category"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=admin_keyboards.get_edit_category_keyboard(category_id)
    )
    
    await callback.answer()

async def edit_category_name_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing category name"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[3]
    
    # Save category ID in state
    await state.update_data(category_id=category_id)
    
    # Set state to editing name
    await state.set_state(AdminCategoryStates.editing_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое название для категории:"
    )
    
    await callback.answer()

async def edit_category_name(message: Message, state: FSMContext):
    """Handle updating category name"""
    # Get category ID from state
    data = await state.get_data()
    category_id = data["category_id"]
    
    # Update the category name
    success = await service_commands.update_category(category_id, name=message.text)
    
    if success:
        await message.answer(
            f"✅ Название категории обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить название категории. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_category_confirm(callback: CallbackQuery, role: str):
    """Confirm category deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить эту категорию? Услуги в этой категории будут без категории.",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(category_id, "category")
    )
    
    await callback.answer()

async def delete_category(callback: CallbackQuery, role: str):
    """Handle category deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract category ID from callback data
    category_id = callback.data.split('_')[3]
    
    # Delete the category
    success = await service_commands.delete_category(category_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Категория успешно удалена!",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить категорию. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Special offers functions
async def admin_offers(callback: CallbackQuery, role: str):
    """Handle admin offers menu"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    await callback.message.edit_text(
        "Управление специальными предложениями",
        reply_markup=admin_keyboards.get_offers_management_keyboard()
    )
    
    await callback.answer()

async def add_offer_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start the add offer flow"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Set state to adding name
    await state.set_state(AdminOfferStates.adding_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите название нового специального предложения:"
    )
    
    await callback.answer()

async def add_offer_name(message: Message, state: FSMContext):
    """Handle adding offer name"""
    # Save the name
    await state.update_data(name=message.text)
    
    # Move to description state
    await state.set_state(AdminOfferStates.adding_description)
    
    await message.answer("Пожалуйста, введите описание специального предложения:")

async def add_offer_description(message: Message, state: FSMContext):
    """Handle adding offer description"""
    # Save the description
    await state.update_data(description=message.text)
    
    # Move to price state
    await state.set_state(AdminOfferStates.adding_price)
    
    await message.answer("Пожалуйста, введите цену специального предложения:")

async def add_offer_price(message: Message, state: FSMContext):
    """Handle adding offer price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Save the price
    await state.update_data(price=price)
    
    # Move to duration state
    await state.set_state(AdminOfferStates.adding_duration)
    
    await message.answer("Пожалуйста, введите продолжительность спец. предложения в минутах (например, 60):")

async def add_offer_duration(message: Message, state: FSMContext):
    """Handle adding offer duration"""
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
    
    # Add the offer
    offer = await service_commands.add_offer(name, description, price, duration)
    
    if offer:
        await message.answer(
            f"✅ Специальное предложение добавлено успешно!\n\nНазвание: {name}\nОписание: {description}\nЦена: {price}\nПродолжительность: {duration}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить специальное предложение. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_offers(callback: CallbackQuery, role: str):
    """Handle viewing all offers"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Get all offers
    offers = await service_commands.get_all_offers()
    
    if not offers:
        await callback.message.edit_text(
            "Спец. предложения не найдены. Вы можете добавить предложения, используя кнопку 'Добавить спец. предложение'.",
            reply_markup=admin_keyboards.get_offers_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            "Все специальные предложения:",
            reply_markup=admin_keyboards.get_all_offers_keyboard(offers)
        )
    
    await callback.answer()

async def admin_view_offer(callback: CallbackQuery, role: str):
    """Handle viewing a specific offer"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Get offer details
    offer = await service_commands.get_offer(offer_id)
    
    if not offer:
        await callback.message.edit_text(
            "Спец. предложение не найдено.",
            reply_markup=admin_keyboards.get_offers_management_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Данные спец. предложения:\n\nID: {offer['id']}\nНазвание: {offer['name']}\nОписание: {offer['description']}\nЦена: {offer['price']}\nПродолжительность: {offer['duration']} минут",
            reply_markup=admin_keyboards.get_offer_actions_keyboard(offer_id)
        )
    
    await callback.answer()

async def edit_offer(callback: CallbackQuery, role: str):
    """Handle editing an offer"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Что вы хотите отредактировать?",
        reply_markup=admin_keyboards.get_edit_offer_keyboard(offer_id)
    )
    
    await callback.answer()

# Handlers for editing offer fields
async def edit_offer_name_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing offer name"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Save offer ID in state
    await state.update_data(offer_id=offer_id)
    
    # Set state to editing name
    await state.set_state(AdminOfferStates.editing_name)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое название для специального предложения:"
    )
    
    await callback.answer()

async def edit_offer_name(message: Message, state: FSMContext):
    """Handle updating offer name"""
    # Get offer ID from state
    data = await state.get_data()
    offer_id = data["offer_id"]
    
    # Update the offer name
    success = await service_commands.update_offer(offer_id, name=message.text)
    
    if success:
        await message.answer(
            f"✅ Название спец. предложения обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить название спец. предложения. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_offer_description_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing offer description"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Save offer ID in state
    await state.update_data(offer_id=offer_id)
    
    # Set state to editing description
    await state.set_state(AdminOfferStates.editing_description)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новое описание для специального предложения:"
    )
    
    await callback.answer()

async def edit_offer_description(message: Message, state: FSMContext):
    """Handle updating offer description"""
    # Get offer ID from state
    data = await state.get_data()
    offer_id = data["offer_id"]
    
    # Update the offer description
    success = await service_commands.update_offer(offer_id, description=message.text)
    
    if success:
        await message.answer(
            f"✅ Описание спец. предложения обновлено: {message.text}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить описание спец. предложения. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_offer_price_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing offer price"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Save offer ID in state
    await state.update_data(offer_id=offer_id)
    
    # Set state to editing price
    await state.set_state(AdminOfferStates.editing_price)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новую цену для специального предложения:"
    )
    
    await callback.answer()

async def edit_offer_price(message: Message, state: FSMContext):
    """Handle updating offer price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Get offer ID from state
    data = await state.get_data()
    offer_id = data["offer_id"]
    
    # Update the offer price
    success = await service_commands.update_offer(offer_id, price=price)
    
    if success:
        await message.answer(
            f"✅ Цена спец. предложения обновлена: {price}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить цену спец. предложения. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_offer_duration_start(callback: CallbackQuery, state: FSMContext, role: str):
    """Start editing offer duration"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Save offer ID in state
    await state.update_data(offer_id=offer_id)
    
    # Set state to editing duration
    await state.set_state(AdminOfferStates.editing_duration)
    
    await callback.message.edit_text(
        "Пожалуйста, введите новую продолжительность для специального предложения (в минутах):"
    )
    
    await callback.answer()

async def edit_offer_duration(message: Message, state: FSMContext):
    """Handle updating offer duration"""
    # Validate duration
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Неверный формат продолжительности. Пожалуйста, введите целое число.")
        return
    
    # Get offer ID from state
    data = await state.get_data()
    offer_id = data["offer_id"]
    
    # Update the offer duration
    success = await service_commands.update_offer(offer_id, duration=duration)
    
    if success:
        await message.answer(
            f"✅ Продолжительность спец. предложения обновлена: {duration} минут",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить продолжительность спец. предложения. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_offer_confirm(callback: CallbackQuery, role: str):
    """Confirm offer deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить это специальное предложение? Это действие нельзя отменить.",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(offer_id, "offer")
    )
    
    await callback.answer()

async def delete_offer(callback: CallbackQuery, role: str):
    """Handle offer deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[3]
    
    # Delete the offer
    success = await service_commands.delete_offer(offer_id)
    
    if success:
        await callback.message.edit_text(
            "✅ Специальное предложение успешно удалено!",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить специальное предложение. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Appointment functions
async def admin_appointments(callback: CallbackQuery, role: str):
    """Handle admin appointments menu"""
    # Check permissions and rest of implementation
    # ... keep existing code (admin_appointments function)

async def admin_appointments_date(callback: CallbackQuery, role: str):
    """Handle viewing appointments for a specific date"""
    # Check permissions and rest of implementation
    # ... keep existing code (admin_appointments_date function)

async def admin_view_appointment(callback: CallbackQuery, role: str, bot: Bot):
    """Handle viewing a specific appointment"""
    # Check permissions and rest of implementation
    # ... keep existing code (admin_view_appointment function)

async def admin_confirm_appointment(callback: CallbackQuery, role: str, bot: Bot):
    """Handle confirming a pending appointment"""
    # Check permissions and rest of implementation
    # ... keep existing code (admin_confirm_appointment function)

# Appointment status update handlers
async def mark_completed(callback: CallbackQuery, role: str, bot: Bot):
    """Mark an appointment as completed"""
    # Check permissions and rest of implementation
    # ... keep existing code (mark_completed function)

async def mark_paid(callback: CallbackQuery, role: str, bot: Bot):
    """Mark an appointment as paid"""
    # Check permissions and rest of implementation
    # ... keep existing code (mark_paid function)

async def set_payment_method(callback: CallbackQuery, role: str):
    """Set payment method for an appointment"""
    # Check permissions and rest of implementation
    # ... keep existing code (set_payment_method function)

def register_handlers(dp: Dispatcher):
    """Register admin handlers"""
    # Command handlers
    dp.message.register(cmd_admin, Command("admin"))
    
    # Main admin menu handlers
    dp.callback_query.register(back_to_admin, F.data == "back_to_admin")
    dp.callback_query.register(admin_services, F.data == "admin_services")
    dp.callback_query.register(admin_masters, F.data == "admin_masters")
    dp.callback_query.register(admin_appointments, F.data == "admin_appointments")
    dp.callback_query.register(admin_offers, F.data == "admin_offers")
    dp.callback_query.register(admin_categories, F.data == "admin_categories")
    
    # Template-based service creation
    dp.callback_query.register(admin_template_categories, F.data == "template_categories")
    dp.callback_query.register(admin_add_category_services, F.data.startswith("template_category_"))
    dp.callback_query.register(update_category_services_price, F.data.startswith("update_category_price_"))
    dp.message.register(process_category_services_price, AdminServiceStates.updating_price)
    dp.callback_query.register(back_to_services, F.data == "back_to_services")
    
    # Service management handlers
    dp.callback_query.register(add_service_start, F.data == "add_service")
    dp.message.register(add_service_name, AdminServiceStates.adding_name)
    dp.message.register(add_service_description, AdminServiceStates.adding_description)
    dp.message.register(add_service_price, AdminServiceStates.adding_price)
    dp.message.register(add_service_duration, AdminServiceStates.adding_duration)
    dp.callback_query.register(add_service_category, F.data.startswith("add_service_category_"))
    dp.callback_query.register(view_services, F.data == "view_services")
    dp.callback_query.register(view_category_services, F.data.startswith("view_category_services_"))
    dp.callback_query.register(admin_view_service, F.data.startswith("admin_view_service_"))
    
    # Service editing handlers
    dp.callback_query.register(edit_service, F.data.startswith("edit_service_"))
    dp.callback_query.register(edit_service_name_start, F.data.startswith("edit_service_name_"))
    dp.message.register(edit_service_name, AdminServiceStates.editing_name)
    dp.callback_query.register(edit_service_description_start, F.data.startswith("edit_service_description_"))
    dp.message.register(edit_service_description, AdminServiceStates.editing_description)
    dp.callback_query.register(edit_service_price_start, F.data.startswith("edit_service_price_"))
    dp.message.register(edit_service_price, AdminServiceStates.editing_price)
    dp.callback_query.register(edit_service_duration_start, F.data.startswith("edit_service_duration_"))
    dp.message.register(edit_service_duration, AdminServiceStates.editing_duration)
    dp.callback_query.register(edit_service_category_start, F.data.startswith("edit_service_category_"))
    dp.callback_query.register(set_service_category, F.data.startswith("set_service_category_"))
    
    # Service deletion handlers
    dp.callback_query.register(delete_service_confirm, F.data.startswith("delete_service_confirm_"))
    dp.callback_query.register(delete_service, F.data.startswith("confirm_delete_service_"))
    
    # Category management handlers
    dp.callback_query.register(add_category_start, F.data == "add_category")
    dp.message.register(add_category_name, AdminCategoryStates.adding_name)
    dp.callback_query.register(view_categories, F.data == "view_categories")
    dp.callback_query.register(admin_view_category, F.data.startswith("admin_view_category_"))
    dp.callback_query.register(edit_category, F.data.startswith("edit_category_"))
    dp.callback_query.register(edit_category_name_start, F.data.startswith("edit_category_name_"))
    dp.message.register(edit_category_name, AdminCategoryStates.editing_name)
    dp.callback_query.register(delete_category_confirm, F.data.startswith("delete_category_confirm_"))
    dp.callback_query.register(delete_category, F.data.startswith("confirm_delete_category_"))
    
    # Special offers management handlers
    dp.callback_query.register(add_offer_start, F.data == "add_offer")
    dp.message.register(add_offer_name, AdminOfferStates.adding_name)
    dp.message.register(add_offer_description, AdminOfferStates.adding_description)
    dp.message.register(add_offer_price, AdminOfferStates.adding_price)
    dp.message.register(add_offer_duration, AdminOfferStates.adding_duration)
    dp.callback_query.register(view_offers, F.data == "view_offers")
    dp.callback_query.register(admin_view_offer, F.data.startswith("admin_view_offer_"))
    dp.callback_query.register(edit_offer, F.data.startswith("edit_offer_"))
    dp.callback_query.register(edit_offer_name_start, F.data.startswith("edit_offer_name_"))
    dp.message.register(edit_offer_name, AdminOfferStates.editing_name)
    dp.callback_query.register(edit_offer_description_start, F.data.startswith("edit_offer_description_"))
    dp.message.register(edit_offer_description, AdminOfferStates.editing_description)
    dp.callback_query.register(edit_offer_price_start, F.data.startswith("edit_offer_price_"))
    dp.message.register(edit_offer_price, AdminOfferStates.editing_price)
    dp.callback_query.register(edit_offer_duration_start, F.data.startswith("edit_offer_duration_"))
    dp.message.register(edit_offer_duration, AdminOfferStates.editing_duration)
    dp.callback_query.register(delete_offer_confirm, F.data.startswith("delete_offer_confirm_"))
    dp.callback_query.register(delete_offer, F.data.startswith("confirm_delete_offer_"))
    
    # Master management handlers
    dp.callback_query.register(add_master_start, F.data == "add_master")
    dp.message.register(add_master_name, AdminMasterStates.adding_name)
    dp.message.register(add_master_telegram, AdminMasterStates.adding_telegram)
    dp.message.register(add_master_address, AdminMasterStates.adding_address)
    dp.message.register(add_master_location, AdminMasterStates.adding_location)
    dp.callback_query.register(view_masters, F.data == "view_masters_admin")
    
    # Appointment management handlers
    dp.callback_query.register(admin_appointments, F.data == "admin_appointments")
    dp.callback_query.register(admin_appointments_date, F.data.startswith("admin_appointments_date_"))
    dp.callback_query.register(mark_completed, F.data.startswith("mark_completed_"))
    dp.callback_query.register(mark_paid, F.data.startswith("mark_paid_"))
    dp.callback_query.register(set_payment_method, F.data.startswith("set_payment_"))
    dp.callback_query.register(admin_confirm_appointment, F.data.startswith("admin_confirm_appointment_"))
    
    # Master editing handlers
    dp.callback_query.register(admin_view_master, F.data.startswith("admin_view_master_"))
    dp.callback_query.register(edit_master, F.data.startswith("edit_master_"))
    dp.callback_query.register(edit_master_name_start, F.data.startswith("edit_master_name_"))
    dp.message.register(edit_master_name, AdminMasterStates.editing_name)
    dp.callback_query.register(edit_master_telegram_start, F.data.startswith("edit_master_telegram_"))
    dp.message.register(edit_master_telegram, AdminMasterStates.editing_telegram)
    dp.callback_query.register(edit_master_address_start, F.data.startswith("edit_master_address_"))
    dp.message.register(edit_master_address, AdminMasterStates.editing_address)
    dp.callback_query.register(edit_master_location_start, F.data.startswith("edit_master_location_"))
    dp.message.register(edit_master_location, AdminMasterStates.editing_location)
    
    # Appointment cancellation handlers
    dp.callback_query.register(admin_cancel_appointment_confirm, F.data.startswith("admin_cancel_appointment_"))
    dp.callback_query.register(admin_cancel_appointment, F.data.startswith("confirm_cancel_"))

