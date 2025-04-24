
from aiogram import Router, F, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import json
import os
import logging

from keyboards.admin_keyboards import get_admin_keyboard, get_back_to_admin_keyboard, get_services_management_keyboard
from keyboards.admin_keyboards import get_appointments_management_keyboard, get_masters_management_keyboard, get_categories_management_keyboard, get_offers_management_keyboard
from keyboards.admin_keyboards import get_template_categories_keyboard, get_service_categories_keyboard, get_category_services_keyboard
from keyboards.admin_keyboards import get_all_categories_keyboard, get_category_actions_keyboard, get_edit_category_keyboard
from keyboards.admin_keyboards import get_all_offers_keyboard, get_offer_actions_keyboard, get_edit_offer_keyboard
from keyboards.admin_keyboards import get_service_actions_keyboard, get_edit_service_keyboard, get_category_services_price_keyboard
from keyboards.admin_keyboards import get_master_actions_keyboard, get_edit_master_keyboard
from keyboards.admin_keyboards import get_confirm_delete_keyboard, get_admin_appointments_keyboard, get_appointment_actions_keyboard
from keyboards.admin_keyboards import get_date_appointments_admin_keyboard, get_cancel_appointment_keyboard

from utils.db_api import service_commands, user_commands, master_commands, appointment_commands

# Define FSM states
class AdminServiceStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    selecting_category = State()
    
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()
    editing_category = State()

class AdminCategoryStates(StatesGroup):
    adding_name = State()
    editing_name = State()

class AdminMasterStates(StatesGroup):
    adding_name = State()
    adding_telegram = State()
    adding_address = State()
    adding_location = State()
    
    editing_name = State()
    editing_telegram = State()
    editing_address = State()
    editing_location = State()

class AdminOfferStates(StatesGroup):
    adding_name = State()
    adding_description = State()
    adding_price = State()
    adding_duration = State()
    
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()

class AdminAppointmentStates(StatesGroup):
    selecting_date = State()

