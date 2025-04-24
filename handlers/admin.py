
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta
import calendar
import re
import os

from keyboards import admin_keyboards
from utils.db_api import service_commands, master_commands, appointment_commands, user_commands

# States for service management
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
    setting_category_price = State()
    
# States for master management
class AdminMasterStates(StatesGroup):
    adding_name = State()
    adding_telegram = State()
    adding_address = State()
    adding_location = State()
    editing_name = State()
    editing_telegram = State()
    editing_address = State()
    editing_location = State()

# States for appointments
class AdminAppointmentStates(StatesGroup):
    selecting_date = State()
    
# States for categories
class AdminCategoryStates(StatesGroup):
    adding_name = State()
    editing_name = State()

# States for special offers
class AdminOfferStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()

# Create router
dp = Router()

# Admin panel
async def admin_start(message: Message):
    """Admin start command handler"""
    await message.answer(
        "👑 Админ-панель\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )
    
# Back to admin panel
async def back_to_admin(callback: CallbackQuery):
    """Back to admin panel handler"""
    await callback.message.edit_text(
        "👑 Админ-панель\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_admin_keyboard()
    )
    await callback.answer()

# Services management
async def admin_services(callback: CallbackQuery):
    """Admin services handler"""
    await callback.message.edit_text(
        "🛠 Управление услугами\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_services_management_keyboard()
    )
    await callback.answer()

# Template categories
async def template_categories(callback: CallbackQuery):
    """Show template categories for quick service creation"""
    # Get template categories
    categories = await service_commands.get_template_categories()
    
    await callback.message.edit_text(
        "✨ Быстрое создание услуг\n\nВыберите категорию для создания услуг:",
        reply_markup=admin_keyboards.get_template_categories_keyboard(categories)
    )
    await callback.answer()
    
async def template_category_selected(callback: CallbackQuery):
    """Handle template category selection"""
    # Extract category from callback data
    category = callback.data.replace("template_category_", "")
    
    # Create services from template
    created = await service_commands.create_services_from_template(category)
    
    if created:
        category_id = created["category_id"]
        services_count = created["count"]
        
        await callback.message.edit_text(
            f"✅ Создано {services_count} услуг в категории '{category}'.\n\n"
            "Теперь вы можете настроить цены для всех услуг этой категории или просмотреть их по отдельности.",
            reply_markup=admin_keyboards.get_category_services_price_keyboard(category_id)
        )
    else:
        await callback.message.edit_text(
            f"❌ Не удалось создать услуги для категории '{category}'.",
            reply_markup=admin_keyboards.get_back_to_services_keyboard()
        )
    
    await callback.answer()
    
async def update_category_price_start(callback: CallbackQuery, state: FSMContext):
    """Start updating price for all services in category"""
    # Extract category ID from callback data
    category_id = callback.data.replace("update_category_price_", "")
    
    # Save category ID to state
    await state.update_data(category_id=category_id)
    
    # Ask for price
    await callback.message.edit_text(
        "Введите цену для всех услуг в этой категории:",
    )
    
    # Set state
    await state.set_state(AdminServiceStates.setting_category_price)
    await callback.answer()
    
async def update_category_price(message: Message, state: FSMContext):
    """Update price for all services in category"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Get category ID from state
    data = await state.get_data()
    category_id = data["category_id"]
    
    # Update prices
    updated = await service_commands.update_category_prices(category_id, price)
    
    if updated:
        await message.answer(
            f"✅ Цены обновлены для {updated} услуг.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось обновить цены.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

# Add service
async def add_service_start(callback: CallbackQuery, state: FSMContext):
    """Start adding service"""
    await callback.message.edit_text(
        "➕ Добавление услуги\n\nВведите название услуги:"
    )
    
    # Set state
    await state.set_state(AdminServiceStates.adding_name)
    await callback.answer()

async def add_service_name(message: Message, state: FSMContext):
    """Handle adding service name"""
    # Save name
    await state.update_data(name=message.text)
    
    # Ask for description
    await message.answer("Введите описание услуги:")
    
    # Set state
    await state.set_state(AdminServiceStates.adding_description)

async def add_service_description(message: Message, state: FSMContext):
    """Handle adding service description"""
    # Save description
    await state.update_data(description=message.text)
    
    # Ask for price
    await message.answer("Введите цену услуги в рублях (например, 1000):")
    
    # Set state
    await state.set_state(AdminServiceStates.adding_price)

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
        await message.answer("Неверный формат. Пожалуйста, введите число минут.")
        return
    
    # Get categories
    categories = await service_commands.get_categories()
    
    # Create keyboard with categories
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category['name'], callback_data=f"add_service_category_{category['id']}")
    
    builder.adjust(1)
    
    # Save duration
    await state.update_data(duration=duration)
    
    # Ask for category
    await message.answer(
        "Выберите категорию для услуги:",
        reply_markup=builder.as_markup()
    )
    
    # Set state
    await state.set_state(AdminServiceStates.adding_category)

async def add_service_category(callback: CallbackQuery, state: FSMContext):
    """Handle adding service category"""
    # Extract category ID from callback data
    category_id = callback.data.replace("add_service_category_", "")
    
    # Get all data
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    duration = data["duration"]
    
    # Add the service
    service = await service_commands.add_service(name, description, price, duration, category_id)
    
    if service:
        await callback.message.edit_text(
            f"✅ Услуга добавлена успешно!\n\nНазвание: {name}\nОписание: {description}\nЦена: {price} руб.\nПродолжительность: {duration} мин.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось добавить услугу. Пожалуйста, попробуйте позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()
    await callback.answer()

# View services
async def view_services(callback: CallbackQuery):
    """View services handler"""
    # Get services grouped by category
    services_by_category = await service_commands.get_services_by_category()
    
    await callback.message.edit_text(
        "📋 Услуги по категориям\n\nВыберите категорию услуг для просмотра:",
        reply_markup=admin_keyboards.get_service_categories_keyboard(services_by_category)
    )
    await callback.answer()
    
async def view_category_services(callback: CallbackQuery):
    """View services in category"""
    # Extract category name from callback data
    category_name = callback.data.replace("view_category_services_", "")
    
    # Get services by category
    services = await service_commands.get_services_by_category_name(category_name)
    
    await callback.message.edit_text(
        f"📋 Услуги в категории '{category_name}'\n\nВыберите услугу для управления:",
        reply_markup=admin_keyboards.get_category_services_keyboard(services, category_name)
    )
    await callback.answer()
    
async def admin_view_service(callback: CallbackQuery):
    """View service details"""
    # Extract service ID from callback data
    service_id = callback.data.replace("admin_view_service_", "")
    
    # Get service details
    service = await service_commands.get_service(service_id)
    
    if service:
        await callback.message.edit_text(
            f"🔍 Детали услуги\n\nНазвание: {service['name']}\nОписание: {service['description']}\nЦена: {service['price']} руб.\nПродолжительность: {service.get('duration', 'Не указана')} мин.\nКатегория: {service.get('category_name', 'Не указана')}",
            reply_markup=admin_keyboards.get_service_actions_keyboard(service_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Услуга не найдена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Edit service
async def edit_service(callback: CallbackQuery):
    """Edit service handler"""
    # Extract service ID from callback data
    service_id = callback.data.replace("edit_service_", "")
    
    await callback.message.edit_text(
        "✏️ Редактирование услуги\n\nВыберите, что хотите изменить:",
        reply_markup=admin_keyboards.get_edit_service_keyboard(service_id)
    )
    await callback.answer()

async def edit_service_name_start(callback: CallbackQuery, state: FSMContext):
    """Start editing service name"""
    # Extract service ID from callback data
    service_id = callback.data.replace("edit_service_name_", "")
    
    # Save service ID to state
    await state.update_data(service_id=service_id)
    
    # Ask for new name
    await callback.message.edit_text("Введите новое название услуги:")
    
    # Set state
    await state.set_state(AdminServiceStates.editing_name)
    await callback.answer()
    
async def edit_service_name(message: Message, state: FSMContext):
    """Edit service name"""
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update name
    updated = await service_commands.update_service_name(service_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Название услуги успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить название услуги.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_description_start(callback: CallbackQuery, state: FSMContext):
    """Start editing service description"""
    # Extract service ID from callback data
    service_id = callback.data.replace("edit_service_description_", "")
    
    # Save service ID to state
    await state.update_data(service_id=service_id)
    
    # Ask for new description
    await callback.message.edit_text("Введите новое описание услуги:")
    
    # Set state
    await state.set_state(AdminServiceStates.editing_description)
    await callback.answer()
    
async def edit_service_description(message: Message, state: FSMContext):
    """Edit service description"""
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update description
    updated = await service_commands.update_service_description(service_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Описание услуги успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить описание услуги.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()
    
async def edit_service_price_start(callback: CallbackQuery, state: FSMContext):
    """Start editing service price"""
    # Extract service ID from callback data
    service_id = callback.data.replace("edit_service_price_", "")
    
    # Save service ID to state
    await state.update_data(service_id=service_id)
    
    # Ask for new price
    await callback.message.edit_text("Введите новую цену услуги в рублях (например, 1000):")
    
    # Set state
    await state.set_state(AdminServiceStates.editing_price)
    await callback.answer()
    
async def edit_service_price(message: Message, state: FSMContext):
    """Edit service price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update price
    updated = await service_commands.update_service_price(service_id, price)
    
    if updated:
        await message.answer(
            "✅ Цена услуги успешно изменена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить цену услуги.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_service_duration_start(callback: CallbackQuery, state: FSMContext):
    """Start editing service duration"""
    # Extract service ID from callback data
    service_id = callback.data.replace("edit_service_duration_", "")
    
    # Save service ID to state
    await state.update_data(service_id=service_id)
    
    # Ask for new duration
    await callback.message.edit_text("Введите новую продолжительность услуги в минутах (например, 15, 30, 60):")
    
    # Set state
    await state.set_state(AdminServiceStates.editing_duration)
    await callback.answer()
    
async def edit_service_duration(message: Message, state: FSMContext):
    """Edit service duration"""
    # Validate duration
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Неверный формат. Пожалуйста, введите число минут.")
        return
    
    # Get service ID from state
    data = await state.get_data()
    service_id = data["service_id"]
    
    # Update duration
    updated = await service_commands.update_service_duration(service_id, duration)
    
    if updated:
        await message.answer(
            "✅ Продолжительность услуги успешно изменена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить продолжительность услуги.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_service_confirm(callback: CallbackQuery):
    """Confirm service deletion"""
    # Extract service ID from callback data
    service_id = callback.data.replace("delete_service_confirm_", "")
    
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить эту услугу?",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(service_id, "service")
    )
    await callback.answer()
    
async def delete_service(callback: CallbackQuery):
    """Delete service"""
    # Extract service ID from callback data
    service_id = callback.data.replace("confirm_delete_service_", "")
    
    # Delete service
    deleted = await service_commands.delete_service(service_id)
    
    if deleted:
        await callback.message.edit_text(
            "✅ Услуга успешно удалена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить услугу.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Category management
async def admin_categories(callback: CallbackQuery):
    """Admin categories handler"""
    await callback.message.edit_text(
        "🗂 Управление категориями\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_categories_management_keyboard()
    )
    await callback.answer()

async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Start adding category"""
    await callback.message.edit_text(
        "➕ Добавление категории\n\nВведите название категории:"
    )
    
    # Set state
    await state.set_state(AdminCategoryStates.adding_name)
    await callback.answer()

async def add_category_name(message: Message, state: FSMContext):
    """Handle adding category name"""
    # Add category
    category = await service_commands.add_category(message.text)
    
    if category:
        await message.answer(
            f"✅ Категория '{message.text}' успешно добавлена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить категорию.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_categories(callback: CallbackQuery):
    """View categories handler"""
    # Get categories
    categories = await service_commands.get_categories()
    
    await callback.message.edit_text(
        "📋 Категории услуг\n\nВыберите категорию для управления:",
        reply_markup=admin_keyboards.get_all_categories_keyboard(categories)
    )
    await callback.answer()

async def admin_view_category(callback: CallbackQuery):
    """View category details"""
    # Extract category ID from callback data
    category_id = callback.data.replace("admin_view_category_", "")
    
    # Get category details
    category = await service_commands.get_category(category_id)
    
    if category:
        await callback.message.edit_text(
            f"🔍 Детали категории\n\nНазвание: {category['name']}",
            reply_markup=admin_keyboards.get_category_actions_keyboard(category_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Категория не найдена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def edit_category(callback: CallbackQuery):
    """Edit category handler"""
    # Extract category ID from callback data
    category_id = callback.data.replace("edit_category_", "")
    
    await callback.message.edit_text(
        "✏️ Редактирование категории\n\nВыберите, что хотите изменить:",
        reply_markup=admin_keyboards.get_edit_category_keyboard(category_id)
    )
    await callback.answer()

async def edit_category_name_start(callback: CallbackQuery, state: FSMContext):
    """Start editing category name"""
    # Extract category ID from callback data
    category_id = callback.data.replace("edit_category_name_", "")
    
    # Save category ID to state
    await state.update_data(category_id=category_id)
    
    # Ask for new name
    await callback.message.edit_text("Введите новое название категории:")
    
    # Set state
    await state.set_state(AdminCategoryStates.editing_name)
    await callback.answer()

async def edit_category_name(message: Message, state: FSMContext):
    """Edit category name"""
    # Get category ID from state
    data = await state.get_data()
    category_id = data["category_id"]
    
    # Update name
    updated = await service_commands.update_category_name(category_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Название категории успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить название категории.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_category_confirm(callback: CallbackQuery):
    """Confirm category deletion"""
    # Extract category ID from callback data
    category_id = callback.data.replace("delete_category_confirm_", "")
    
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить эту категорию?\n\nВместе с категорией будут удалены все услуги в этой категории!",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(category_id, "category")
    )
    await callback.answer()

async def delete_category(callback: CallbackQuery):
    """Delete category"""
    # Extract category ID from callback data
    category_id = callback.data.replace("confirm_delete_category_", "")
    
    # Delete category
    deleted = await service_commands.delete_category(category_id)
    
    if deleted:
        await callback.message.edit_text(
            "✅ Категория успешно удалена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить категорию.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Special offers management
async def admin_offers(callback: CallbackQuery):
    """Admin offers handler"""
    await callback.message.edit_text(
        "🌟 Управление специальными предложениями\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_offers_management_keyboard()
    )
    await callback.answer()

async def add_offer_start(callback: CallbackQuery, state: FSMContext):
    """Start adding offer"""
    await callback.message.edit_text(
        "➕ Добавление спец. предложения\n\nВведите название предложения:"
    )
    
    # Set state
    await state.set_state(AdminOfferStates.adding_name)
    await callback.answer()

async def add_offer_name(message: Message, state: FSMContext):
    """Handle adding offer name"""
    # Save name
    await state.update_data(name=message.text)
    
    # Ask for description
    await message.answer("Введите описание специального предложения:")
    
    # Set state
    await state.set_state(AdminOfferStates.adding_description)

async def add_offer_description(message: Message, state: FSMContext):
    """Handle adding offer description"""
    # Save description
    await state.update_data(description=message.text)
    
    # Ask for price
    await message.answer("Введите цену специального предложения в рублях (например, 1000):")
    
    # Set state
    await state.set_state(AdminOfferStates.adding_price)

async def add_offer_price(message: Message, state: FSMContext):
    """Handle adding offer price"""
    # Validate price
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Неверный формат цены. Пожалуйста, введите число.")
        return
    
    # Save price
    await state.update_data(price=price)
    
    # Ask for duration
    await message.answer("Введите продолжительность специального предложения в минутах (например, 15, 30, 60):")
    
    # Set state
    await state.set_state(AdminOfferStates.adding_duration)

async def add_offer_duration(message: Message, state: FSMContext):
    """Handle adding offer duration"""
    # Validate duration
    try:
        duration = int(message.text)
    except ValueError:
        await message.answer("Неверный формат. Пожалуйста, введите число минут.")
        return
    
    # Get all data
    data = await state.get_data()
    name = data["name"]
    description = data["description"]
    price = data["price"]
    
    # Add offer
    offer = await service_commands.add_offer(name, description, price, duration)
    
    if offer:
        await message.answer(
            f"✅ Специальное предложение добавлено успешно!\n\nНазвание: {name}\nОписание: {description}\nЦена: {price} руб.\nПродолжительность: {duration} мин.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить специальное предложение. Пожалуйста, попробуйте позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def view_offers(callback: CallbackQuery):
    """View offers handler"""
    # Get offers
    offers = await service_commands.get_offers()
    
    await callback.message.edit_text(
        "📋 Специальные предложения\n\nВыберите предложение для управления:",
        reply_markup=admin_keyboards.get_all_offers_keyboard(offers)
    )
    await callback.answer()

async def admin_view_offer(callback: CallbackQuery):
    """View offer details"""
    # Extract offer ID from callback data
    offer_id = callback.data.replace("admin_view_offer_", "")
    
    # Get offer details
    offer = await service_commands.get_offer(offer_id)
    
    if offer:
        await callback.message.edit_text(
            f"🔍 Детали специального предложения\n\nНазвание: {offer['name']}\nОписание: {offer['description']}\nЦена: {offer['price']} руб.\nПродолжительность: {offer.get('duration', 'Не указана')} мин.",
            reply_markup=admin_keyboards.get_offer_actions_keyboard(offer_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Специальное предложение не найдено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def edit_offer(callback: CallbackQuery):
    """Edit offer handler"""
    # Extract offer ID from callback data
    offer_id = callback.data.replace("edit_offer_", "")
    
    await callback.message.edit_text(
        "✏️ Редактирование специального предложения\n\nВыберите, что хотите изменить:",
        reply_markup=admin_keyboards.get_edit_offer_keyboard(offer_id)
    )
    await callback.answer()

async def edit_offer_name_start(callback: CallbackQuery, state: FSMContext):
    """Start editing offer name"""
    # Extract offer ID from callback data
    offer_id = callback.data.replace("edit_offer_name_", "")
    
    # Save offer ID to state
    await state.update_data(offer_id=offer_id)
    
    # Ask for new name
    await callback.message.edit_text("Введите новое название специального предложения:")
    
    # Set state
    await state.set_state(AdminOfferStates.editing_name)
    await callback.answer()

async def edit_offer_name(message: Message, state: FSMContext):
    """Edit offer name"""
    # Get offer ID from state
    data = await state.get_data()
    offer_id = data["offer_id"]
    
    # Update name
    updated = await service_commands.update_offer_name(offer_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Название специального предложения успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить название специального предложения.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def delete_offer_confirm(callback: CallbackQuery):
    """Confirm offer deletion"""
    # Extract offer ID from callback data
    offer_id = callback.data.replace("delete_offer_confirm_", "")
    
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить это специальное предложение?",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(offer_id, "offer")
    )
    await callback.answer()

async def delete_offer(callback: CallbackQuery):
    """Delete offer"""
    # Extract offer ID from callback data
    offer_id = callback.data.replace("confirm_delete_offer_", "")
    
    # Delete offer
    deleted = await service_commands.delete_offer(offer_id)
    
    if deleted:
        await callback.message.edit_text(
            "✅ Специальное предложение успешно удалено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить специальное предложение.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Appointment management
async def admin_appointments(callback: CallbackQuery):
    """Admin appointments handler"""
    await callback.message.edit_text(
        "📅 Управление записями\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_admin_appointments_keyboard()
    )
    await callback.answer()

async def admin_appointments_today(callback: CallbackQuery):
    """Show today's appointments"""
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get appointments for today
    appointments = await appointment_commands.get_appointments_by_date(today)
    
    if appointments:
        await callback.message.edit_text(
            f"📅 Записи на сегодня ({today})\n\nВыберите запись для управления:",
            reply_markup=admin_keyboards.get_date_appointments_admin_keyboard(appointments, today)
        )
    else:
        await callback.message.edit_text(
            f"На сегодня ({today}) записей нет.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_appointments_all(callback: CallbackQuery):
    """Show all appointments"""
    # Get all appointments
    appointments = await appointment_commands.get_all_appointments()
    
    # Group appointments by date
    appointments_by_date = {}
    for appointment in appointments:
        date = appointment["date"]
        if date not in appointments_by_date:
            appointments_by_date[date] = []
        appointments_by_date[date].append(appointment)
    
    # Create message
    message = "📅 Все записи\n\n"
    for date in sorted(appointments_by_date.keys()):
        message += f"📌 {date}:\n"
        for appointment in appointments_by_date[date]:
            client = await user_commands.get_user(appointment["client_id"])
            client_name = client["name"] if client else "Unknown"
            service = await service_commands.get_service(appointment["service_id"])
            service_name = service["name"] if service else "Unknown"
            
            status_emoji = "⏳" if appointment["status"] == "pending" else "✅" if appointment["status"] == "confirmed" else "❌" if appointment["status"] == "cancelled" else "🏁" if appointment["status"] == "completed" else "💰"
            
            message += f"{status_emoji} {appointment['time']} - {client_name} - {service_name}\n"
        message += "\n"
    
    # Check if message is too long
    if len(message) > 4096:
        message = "📅 Слишком много записей для отображения. Пожалуйста, используйте фильтры."
    
    await callback.message.edit_text(
        message,
        reply_markup=admin_keyboards.get_back_to_admin_keyboard()
    )
    
    await callback.answer()

async def admin_appointments_date(callback: CallbackQuery):
    """Show appointments by date"""
    # Create calendar keyboard
    now = datetime.now()
    month = now.month
    year = now.year
    
    # Create calendar
    calendar_keyboard = await create_calendar(year, month)
    
    await callback.message.edit_text(
        "📅 Выберите дату для просмотра записей:",
        reply_markup=calendar_keyboard
    )
    
    await callback.answer()

async def create_calendar(year, month):
    """Create calendar keyboard"""
    builder = InlineKeyboardBuilder()
    
    # Add month and year header
    month_name = calendar.month_name[month]
    builder.button(text=f"{month_name} {year}", callback_data=f"ignore")
    
    # Add day headers
    for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
        builder.button(text=day, callback_data=f"ignore")
    
    # Get calendar
    cal = calendar.monthcalendar(year, month)
    
    # Add days
    for week in cal:
        for day in week:
            if day == 0:
                builder.button(text=" ", callback_data=f"ignore")
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                builder.button(text=str(day), callback_data=f"admin_appointments_date_{date_str}")
    
    # Add navigation buttons
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1
    
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1
    
    builder.button(text="⬅️ Пред", callback_data=f"calendar_{prev_year}_{prev_month}")
    builder.button(text="След ➡️", callback_data=f"calendar_{next_year}_{next_month}")
    
    # Add back button
    builder.button(text="◀️ Назад", callback_data="admin_appointments")
    
    # Adjust width
    builder.adjust(7, 7, 7, 7, 7, 2, 1)
    
    return builder.as_markup()

async def admin_appointments_date_selected(callback: CallbackQuery):
    """Handle date selection for appointments"""
    # Extract date from callback data
    date = callback.data.replace("admin_appointments_date_", "")
    
    # Get appointments for date
    appointments = await appointment_commands.get_appointments_by_date(date)
    
    if appointments:
        await callback.message.edit_text(
            f"📅 Записи на {date}\n\nВыберите запись для управления:",
            reply_markup=admin_keyboards.get_date_appointments_admin_keyboard(appointments, date)
        )
    else:
        await callback.message.edit_text(
            f"На {date} записей нет.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_view_appointment(callback: CallbackQuery):
    """View appointment details"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("admin_view_appointment_", "")
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if appointment:
        # Get client details
        client = await user_commands.get_user(appointment["client_id"])
        client_name = client["name"] if client else "Unknown"
        client_phone = client.get("phone", "Не указан")
        
        # Get service details
        service = await service_commands.get_service(appointment["service_id"])
        service_name = service["name"] if service else "Unknown"
        service_price = service["price"] if service else "Unknown"
        
        # Get master details
        master = await master_commands.get_master(appointment["master_id"])
        master_name = master["name"] if master else "Unknown"
        
        # Status emoji
        status_emoji = "⏳" if appointment["status"] == "pending" else "✅" if appointment["status"] == "confirmed" else "❌" if appointment["status"] == "cancelled" else "🏁" if appointment["status"] == "completed" else "💰"
        payment_status = "Оплачено" if appointment.get("paid", False) else "Не оплачено"
        payment_method = appointment.get("payment_method", "Не указан")
        
        await callback.message.edit_text(
            f"🔍 Детали записи\n\n"
            f"Дата: {appointment['date']}\n"
            f"Время: {appointment['time']}\n"
            f"Статус: {status_emoji} {appointment['status'].capitalize()}\n"
            f"Оплата: {payment_status} ({payment_method})\n\n"
            f"Клиент: {client_name}\n"
            f"Телефон: {client_phone}\n\n"
            f"Услуга: {service_name}\n"
            f"Цена: {service_price} руб.\n\n"
            f"Мастер: {master_name}",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, appointment["status"])
        )
    else:
        await callback.message.edit_text(
            "❌ Запись не найдена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_confirm_appointment(callback: CallbackQuery):
    """Confirm appointment by admin"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("admin_confirm_appointment_", "")
    
    # Confirm appointment
    confirmed = await appointment_commands.confirm_appointment(appointment_id)
    
    if confirmed:
        # Get appointment details
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        # Get client details
        client = await user_commands.get_user(appointment["client_id"])
        
        # Notify client if possible
        if client and "user_id" in client:
            try:
                # Get service details
                service = await service_commands.get_service(appointment["service_id"])
                service_name = service["name"] if service else "Unknown"
                
                # Get master details
                master = await master_commands.get_master(appointment["master_id"])
                master_name = master["name"] if master else "Unknown"
                
                # Send notification
                from aiogram import Bot
                from main import bot
                
                await bot.send_message(
                    client["user_id"],
                    f"✅ Ваша запись подтверждена!\n\n"
                    f"Дата: {appointment['date']}\n"
                    f"Время: {appointment['time']}\n"
                    f"Услуга: {service_name}\n"
                    f"Мастер: {master_name}"
                )
            except:
                pass
        
        await callback.message.edit_text(
            "✅ Запись успешно подтверждена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось подтвердить запись.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def admin_cancel_appointment(callback: CallbackQuery):
    """Cancel appointment by admin"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("admin_cancel_appointment_", "")
    
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите отменить эту запись?",
        reply_markup=admin_keyboards.get_cancel_appointment_keyboard(appointment_id)
    )
    
    await callback.answer()

async def confirm_cancel_appointment(callback: CallbackQuery):
    """Confirm cancellation of appointment"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("confirm_cancel_appointment_", "")
    
    # Cancel appointment
    cancelled = await appointment_commands.cancel_appointment(appointment_id)
    
    if cancelled:
        # Get appointment details
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        # Get client details
        client = await user_commands.get_user(appointment["client_id"])
        
        # Notify client if possible
        if client and "user_id" in client:
            try:
                # Get service details
                service = await service_commands.get_service(appointment["service_id"])
                service_name = service["name"] if service else "Unknown"
                
                # Send notification
                from aiogram import Bot
                from main import bot
                
                await bot.send_message(
                    client["user_id"],
                    f"❌ Ваша запись отменена.\n\n"
                    f"Дата: {appointment['date']}\n"
                    f"Время: {appointment['time']}\n"
                    f"Услуга: {service_name}\n\n"
                    f"Вы можете записаться на другое время."
                )
            except:
                pass
        
        await callback.message.edit_text(
            "✅ Запись успешно отменена.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отменить запись.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def mark_completed(callback: CallbackQuery):
    """Mark appointment as completed"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("mark_completed_", "")
    
    # Mark as completed
    completed = await appointment_commands.complete_appointment(appointment_id)
    
    if completed:
        await callback.message.edit_text(
            "✅ Запись отмечена как выполненная.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отметить запись как выполненную.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def mark_paid(callback: CallbackQuery):
    """Mark appointment as paid"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.replace("mark_paid_", "")
    
    # Mark as paid
    paid = await appointment_commands.mark_appointment_paid(appointment_id)
    
    if paid:
        await callback.message.edit_text(
            "✅ Запись отмечена как оплаченная.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отметить запись как оплаченную.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def set_payment_method(callback: CallbackQuery):
    """Set payment method for appointment"""
    # Extract payment method and appointment ID from callback data
    data = callback.data.replace("set_payment_", "")
    method, appointment_id = data.split("_")
    
    # Set payment method
    updated = await appointment_commands.set_payment_method(appointment_id, method)
    
    if updated:
        method_name = "Наличные" if method == "cash" else "Карта/Терминал" if method == "card" else "Перевод" if method == "transfer" else method
        
        await callback.message.edit_text(
            f"✅ Способ оплаты установлен: {method_name}.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось установить способ оплаты.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Master management
async def admin_masters(callback: CallbackQuery):
    """Admin masters handler"""
    await callback.message.edit_text(
        "👤 Управление мастерами\n\nВыберите действие:",
        reply_markup=admin_keyboards.get_masters_management_keyboard()
    )
    await callback.answer()

# Add master
async def add_master_start(callback: CallbackQuery, state: FSMContext):
    """Start adding master"""
    await callback.message.edit_text(
        "➕ Добавление мастера\n\nВведите имя мастера:"
    )
    
    # Set state
    await state.set_state(AdminMasterStates.adding_name)
    await callback.answer()

async def add_master_name(message: Message, state: FSMContext):
    """Handle adding master name"""
    # Save name
    await state.update_data(name=message.text)
    
    # Ask for telegram
    await message.answer("Введите Telegram мастера (или '-' если нет):")
    
    # Set state
    await state.set_state(AdminMasterStates.adding_telegram)

async def add_master_telegram(message: Message, state: FSMContext):
    """Handle adding master telegram"""
    # Save telegram
    telegram = message.text if message.text != "-" else None
    await state.update_data(telegram=telegram)
    
    # Ask for address
    await message.answer("Введите адрес мастера:")
    
    # Set state
    await state.set_state(AdminMasterStates.adding_address)

async def add_master_address(message: Message, state: FSMContext):
    """Handle adding master address"""
    # Save address
    await state.update_data(address=message.text)
    
    # Ask for location
    await message.answer("Отправьте местоположение мастера (или напишите 'пропустить'):")
    
    # Set state
    await state.set_state(AdminMasterStates.adding_location)

async def add_master_location(message: Message, state: FSMContext):
    """Handle adding master location"""
    # Get all data
    data = await state.get_data()
    name = data["name"]
    telegram = data.get("telegram")
    address = data["address"]
    
    # Check if location is sent
    latitude = None
    longitude = None
    
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.text.lower() != "пропустить":
        await message.answer("Неверный формат местоположения. Отправьте местоположение или напишите 'пропустить':")
        return
    
    # Add master
    master = await master_commands.add_master(name, telegram, address, latitude, longitude)
    
    if master:
        await message.answer(
            f"✅ Мастер добавлен успешно!\n\nИмя: {name}\nTelegram: {telegram or 'Не указан'}\nАдрес: {address}",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось добавить мастера. Пожалуйста, попробуйте позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

# View masters
async def view_masters_admin(callback: CallbackQuery):
    """View masters handler"""
    # Get masters
    masters = await master_commands.get_masters()
    
    if masters:
        # Create message
        message = "👤 Мастера\n\n"
        
        # Create keyboard
        builder = InlineKeyboardBuilder()
        
        for master in masters:
            master_name = master["name"]
            master_id = master["id"]
            
            # Add to message
            message += f"• {master_name}\n"
            
            # Add button to keyboard
            builder.button(text=master_name, callback_data=f"admin_view_master_{master_id}")
        
        # Add back button
        builder.button(text="◀️ Назад", callback_data="admin_masters")
        
        # Adjust keyboard
        builder.adjust(1)
        
        await callback.message.edit_text(message, reply_markup=builder.as_markup())
    else:
        await callback.message.edit_text(
            "Пока нет добавленных мастеров.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# View master details
async def admin_view_master(callback: CallbackQuery):
    """View master details"""
    # Extract master ID from callback data
    master_id = callback.data.replace("admin_view_master_", "")
    
    # Get master details
    master = await master_commands.get_master(master_id)
    
    if master:
        # Create message
        message = f"🔍 Детали мастера\n\nИмя: {master['name']}\n"
        
        # Add telegram if exists
        if master.get("telegram"):
            message += f"Telegram: {master['telegram']}\n"
        
        # Add address
        message += f"Адрес: {master['address']}\n"
        
        # Check if has location
        if master.get("latitude") and master.get("longitude"):
            message += f"Местоположение: Да"
        else:
            message += f"Местоположение: Нет"
        
        await callback.message.edit_text(
            message,
            reply_markup=admin_keyboards.get_master_actions_keyboard(master_id)
        )
    else:
        await callback.message.edit_text(
            "❌ Мастер не найден.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Edit master
async def edit_master(callback: CallbackQuery):
    """Edit master handler"""
    # Extract master ID from callback data
    master_id = callback.data.replace("edit_master_", "")
    
    await callback.message.edit_text(
        "✏️ Редактирование мастера\n\nВыберите, что хотите изменить:",
        reply_markup=admin_keyboards.get_edit_master_keyboard(master_id)
    )
    await callback.answer()

async def edit_master_name_start(callback: CallbackQuery, state: FSMContext):
    """Start editing master name"""
    # Extract master ID from callback data
    master_id = callback.data.replace("edit_master_name_", "")
    
    # Save master ID to state
    await state.update_data(master_id=master_id)
    
    # Ask for new name
    await callback.message.edit_text("Введите новое имя мастера:")
    
    # Set state
    await state.set_state(AdminMasterStates.editing_name)
    await callback.answer()

async def edit_master_name(message: Message, state: FSMContext):
    """Edit master name"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update name
    updated = await master_commands.update_master_name(master_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Имя мастера успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить имя мастера.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_telegram_start(callback: CallbackQuery, state: FSMContext):
    """Start editing master telegram"""
    # Extract master ID from callback data
    master_id = callback.data.replace("edit_master_telegram_", "")
    
    # Save master ID to state
    await state.update_data(master_id=master_id)
    
    # Ask for new telegram
    await callback.message.edit_text("Введите новый Telegram мастера (или '-' если нет):")
    
    # Set state
    await state.set_state(AdminMasterStates.editing_telegram)
    await callback.answer()

async def edit_master_telegram(message: Message, state: FSMContext):
    """Edit master telegram"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update telegram
    telegram = message.text if message.text != "-" else None
    updated = await master_commands.update_master_telegram(master_id, telegram)
    
    if updated:
        await message.answer(
            "✅ Telegram мастера успешно изменен.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить Telegram мастера.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_address_start(callback: CallbackQuery, state: FSMContext):
    """Start editing master address"""
    # Extract master ID from callback data
    master_id = callback.data.replace("edit_master_address_", "")
    
    # Save master ID to state
    await state.update_data(master_id=master_id)
    
    # Ask for new address
    await callback.message.edit_text("Введите новый адрес мастера:")
    
    # Set state
    await state.set_state(AdminMasterStates.editing_address)
    await callback.answer()

async def edit_master_address(message: Message, state: FSMContext):
    """Edit master address"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Update address
    updated = await master_commands.update_master_address(master_id, message.text)
    
    if updated:
        await message.answer(
            "✅ Адрес мастера успешно изменен.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить адрес мастера.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

async def edit_master_location_start(callback: CallbackQuery, state: FSMContext):
    """Start editing master location"""
    # Extract master ID from callback data
    master_id = callback.data.replace("edit_master_location_", "")
    
    # Save master ID to state
    await state.update_data(master_id=master_id)
    
    # Ask for new location
    await callback.message.edit_text("Отправьте новое местоположение мастера (или напишите 'пропустить'):")
    
    # Set state
    await state.set_state(AdminMasterStates.editing_location)
    await callback.answer()

async def edit_master_location(message: Message, state: FSMContext):
    """Edit master location"""
    # Get master ID from state
    data = await state.get_data()
    master_id = data["master_id"]
    
    # Check if location is sent
    latitude = None
    longitude = None
    
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude
    elif message.text.lower() != "пропустить":
        await message.answer("Неверный формат местоположения. Отправьте местоположение или напишите 'пропустить':")
        return
    
    # Update location
    updated = await master_commands.update_master_location(master_id, latitude, longitude)
    
    if updated:
        await message.answer(
            "✅ Местоположение мастера успешно изменено.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await message.answer(
            "❌ Не удалось изменить местоположение мастера.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    # Clear state
    await state.clear()

# Delete master
async def delete_master_confirm(callback: CallbackQuery):
    """Confirm master deletion"""
    # Extract master ID from callback data
    master_id = callback.data.replace("delete_master_confirm_", "")
    
    await callback.message.edit_text(
        "❓ Вы уверены, что хотите удалить этого мастера?",
        reply_markup=admin_keyboards.get_confirm_delete_keyboard(master_id, "master")
    )
    await callback.answer()

async def delete_master(callback: CallbackQuery):
    """Delete master"""
    # Extract master ID from callback data
    master_id = callback.data.replace("confirm_delete_master_", "")
    
    # Delete master
    deleted = await master_commands.delete_master(master_id)
    
    if deleted:
        await callback.message.edit_text(
            "✅ Мастер успешно удален.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось удалить мастера.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Calendar navigation
async def calendar_navigation(callback: CallbackQuery):
    """Handle calendar navigation"""
    # Extract year and month from callback data
    year, month = map(int, callback.data.replace("calendar_", "").split("_"))
    
    # Create calendar
    calendar_keyboard = await create_calendar(year, month)
    
    await callback.message.edit_text(
        "📅 Выберите дату для просмотра записей:",
        reply_markup=calendar_keyboard
    )
    
    await callback.answer()

# Register handlers
def register_handlers(dp: Router):
    # Admin panel
    dp.message.register(admin_start, Command("admin"))
    dp.callback_query.register(back_to_admin, F.data == "back_to_admin")
    dp.callback_query.register(admin_services, F.data == "admin_services")
    dp.callback_query.register(admin_masters, F.data == "admin_masters")
    dp.callback_query.register(admin_appointments, F.data == "admin_appointments")
    dp.callback_query.register(admin_offers, F.data == "admin_offers")
    dp.callback_query.register(admin_categories, F.data == "admin_categories")
    
    # Template categories
    dp.callback_query.register(template_categories, F.data == "template_categories")
    dp.callback_query.register(template_category_selected, F.data.startswith("template_category_"))
    dp.callback_query.register(update_category_price_start, F.data.startswith("update_category_price_"))
    dp.message.register(update_category_price, AdminServiceStates.setting_category_price)
    
    # Services management
    dp.callback_query.register(add_service_start, F.data == "add_service")
    dp.message.register(add_service_name, AdminServiceStates.adding_name)
    dp.message.register(add_service_description, AdminServiceStates.adding_description)
    dp.message.register(add_service_price, AdminServiceStates.adding_price)
    dp.message.register(add_service_duration, AdminServiceStates.adding_duration)
    dp.callback_query.register(add_service_category, F.data.startswith("add_service_category_"))
    
    dp.callback_query.register(view_services, F.data == "view_services")
    dp.callback_query.register(view_category_services, F.data.startswith("view_category_services_"))
    dp.callback_query.register(admin_view_service, F.data.startswith("admin_view_service_"))
    dp.callback_query.register(edit_service, F.data.startswith("edit_service_"))
    dp.callback_query.register(edit_service_name_start, F.data.startswith("edit_service_name_"))
    dp.message.register(edit_service_name, AdminServiceStates.editing_name)
    dp.callback_query.register(edit_service_description_start, F.data.startswith("edit_service_description_"))
    dp.message.register(edit_service_description, AdminServiceStates.editing_description)
    dp.callback_query.register(edit_service_price_start, F.data.startswith("edit_service_price_"))
    dp.message.register(edit_service_price, AdminServiceStates.editing_price)
    dp.callback_query.register(edit_service_duration_start, F.data.startswith("edit_service_duration_"))
    dp.message.register(edit_service_duration, AdminServiceStates.editing_duration)
    dp.callback_query.register(delete_service_confirm, F.data.startswith("delete_service_confirm_"))
    dp.callback_query.register(delete_service, F.data.startswith("confirm_delete_service_"))
    
    # Category management
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
    dp.callback_query.register(delete_offer_confirm, F.data.startswith("delete_offer_confirm_"))
    dp.callback_query.register(delete_offer, F.data.startswith("confirm_delete_offer_"))
    
    # Appointment management
    dp.callback_query.register(admin_appointments_today, F.data == "admin_appointments_today")
    dp.callback_query.register(admin_appointments_all, F.data == "admin_appointments_all")
    dp.callback_query.register(admin_appointments_date, F.data == "admin_appointments_date")
    dp.callback_query.register(admin_appointments_date_selected, F.data.startswith("admin_appointments_date_"))
    dp.callback_query.register(admin_view_appointment, F.data.startswith("admin_view_appointment_"))
    dp.callback_query.register(admin_confirm_appointment, F.data.startswith("admin_confirm_appointment_"))
    dp.callback_query.register(admin_cancel_appointment, F.data.startswith("admin_cancel_appointment_"))
    dp.callback_query.register(confirm_cancel_appointment, F.data.startswith("confirm_cancel_appointment_"))
    dp.callback_query.register(mark_completed, F.data.startswith("mark_completed_"))
    dp.callback_query.register(mark_paid, F.data.startswith("mark_paid_"))
    dp.callback_query.register(set_payment_method, F.data.startswith("set_payment_"))
    dp.callback_query.register(calendar_navigation, F.data.startswith("calendar_"))
    
    # Master management
    dp.callback_query.register(add_master_start, F.data == "add_master")
    dp.message.register(add_master_name, AdminMasterStates.adding_name)
    dp.message.register(add_master_telegram, AdminMasterStates.adding_telegram)
    dp.message.register(add_master_address, AdminMasterStates.adding_address)
    dp.message.register(add_master_location, AdminMasterStates.adding_location)
    dp.callback_query.register(view_masters_admin, F.data == "view_masters_admin")
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
    dp.callback_query.register(delete_master_confirm, F.data.startswith("delete_master_confirm_"))
    dp.callback_query.register(delete_master, F.data.startswith("confirm_delete_master_"))