# Function to register admin handlers
def register_handlers(dp: Dispatcher):
    """Register admin handlers"""
    
    @dp.message(Command("admin"))
    async def admin_command(message: Message):
        """Handle /admin command"""
        # Check if user is admin
        user_id = message.from_user.id
        user = await user_commands.get_user(user_id)
        if not user or user.get('role') != 'admin':
            await message.answer("У вас нет доступа к админ-панели.")
            return
        
        await message.answer("Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())
    
    @dp.callback_query(F.data == "back_to_admin")
    async def back_to_admin(callback: CallbackQuery):
        """Return to admin panel"""
        await callback.message.edit_text("Добро пожаловать в админ-панель!", reply_markup=get_admin_keyboard())
        await callback.answer()

    # Service management handlers
    @dp.callback_query(F.data == "admin_services")
    async def admin_services(callback: CallbackQuery):
        """Show services management menu"""
        await callback.message.edit_text(
            "Управление услугами:",
            reply_markup=get_services_management_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "template_categories")
    async def template_categories(callback: CallbackQuery):
        """Show template service categories"""
        categories = await service_commands.get_all_template_categories()
        
        if not categories:
            await callback.message.edit_text(
                "В базе нет шаблонных категорий услуг. Попробуйте инициализировать данные.",
                reply_markup=get_back_to_admin_keyboard()
            )
            return
        
        await callback.message.edit_text(
            "Выберите категорию для быстрого создания услуг:",
            reply_markup=get_template_categories_keyboard(categories)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("template_category_"))
    async def template_category_selected(callback: CallbackQuery):
        """Handle template category selection"""
        # Extract category name
        category = callback.data.replace("template_category_", "")
        
        # Create services from templates
        result = await service_commands.create_services_from_template(category)
        success, message = result
        
        # Set correct category ID for created services
        if success:
            # Get category by name
            category_obj = await service_commands.get_category_by_name(category)
            if category_obj:
                category_id = category_obj.get('id')
                await callback.message.edit_text(
                    f"{message}\n\nВы можете настроить цены для этих услуг:",
                    reply_markup=get_category_services_price_keyboard(category_id)
                )
            else:
                await callback.message.edit_text(
                    f"{message}\n\nВернуться в управление услугами:",
                    reply_markup=get_services_management_keyboard()
                )
        else:
            await callback.message.edit_text(
                f"Ошибка: {message}",
                reply_markup=get_services_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data == "add_service")
    async def add_service_start(callback: CallbackQuery, state: FSMContext):
        """Start adding a new service"""
        await callback.message.edit_text("Введите название услуги:")
        await state.set_state(AdminServiceStates.adding_name)
        await callback.answer()
    
    @dp.message(AdminServiceStates.adding_name)
    async def add_service_name(message: Message, state: FSMContext):
        """Handle service name input"""
        # Save name to FSM context
        await state.update_data(name=message.text)
        
        await message.answer("Введите описание услуги:")
        await state.set_state(AdminServiceStates.adding_description)
    
    @dp.message(AdminServiceStates.adding_description)
    async def add_service_description(message: Message, state: FSMContext):
        """Handle service description input"""
        # Save description to FSM context
        await state.update_data(description=message.text)
        
        await message.answer("Введите цену услуги (только цифры):")
        await state.set_state(AdminServiceStates.adding_price)
    
    @dp.message(AdminServiceStates.adding_price)
    async def add_service_price(message: Message, state: FSMContext):
        """Handle service price input"""
        try:
            price = float(message.text)
            await state.update_data(price=price)
            
            await message.answer("Введите продолжительность услуги в минутах (только цифры):")
            await state.set_state(AdminServiceStates.adding_duration)
        except ValueError:
            await message.answer("Пожалуйста, введите корректную цену (только цифры).")
    
    @dp.message(AdminServiceStates.adding_duration)
    async def add_service_duration(message: Message, state: FSMContext):
        """Handle service duration input"""
        try:
            duration = int(message.text)
            await state.update_data(duration=duration)
            
            # Get all categories for selection
            categories = await service_commands.get_all_categories()
            
            if categories:
                category_text = "\n".join([f"{cat['id']}. {cat['name']}" for cat in categories])
                await message.answer(
                    f"Выберите категорию услуги (введите ID категории):\n\n{category_text}\n\nЕсли хотите пропустить, введите 0."
                )
                await state.set_state(AdminServiceStates.selecting_category)
            else:
                # No categories, skip to creation
                await add_service_complete(message, state)
        except ValueError:
            await message.answer("Пожалуйста, введите корректную продолжительность в минутах (только цифры).")
    
    @dp.message(AdminServiceStates.selecting_category)
    async def add_service_select_category(message: Message, state: FSMContext):
        """Handle service category selection"""
        try:
            category_id = message.text.strip()
            
            if category_id == "0":
                # Skip category selection
                await add_service_complete(message, state)
                return
            
            # Verify category exists
            category = await service_commands.get_category(category_id)
            if category:
                await state.update_data(category_id=category_id)
                await add_service_complete(message, state)
            else:
                await message.answer("Такой категории не существует. Попробуйте еще раз или введите 0, чтобы пропустить.")
        except ValueError:
            await message.answer("Пожалуйста, введите корректный ID категории или 0, чтобы пропустить.")
    
    async def add_service_complete(message: Message, state: FSMContext):
        """Complete service addition process"""
        # Get all the data from FSM context
        data = await state.get_data()
        
        # Create the service
        service = await service_commands.add_service(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            duration=data.get('duration'),
            category_id=data.get('category_id')
        )
        
        if service:
            await message.answer(
                f"Услуга '{service['name']}' успешно добавлена!",
                reply_markup=get_services_management_keyboard()
            )
        else:
            await message.answer(
                "Ошибка при добавлении услуги.",
                reply_markup=get_services_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data == "view_services")
    async def view_services(callback: CallbackQuery):
        """Show all services by category"""
        services_by_category = await service_commands.get_services_by_category()
        
        if not services_by_category:
            await callback.message.edit_text(
                "В базе нет услуг. Добавьте несколько услуг.",
                reply_markup=get_services_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            "Выберите категорию услуг:",
            reply_markup=get_service_categories_keyboard(services_by_category)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("view_category_services_"))
    async def view_category_services(callback: CallbackQuery):
        """Show services in a specific category"""
        category_name = callback.data.replace("view_category_services_", "")
        services = await service_commands.get_services_by_category_name(category_name)
        
        if not services:
            await callback.message.edit_text(
                f"В категории '{category_name}' нет услуг.",
                reply_markup=get_service_categories_keyboard(await service_commands.get_services_by_category())
            )
            return
        
        # Create a paginated keyboard for services
        await callback.message.edit_text(
            f"Услуги в категории '{category_name}':",
            reply_markup=get_category_services_keyboard(services, category_name)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_view_service_"))
    async def admin_view_service(callback: CallbackQuery):
        """Show service details"""
        service_id = callback.data.replace("admin_view_service_", "")
        service = await service_commands.get_service(service_id)
        
        if not service:
            await callback.message.edit_text(
                "Услуга не найдена.",
                reply_markup=get_services_management_keyboard()
            )
            return
        
        # Get category name if exists
        category_name = "Без категории"
        if service.get('category_id'):
            category = await service_commands.get_category(service.get('category_id'))
            if category:
                category_name = category.get('name')
        
        service_text = (
            f"📋 Информация об услуге\n\n"
            f"📌 Название: {service.get('name')}\n"
            f"📝 Описание: {service.get('description')}\n"
            f"💰 Цена: {service.get('price')} руб.\n"
            f"⏱ Продолжительность: {service.get('duration')} мин.\n"
            f"📁 Категория: {category_name}\n"
        )
        
        await callback.message.edit_text(
            service_text,
            reply_markup=get_service_actions_keyboard(service_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_service_"))
    async def edit_service(callback: CallbackQuery):
        """Show service edit options"""
        service_id = callback.data.replace("edit_service_", "")
        service = await service_commands.get_service(service_id)
        
        if not service:
            await callback.message.edit_text(
                "Услуга не найдена.",
                reply_markup=get_services_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Выберите, что вы хотите изменить для услуги '{service.get('name')}':",
            reply_markup=get_edit_service_keyboard(service_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_service_name_"))
    async def edit_service_name_start(callback: CallbackQuery, state: FSMContext):
        """Start editing service name"""
        service_id = callback.data.replace("edit_service_name_", "")
        await state.update_data(service_id=service_id)
        
        await callback.message.edit_text("Введите новое название услуги:")
        await state.set_state(AdminServiceStates.editing_name)
        await callback.answer()
    
    @dp.message(AdminServiceStates.editing_name)
    async def edit_service_name(message: Message, state: FSMContext):
        """Handle service name edit"""
        data = await state.get_data()
        service_id = data.get('service_id')
        
        # Update service name
        success = await service_commands.update_service(service_id, name=message.text)
        
        if success:
            service = await service_commands.get_service(service_id)
            await message.answer(
                f"Название услуги успешно изменено на '{message.text}'.",
                reply_markup=get_service_actions_keyboard(service_id)
            )
        else:
            await message.answer(
                "Ошибка при изменении названия услуги.",
                reply_markup=get_services_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("edit_service_description_"))
    async def edit_service_description_start(callback: CallbackQuery, state: FSMContext):
        """Start editing service description"""
        service_id = callback.data.replace("edit_service_description_", "")
        await state.update_data(service_id=service_id)
        
        await callback.message.edit_text("Введите новое описание услуги:")
        await state.set_state(AdminServiceStates.editing_description)
        await callback.answer()
    
    @dp.message(AdminServiceStates.editing_description)
    async def edit_service_description(message: Message, state: FSMContext):
        """Handle service description edit"""
        data = await state.get_data()
        service_id = data.get('service_id')
        
        # Update service description
        success = await service_commands.update_service(service_id, description=message.text)
        
        if success:
            await message.answer(
                "Описание услуги успешно изменено.",
                reply_markup=get_service_actions_keyboard(service_id)
            )
        else:
            await message.answer(
                "Ошибка при изменении описания услуги.",
                reply_markup=get_services_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("edit_service_price_"))
    async def edit_service_price_start(callback: CallbackQuery, state: FSMContext):
        """Start editing service price"""
        service_id = callback.data.replace("edit_service_price_", "")
        await state.update_data(service_id=service_id)
        
        await callback.message.edit_text("Введите новую цену услуги (только цифры):")
        await state.set_state(AdminServiceStates.editing_price)
        await callback.answer()
    
    @dp.message(AdminServiceStates.editing_price)
    async def edit_service_price(message: Message, state: FSMContext):
        """Handle service price edit"""
        data = await state.get_data()
        service_id = data.get('service_id')
        
        try:
            price = float(message.text)
            
            # Update service price
            success = await service_commands.update_service(service_id, price=price)
            
            if success:
                await message.answer(
                    f"Цена услуги успешно изменена на {price} руб.",
                    reply_markup=get_service_actions_keyboard(service_id)
                )
            else:
                await message.answer(
                    "Ошибка при изменении цены услуги.",
                    reply_markup=get_services_management_keyboard()
                )
        except ValueError:
            await message.answer(
                "Пожалуйста, введите корректную цену (только цифры)."
            )
            return
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("edit_service_duration_"))
    async def edit_service_duration_start(callback: CallbackQuery, state: FSMContext):
        """Start editing service duration"""
        service_id = callback.data.replace("edit_service_duration_", "")
        await state.update_data(service_id=service_id)
        
        await callback.message.edit_text("Введите новую продолжительность услуги в минутах (только цифры):")
        await state.set_state(AdminServiceStates.editing_duration)
        await callback.answer()
    
    @dp.message(AdminServiceStates.editing_duration)
    async def edit_service_duration(message: Message, state: FSMContext):
        """Handle service duration edit"""
        data = await state.get_data()
        service_id = data.get('service_id')
        
        try:
            duration = int(message.text)
            
            # Update service duration
            success = await service_commands.update_service(service_id, duration=duration)
            
            if success:
                await message.answer(
                    f"Продолжительность услуги успешно изменена на {duration} мин.",
                    reply_markup=get_service_actions_keyboard(service_id)
                )
            else:
                await message.answer(
                    "Ошибка при изменении продолжительности услуги.",
                    reply_markup=get_services_management_keyboard()
                )
        except ValueError:
            await message.answer(
                "Пожалуйста, введите корректную продолжительность (только цифры)."
            )
            return
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("edit_service_category_"))
    async def edit_service_category_start(callback: CallbackQuery, state: FSMContext):
        """Start editing service category"""
        service_id = callback.data.replace("edit_service_category_", "")
        await state.update_data(service_id=service_id)
        
        # Get all categories
        categories = await service_commands.get_all_categories()
        
        if not categories:
            await callback.message.edit_text(
                "Нет доступных категорий. Сначала создайте категории.",
                reply_markup=get_service_actions_keyboard(service_id)
            )
            return
        
        category_text = "\n".join([f"{cat['id']}. {cat['name']}" for cat in categories])
        
        await callback.message.edit_text(
            f"Выберите категорию для услуги (введите ID категории):\n\n{category_text}\n\nЕсли хотите удалить категорию, введите 0."
        )
        await state.set_state(AdminServiceStates.editing_category)
        await callback.answer()
    
    @dp.message(AdminServiceStates.editing_category)
    async def edit_service_category(message: Message, state: FSMContext):
        """Handle service category edit"""
        data = await state.get_data()
        service_id = data.get('service_id')
        
        try:
            category_input = message.text.strip()
            
            if category_input == "0":
                # Remove category from service
                success = await service_commands.update_service(service_id, category_id=None)
                
                if success:
                    await message.answer(
                        "Категория услуги успешно удалена.",
                        reply_markup=get_service_actions_keyboard(service_id)
                    )
                else:
                    await message.answer(
                        "Ошибка при удалении категории услуги.",
                        reply_markup=get_service_actions_keyboard(service_id)
                    )
            else:
                # Verify category exists
                category = await service_commands.get_category(category_input)
                
                if category:
                    success = await service_commands.update_service(service_id, category_id=category_input)
                    
                    if success:
                        await message.answer(
                            f"Категория услуги успешно изменена на '{category['name']}'.",
                            reply_markup=get_service_actions_keyboard(service_id)
                        )
                    else:
                        await message.answer(
                            "Ошибка при изменении категории услуги.",
                            reply_markup=get_service_actions_keyboard(service_id)
                        )
                else:
                    await message.answer(
                        "Такой категории не существует. Попробуйте еще раз или введите 0, чтобы удалить категорию.",
                        reply_markup=get_service_actions_keyboard(service_id)
                    )
                    return
        except ValueError:
            await message.answer(
                "Пожалуйста, введите корректный ID категории или 0 для удаления категории."
            )
            return
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("delete_service_confirm_"))
    async def delete_service_confirm(callback: CallbackQuery):
        """Confirm service deletion"""
        service_id = callback.data.replace("delete_service_confirm_", "")
        service = await service_commands.get_service(service_id)
        
        if not service:
            await callback.message.edit_text(
                "Услуга не найдена.",
                reply_markup=get_services_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить услугу '{service.get('name')}'?",
            reply_markup=get_confirm_delete_keyboard(service_id, "service")
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("confirm_delete_service_"))
    async def delete_service(callback: CallbackQuery):
        """Delete service"""
        service_id = callback.data.replace("confirm_delete_service_", "")
        
        # Delete the service
        success = await service_commands.delete_service(service_id)
        
        if success:
            await callback.message.edit_text(
                "Услуга успешно удалена.",
                reply_markup=get_services_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при удалении услуги.",
                reply_markup=get_services_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("update_category_price_"))
    async def update_category_price_start(callback: CallbackQuery, state: FSMContext):
        """Start updating prices for all services in a category"""
        category_id = callback.data.replace("update_category_price_", "")
        category = await service_commands.get_category(category_id)
        
        if not category:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=get_services_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Введите цену для всех услуг в категории '{category.get('name')}' (только цифры):"
        )
        await state.update_data(category_id=category_id)
        await state.set_state(AdminServiceStates.editing_price)
        await callback.answer()
    
    # Category management handlers
    @dp.callback_query(F.data == "admin_categories")
    async def admin_categories(callback: CallbackQuery):
        """Show categories management menu"""
        await callback.message.edit_text(
            "Управление категориями услуг:",
            reply_markup=get_categories_management_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "add_category")
    async def add_category_start(callback: CallbackQuery, state: FSMContext):
        """Start adding a new category"""
        await callback.message.edit_text("Введите название новой категории:")
        await state.set_state(AdminCategoryStates.adding_name)
        await callback.answer()
    
    @dp.message(AdminCategoryStates.adding_name)
    async def add_category_name(message: Message, state: FSMContext):
        """Handle category name input"""
        # Create the category
        category = await service_commands.add_category(name=message.text)
        
        if category:
            await message.answer(
                f"Категория '{category['name']}' успешно добавлена!",
                reply_markup=get_categories_management_keyboard()
            )
        else:
            await message.answer(
                "Ошибка при добавлении категории.",
                reply_markup=get_categories_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data == "view_categories")
    async def view_categories(callback: CallbackQuery):
        """Show all categories"""
        categories = await service_commands.get_categories()
        
        if not categories:
            await callback.message.edit_text(
                "В базе нет категорий. Добавьте несколько категорий.",
                reply_markup=get_categories_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            "Все категории услуг:",
            reply_markup=get_all_categories_keyboard(categories)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_view_category_"))
    async def admin_view_category(callback: CallbackQuery):
        """Show category details"""
        category_id = callback.data.replace("admin_view_category_", "")
        category = await service_commands.get_category(category_id)
        
        if not category:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=get_categories_management_keyboard()
            )
            return
        
        # Count services in this category
        services = await service_commands.get_services_in_category(category_id)
        service_count = len(services)
        
        category_text = (
            f"📋 Информация о категории\n\n"
            f"📌 Название: {category.get('name')}\n"
            f"🔢 ID: {category.get('id')}\n"
            f"🛍 Количество услуг: {service_count}\n"
        )
        
        await callback.message.edit_text(
            category_text,
            reply_markup=get_category_actions_keyboard(category_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_category_"))
    async def edit_category(callback: CallbackQuery):
        """Show category edit options"""
        category_id = callback.data.replace("edit_category_", "")
        category = await service_commands.get_category(category_id)
        
        if not category:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=get_categories_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Выберите, что вы хотите изменить для категории '{category.get('name')}':",
            reply_markup=get_edit_category_keyboard(category_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_category_name_"))
    async def edit_category_name_start(callback: CallbackQuery, state: FSMContext):
        """Start editing category name"""
        category_id = callback.data.replace("edit_category_name_", "")
        await state.update_data(category_id=category_id)
        
        await callback.message.edit_text("Введите новое название категории:")
        await state.set_state(AdminCategoryStates.editing_name)
        await callback.answer()
    
    @dp.message(AdminCategoryStates.editing_name)
    async def edit_category_name(message: Message, state: FSMContext):
        """Handle category name edit"""
        data = await state.get_data()
        category_id = data.get('category_id')
        
        # Update category name
        success = await service_commands.update_category(category_id, name=message.text)
        
        if success:
            await message.answer(
                f"Название категории успешно изменено на '{message.text}'.",
                reply_markup=get_category_actions_keyboard(category_id)
            )
        else:
            await message.answer(
                "Ошибка при изменении названия категории.",
                reply_markup=get_categories_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("delete_category_confirm_"))
    async def delete_category_confirm(callback: CallbackQuery):
        """Confirm category deletion"""
        category_id = callback.data.replace("delete_category_confirm_", "")
        category = await service_commands.get_category(category_id)
        
        if not category:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=get_categories_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить категорию '{category.get('name')}'?\n\n"
            f"Это также уберет эту категорию у всех услуг, но сами услуги останутся в базе без категории.",
            reply_markup=get_confirm_delete_keyboard(category_id, "category")
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("confirm_delete_category_"))
    async def delete_category(callback: CallbackQuery):
        """Delete category"""
        category_id = callback.data.replace("confirm_delete_category_", "")
        
        # Delete the category
        success = await service_commands.delete_category(category_id)
        
        if success:
            await callback.message.edit_text(
                "Категория успешно удалена.",
                reply_markup=get_categories_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при удалении категории.",
                reply_markup=get_categories_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("view_category_"))
    async def view_category(callback: CallbackQuery):
        """Show services in a category from edit menu"""
        category_id = callback.data.replace("view_category_", "")
        category = await service_commands.get_category(category_id)
        
        if not category:
            await callback.message.edit_text(
                "Категория не найдена.",
                reply_markup=get_categories_management_keyboard()
            )
            return
        
        # Get services in this category
        services = await service_commands.get_services_in_category(category_id)
        
        if not services:
            await callback.message.edit_text(
                f"В категории '{category.get('name')}' нет услуг.",
                reply_markup=get_category_actions_keyboard(category_id)
            )
            return
        
        await callback.message.edit_text(
            f"Услуги в категории '{category.get('name')}':",
            reply_markup=get_category_services_keyboard(services, category.get('name'))
        )
        await callback.answer()
    
    # Special offers management handlers
    @dp.callback_query(F.data == "admin_offers")
    async def admin_offers(callback: CallbackQuery):
        """Show offers management menu"""
        await callback.message.edit_text(
            "Управление специальными предложениями:",
            reply_markup=get_offers_management_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "add_offer")
    async def add_offer_start(callback: CallbackQuery, state: FSMContext):
        """Start adding a new special offer"""
        await callback.message.edit_text("Введите название специального предложения:")
        await state.set_state(AdminOfferStates.adding_name)
        await callback.answer()
    
    @dp.message(AdminOfferStates.adding_name)
    async def add_offer_name(message: Message, state: FSMContext):
        """Handle offer name input"""
        # Save name to FSM context
        await state.update_data(name=message.text)
        
        await message.answer("Введите описание специального предложения:")
        await state.set_state(AdminOfferStates.adding_description)
    
    @dp.message(AdminOfferStates.adding_description)
    async def add_offer_description(message: Message, state: FSMContext):
        """Handle offer description input"""
        # Save description to FSM context
        await state.update_data(description=message.text)
        
        await message.answer("Введите цену специального предложения (только цифры):")
        await state.set_state(AdminOfferStates.adding_price)
    
    @dp.message(AdminOfferStates.adding_price)
    async def add_offer_price(message: Message, state: FSMContext):
        """Handle offer price input"""
        try:
            price = float(message.text)
            await state.update_data(price=price)
            
            await message.answer("Введите продолжительность специального предложения в минутах (только цифры):")
            await state.set_state(AdminOfferStates.adding_duration)
        except ValueError:
            await message.answer("Пожалуйста, введите корректную цену (только цифры).")
    
    @dp.message(AdminOfferStates.adding_duration)
    async def add_offer_duration(message: Message, state: FSMContext):
        """Handle offer duration input"""
        try:
            duration = int(message.text)
            await state.update_data(duration=duration)
            
            # Complete offer creation
            data = await state.get_data()
            
            # Create the offer
            offer = await service_commands.add_offer(
                name=data.get('name'),
                description=data.get('description'),
                price=data.get('price'),
                duration=duration
            )
            
            if offer:
                await message.answer(
                    f"Специальное предложение '{offer['name']}' успешно добавлено!",
                    reply_markup=get_offers_management_keyboard()
                )
            else:
                await message.answer(
                    "Ошибка при добавлении специального предложения.",
                    reply_markup=get_offers_management_keyboard()
                )
            
            # Reset the state
            await state.clear()
        except ValueError:
            await message.answer("Пожалуйста, введите корректную продолжительность в минутах (только цифры).")
    
    @dp.callback_query(F.data == "view_offers")
    async def view_offers(callback: CallbackQuery):
        """Show all special offers"""
        offers = await service_commands.get_offers()
        
        if not offers:
            await callback.message.edit_text(
                "В базе нет специальных предложений. Добавьте несколько предложений.",
                reply_markup=get_offers_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            "Все специальные предложения:",
            reply_markup=get_all_offers_keyboard(offers)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_view_offer_"))
    async def admin_view_offer(callback: CallbackQuery):
        """Show offer details"""
        offer_id = callback.data.replace("admin_view_offer_", "")
        offer = await service_commands.get_offer(offer_id)
        
        if not offer:
            await callback.message.edit_text(
                "Специальное предложение не найдено.",
                reply_markup=get_offers_management_keyboard()
            )
            return
        
        offer_text = (
            f"📋 Информация о специальном предложении\n\n"
            f"📌 Название: {offer.get('name')}\n"
            f"📝 Описание: {offer.get('description')}\n"
            f"💰 Цена: {offer.get('price')} руб.\n"
            f"⏱ Продолжительность: {offer.get('duration')} мин.\n"
        )
        
        await callback.message.edit_text(
            offer_text,
            reply_markup=get_offer_actions_keyboard(offer_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_offer_"))
    async def edit_offer(callback: CallbackQuery):
        """Show offer edit options"""
        offer_id = callback.data.replace("edit_offer_", "")
        offer = await service_commands.get_offer(offer_id)
        
        if not offer:
            await callback.message.edit_text(
                "Специальное предложение не найдено.",
                reply_markup=get_offers_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Выберите, что вы хотите изменить для предложения '{offer.get('name')}':",
            reply_markup=get_edit_offer_keyboard(offer_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("edit_offer_name_"))
    async def edit_offer_name_start(callback: CallbackQuery, state: FSMContext):
        """Start editing offer name"""
        offer_id = callback.data.replace("edit_offer_name_", "")
        await state.update_data(offer_id=offer_id)
        
        await callback.message.edit_text("Введите новое название специального предложения:")
        await state.set_state(AdminOfferStates.editing_name)
        await callback.answer()
    
    @dp.message(AdminOfferStates.editing_name)
    async def edit_offer_name(message: Message, state: FSMContext):
        """Handle offer name edit"""
        data = await state.get_data()
        offer_id = data.get('offer_id')
        
        # Update offer name
        success = await service_commands.update_offer(offer_id, name=message.text)
        
        if success:
            await message.answer(
                f"Название специального предложения успешно изменено на '{message.text}'.",
                reply_markup=get_offer_actions_keyboard(offer_id)
            )
        else:
            await message.answer(
                "Ошибка при изменении названия специального предложения.",
                reply_markup=get_offers_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("delete_offer_confirm_"))
    async def delete_offer_confirm(callback: CallbackQuery):
        """Confirm offer deletion"""
        offer_id = callback.data.replace("delete_offer_confirm_", "")
        offer = await service_commands.get_offer(offer_id)
        
        if not offer:
            await callback.message.edit_text(
                "Специальное предложение не найдено.",
                reply_markup=get_offers_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Вы уверены, что хотите удалить специальное предложение '{offer.get('name')}'?",
            reply_markup=get_confirm_delete_keyboard(offer_id, "offer")
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("confirm_delete_offer_"))
    async def delete_offer(callback: CallbackQuery):
        """Delete offer"""
        offer_id = callback.data.replace("confirm_delete_offer_", "")
        
        # Delete the offer
        success = await service_commands.delete_offer(offer_id)
        
        if success:
            await callback.message.edit_text(
                "Специальное предложение успешно удалено.",
                reply_markup=get_offers_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при удалении специального предложения.",
                reply_markup=get_offers_management_keyboard()
            )
        
        await callback.answer()
    
    # Appointment management handlers
    @dp.callback_query(F.data == "admin_appointments")
    async def admin_appointments(callback: CallbackQuery):
        """Show appointments management menu"""
        await callback.message.edit_text(
            "Управление записями:",
            reply_markup=get_admin_appointments_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "admin_appointments_today")
    async def admin_appointments_today(callback: CallbackQuery):
        """Show today's appointments"""
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        appointments = await appointment_commands.get_appointments_by_date(today)
        
        if not appointments:
            await callback.message.edit_text(
                "На сегодня нет записей.",
                reply_markup=get_appointments_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Записи на сегодня ({today}):",
            reply_markup=get_date_appointments_admin_keyboard(appointments, today)
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "admin_appointments_all")
    async def admin_appointments_all(callback: CallbackQuery, state: FSMContext):
        """Show all appointments"""
        appointments = await appointment_commands.get_all_appointments()
        
        if not appointments:
            await callback.message.edit_text(
                "В базе нет записей.",
                reply_markup=get_appointments_management_keyboard()
            )
            return
        
        # Group appointments by date for better display
        grouped_appointments = {}
        for appointment in appointments:
            date = appointment.get('date')
            if date not in grouped_appointments:
                grouped_appointments[date] = []
            
            # Get client details
            user = await user_commands.get_user(appointment.get('user_id'))
            if user:
                appointment['client_name'] = user.get('full_name') or user.get('username') or f"ID: {user.get('user_id')}"
            
            grouped_appointments[date].append(appointment)
        
        # Sort dates
        sorted_dates = sorted(grouped_appointments.keys())
        
        # Create a list of appointments grouped by date
        message_text = "Все записи:\n\n"
        for date in sorted_dates:
            message_text += f"📅 {date}:\n"
            for appointment in grouped_appointments[date]:
                service = await service_commands.get_service(appointment.get('service_id'))
                service_name = service.get('name') if service else "Неизвестная услуга"
                
                status_emoji = "✅" if appointment.get('status') == 'completed' else "🔄" if appointment.get('status') == 'confirmed' else "⏳" if appointment.get('status') == 'pending' else "❌"
                
                message_text += f"  {status_emoji} {appointment.get('time')} - {service_name} - {appointment.get('client_name')}\n"
            message_text += "\n"
        
        # If message is too long, need pagination or truncation
        if len(message_text) > 4000:
            message_text = message_text[:3990] + "\n... (и еще записи)"
        
        await callback.message.edit_text(
            message_text,
            reply_markup=get_appointments_management_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "admin_appointments_date")
    async def admin_appointments_date(callback: CallbackQuery, state: FSMContext):
        """Ask for date to show appointments"""
        await callback.message.edit_text(
            "Введите дату в формате YYYY-MM-DD (например, 2023-01-01):"
        )
        await state.set_state(AdminAppointmentStates.selecting_date)
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_appointments_date_"))
    async def admin_appointments_date_selected(callback: CallbackQuery):
        """Show appointments for selected date"""
        date = callback.data.replace("admin_appointments_date_", "")
        appointments = await appointment_commands.get_appointments_by_date(date)
        
        if not appointments:
            await callback.message.edit_text(
                f"На {date} нет записей.",
                reply_markup=get_appointments_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Записи на {date}:",
            reply_markup=get_date_appointments_admin_keyboard(appointments, date)
        )
        await callback.answer()
    
    @dp.message(AdminAppointmentStates.selecting_date)
    async def admin_appointments_date_manual(message: Message, state: FSMContext):
        """Handle manual date input"""
        try:
            # Validate date format
            date = datetime.datetime.strptime(message.text, "%Y-%m-%d").strftime("%Y-%m-%d")
            
            appointments = await appointment_commands.get_appointments_by_date(date)
            
            if not appointments:
                await message.answer(
                    f"На {date} нет записей.",
                    reply_markup=get_appointments_management_keyboard()
                )
            else:
                await message.answer(
                    f"Записи на {date}:",
                    reply_markup=get_date_appointments_admin_keyboard(appointments, date)
                )
        except ValueError:
            await message.answer(
                "Пожалуйста, введите дату в формате YYYY-MM-DD (например, 2023-01-01)."
            )
            return
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data.startswith("admin_view_appointment_"))
    async def admin_view_appointment(callback: CallbackQuery):
        """Show appointment details"""
        appointment_id = callback.data.replace("admin_view_appointment_", "")
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        if not appointment:
            await callback.message.edit_text(
                "Запись не найдена.",
                reply_markup=get_appointments_management_keyboard()
            )
            return
        
        # Get additional details
        service = await service_commands.get_service(appointment.get('service_id'))
        service_name = service.get('name') if service else "Неизвестная услуга"
        service_price = service.get('price') if service else "N/A"
        
        user = await user_commands.get_user(appointment.get('user_id'))
        client_name = user.get('full_name') or user.get('username') or f"ID: {user.get('user_id')}" if user else "Неизвестный клиент"
        
        master = await master_commands.get_master(appointment.get('master_id')) if appointment.get('master_id') else None
        master_name = master.get('name') if master else "Не назначен"
        
        status_map = {
            'pending': "⏳ Ожидает подтверждения",
            'confirmed': "✅ Подтверждена",
            'completed': "✅ Выполнена",
            'canceled': "❌ Отменена",
            'paid': "💰 Оплачена"
        }
        status_text = status_map.get(appointment.get('status'), "⏳ В обработке")
        
        payment_method = appointment.get('payment_method', "Не указан")
        
        appointment_text = (
            f"📋 Информация о записи #{appointment.get('id')}\n\n"
            f"📅 Дата: {appointment.get('date')}\n"
            f"🕒 Время: {appointment.get('time')}\n"
            f"🛍 Услуга: {service_name}\n"
            f"💰 Цена: {service_price} руб.\n"
            f"👤 Клиент: {client_name}\n"
            f"👨‍⚕️ Мастер: {master_name}\n"
            f"📊 Статус: {status_text}\n"
            f"💳 Способ оплаты: {payment_method}\n"
        )
        
        await callback.message.edit_text(
            appointment_text,
            reply_markup=get_appointment_actions_keyboard(appointment_id, appointment.get('status'))
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("mark_completed_"))
    async def mark_completed(callback: CallbackQuery):
        """Mark appointment as completed"""
        appointment_id = callback.data.replace("mark_completed_", "")
        
        # Update the appointment status
        success = await appointment_commands.update_appointment_status(appointment_id, "completed")
        
        if success:
            await callback.message.edit_text(
                "Запись отмечена как выполненная.",
                reply_markup=get_appointments_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при обновлении статуса записи.",
                reply_markup=get_appointments_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("mark_paid_"))
    async def mark_paid(callback: CallbackQuery):
        """Mark appointment as paid"""
        appointment_id = callback.data.replace("mark_paid_", "")
        
        # Update the appointment status
        success = await appointment_commands.update_appointment_status(appointment_id, "paid")
        
        if success:
            await callback.message.edit_text(
                "Запись отмечена как оплаченная.",
                reply_markup=get_appointments_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при обновлении статуса записи.",
                reply_markup=get_appointments_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("set_payment_"))
    async def set_payment_method(callback: CallbackQuery):
        """Set payment method for appointment"""
        parts = callback.data.split("_")
        appointment_id = parts[2]
        payment_method = parts[1]
        
        payment_map = {
            "cash": "Наличные",
            "card": "Карта/Терминал",
            "transfer": "Перевод"
        }
        
        # Update the appointment payment method
        success = await appointment_commands.update_appointment_payment(appointment_id, payment_map.get(payment_method, "Неизвестно"))
        
        if success:
            await callback.message.edit_text(
                f"Способ оплаты установлен: {payment_map.get(payment_method, 'Неизвестно')}",
                reply_markup=get_appointments_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при обновлении способа оплаты.",
                reply_markup=get_appointments_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_cancel_appointment_"))
    async def admin_cancel_appointment_confirm(callback: CallbackQuery):
        """Confirm appointment cancellation"""
        appointment_id = callback.data.replace("admin_cancel_appointment_", "")
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        if not appointment:
            await callback.message.edit_text(
                "Запись не найдена.",
                reply_markup=get_appointments_management_keyboard()
            )
            return
        
        await callback.message.edit_text(
            f"Вы уверены, что хотите отменить запись #{appointment_id}?",
            reply_markup=get_cancel_appointment_keyboard(appointment_id)
        )
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("confirm_cancel_appointment_"))
    async def admin_cancel_appointment(callback: CallbackQuery):
        """Cancel appointment"""
        appointment_id = callback.data.replace("confirm_cancel_appointment_", "")
        
        # Cancel the appointment
        success = await appointment_commands.cancel_appointment(appointment_id)
        
        if success:
            await callback.message.edit_text(
                "Запись успешно отменена.",
                reply_markup=get_appointments_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при отмене записи.",
                reply_markup=get_appointments_management_keyboard()
            )
        
        await callback.answer()
    
    @dp.callback_query(F.data.startswith("admin_confirm_appointment_"))
    async def admin_confirm_appointment(callback: CallbackQuery):
        """Confirm a pending appointment"""
        appointment_id = callback.data.replace("admin_confirm_appointment_", "")
        
        # Update the appointment status to confirmed
        success = await appointment_commands.update_appointment_status(appointment_id, "confirmed")
        
        if success:
            # Verify the user so future appointments are auto-confirmed
            appointment = await appointment_commands.get_appointment(appointment_id)
            if appointment:
                await appointment_commands.verify_user(appointment.get('user_id'))
            
            await callback.message.edit_text(
                "Запись подтверждена. Клиент добавлен в список проверенных клиентов.",
                reply_markup=get_appointments_management_keyboard()
            )
        else:
            await callback.message.edit_text(
                "Ошибка при подтверждении записи.",
                reply_markup=get_appointments_management_keyboard()
            )
        
        await callback.answer()
    
    # Master management handlers
    @dp.callback_query(F.data == "admin_masters")
    async def admin_masters(callback: CallbackQuery):
        """Show masters management menu"""
        await callback.message.edit_text(
            "Управление мастерами:",
            reply_markup=get_masters_management_keyboard()
        )
        await callback.answer()
    
    @dp.callback_query(F.data == "add_master")
    async def add_master_start(callback: CallbackQuery, state: FSMContext):
        """Start adding a new master"""
        await callback.message.edit_text("Введите ID пользователя Telegram для нового мастера:")
        await state.set_state(AdminMasterStates.adding_name)
        await callback.answer()
    
    @dp.message(AdminMasterStates.adding_name)
    async def add_master_name(message: Message, state: FSMContext):
        """Handle master name input"""
        try:
            user_id = int(message.text)
            await state.update_data(user_id=user_id)
            
            # Check if user exists in the database
            user = await user_commands.get_user(user_id)
            
            if not user:
                # User doesn't exist, create them
                await user_commands.add_user(
                    user_id=user_id,
                    username=f"master_{user_id}",
                    full_name="Новый мастер",
                    role="master"
                )
            
            await message.answer("Введите имя мастера:")
            await state.set_state(AdminMasterStates.adding_telegram)
        except ValueError:
            await message.answer("Пожалуйста, введите корректный ID пользователя (только цифры).")
    
    @dp.message(AdminMasterStates.adding_telegram)
    async def add_master_telegram(message: Message, state: FSMContext):
        """Handle master telegram input"""
        await state.update_data(name=message.text)
        
        await message.answer("Введите telegram контакт мастера (username без @):")
        await state.set_state(AdminMasterStates.adding_address)
    
    @dp.message(AdminMasterStates.adding_address)
    async def add_master_address(message: Message, state: FSMContext):
        """Handle master address input"""
        await state.update_data(telegram=message.text)
        
        await message.answer("Введите адрес мастера (необязательно, можно пропустить командой /skip):")
        await state.set_state(AdminMasterStates.adding_location)
    
    @dp.message(AdminMasterStates.adding_location)
    async def add_master_location(message: Message, state: FSMContext):
        """Handle master location input"""
        if message.text == "/skip":
            await state.update_data(address="")
        else:
            await state.update_data(address=message.text)
        
        await message.answer("Введите местоположение (координаты или описание, необязательно, можно пропустить командой /skip):")
        await add_master_complete(message, state)
    
    async def add_master_complete(message: Message, state: FSMContext):
        """Complete master addition process"""
        if message.text == "/skip":
            await state.update_data(location="")
        else:
            await state.update_data(location=message.text)
        
        # Get all the data from FSM context
        data = await state.get_data()
        
        # Create the master
        master = await master_commands.add_master(
            user_id=data.get('user_id'),
            name=data.get('name'),
            telegram=data.get('telegram'),
            address=data.get('address', ""),
            location=data.get('location', "")
        )
        
        if master:
            await message.answer(
                f"Мастер '{master['name']}' успешно добавлен!",
                reply_markup=get_masters_management_keyboard()
            )
        else:
            await message.answer(
                "Ошибка при добавлении мастера.",
                reply_markup=get_masters_management_keyboard()
            )
        
        # Reset the state
        await state.clear()
    
    @dp.callback_query(F.data == "view_masters_admin")
    async def view_masters_admin(callback: CallbackQuery):
        """Show all masters"""
        masters = await master_commands.get_masters()
        
        if not masters:
            await callback.message.edit_text(
                "В базе нет мастеров. Добавьте несколько мастеров.",
                reply_markup=get_masters_management_keyboard()
            )
            return
        
        # Create a list of masters
        message_text = "Все мастера:\n\n"
        
        for idx, master in enumerate(masters, start=1):
            message_text += f"{idx}. {master.get('name')} (@{master.get('telegram')})\n"
            if master.get('address'):
                message_text += f"   📍 {master.get('address')}\n"
        
        await callback.message.edit_text(
            message_text,
            reply_markup=get_masters_management_keyboard()
        )
        await callback.answer()
    
    # Admin help handler
    @dp.message(Command("admin_help"))
    async def admin_help(message: Message):
        """Show admin help information"""
        # Check if user is admin
        user_id = message.from_user.id
        user = await user_commands.get_user(user_id)
        if not user or user.get('role') != 'admin':
            await message.answer("У вас нет доступа к этой команде.")
            return
        
        help_text = (
            "📋 Руководство по использованию админ-панели\n\n"
            
            "🔄 Быстрая настройка:\n"
            "1. Сначала создайте категории услуг через 'Управление категориями' > 'Добавить категорию'\n"
            "2. Для быстрого добавления услуг используйте 'Управление услугами' > 'Быстрое создание услуг'\n"
            "3. Добавьте мастеров через 'Управление мастерами' > 'Добавить мастера'\n\n"
            
            "📊 Управление услугами:\n"
            "- Используйте 'Быстрое создание услуг' для добавления типовых услуг из шаблонов\n"
            "- Для редактирования цен перейдите в 'Просмотреть услуги' > выберите категорию > выберите услугу\n"
            "- Для добавления персональных услуг используйте 'Добавить услугу'\n\n"
            
            "👨‍💼 Управление мастерами:\n"
            "- Для добавления мастера вам потребуется его Telegram ID\n"
            "- После добавления мастера вы можете настроить его рабочие часы\n\n"
            
            "📅 Управление записями:\n"
            "- В разделе 'Записи по дате' вы можете просматривать и управлять записями клиентов\n"
            "- Для подтверждения записи нового клиента нажмите 'Подтвердить'\n"
            "- После выполнения услуги отметьте запись как 'Выполнена'\n"
            "- После оплаты укажите способ оплаты и отметьте запись как 'Оплачена'\n\n"
            
            "⚠️ Важно: Первая запись от нового клиента требует подтверждения администратора\n"
        )
        
        await message.answer(help_text)
