
# Partial update of the admin.py file
# Adding new functionality for special offers, categories, and user verification

from aiogram import Dispatcher, F, Bot
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
    adding_category = State()
    editing_name = State()
    editing_description = State()
    editing_price = State()
    editing_duration = State()
    editing_category = State()

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

# ... keep existing code (function cmd_admin and back_to_admin)

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
            f"✅ Категория добавлена успешно!\n\nНазвание: {name}",
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

# Handlers for editing offer fields (similar to service editing)
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

# ... similar handlers for other offer fields (description, price, duration)

async def delete_offer_confirm(callback: CallbackQuery, role: str):
    """Confirm offer deletion"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract offer ID from callback data
    offer_id = callback.data.split('_')[2]
    
    await callback.message.edit_text(
        "Вы уверены, что хотите удалить это специальное предложение?",
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

# Adding functionality for user verification
async def admin_view_appointment(callback: CallbackQuery, role: str, bot: Bot):
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
        await callback.answer()
        return
    
    # Get service and master details
    service_info = "Не указана"
    master_info = "Не указан"
    user_info = f"ID: {appointment.get('user_id', 'Не указан')}"
    
    service = await service_commands.get_service(appointment.get('service_id'))
    if service:
        service_info = f"{service.get('name')} - {service.get('price')}"
    
    master = await master_commands.get_master(appointment.get('master_id'))
    if master:
        master_info = master.get('name')
    
    # Format payment method
    payment_method = appointment.get('payment_method', 'Не указан')
    payment_text = {
        'cash': '💵 Наличные',
        'card': '💳 Карта/Терминал',
        'transfer': '📲 Перевод'
    }.get(payment_method, payment_method)
    
    # Format status
    status = appointment.get('status', 'confirmed')
    status_text = {
        'confirmed': '✅ Подтверждено',
        'canceled': '❌ Отменено',
        'completed': '✓ Выполнено',
        'paid': '💰 Оплачено',
        'pending': '⏳ Ожидает подтверждения'
    }.get(status, status)
    
    # Format details
    details = f"""
Данные записи:

ID: {appointment['id']}
Дата: {appointment['date']}
Время: {appointment['time']}
Статус: {status_text}
Оплата: {payment_text}

Услуга: {service_info}
Мастер: {master_info}
Клиент: {user_info}
"""
    
    await callback.message.edit_text(
        details,
        reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, status)
    )
    
    # If this is a pending appointment from a new client, send notification to verify
    if status == "pending" and not await appointment_commands.is_user_verified(appointment.get('user_id')):
        await bot.send_message(
            callback.from_user.id,
            f"⚠️ Внимание! Новая запись от непроверенного клиента!\n\nID записи: {appointment['id']}\nКлиент: {user_info}\n\nТребуется подтверждение.",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, status)
        )
    
    await callback.answer()

async def admin_confirm_appointment(callback: CallbackQuery, role: str, bot: Bot):
    """Handle confirming a pending appointment"""
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
        await callback.answer()
        return
    
    # Update appointment status to confirmed
    success = await appointment_commands.update_appointment_status(appointment_id, "confirmed")
    
    # Verify the user for future appointments
    user_id = appointment.get('user_id')
    await appointment_commands.verify_user(user_id)
    
    if success:
        # Get service and master details for the notification
        service_info = "услугу"
        master_info = "мастера"
        
        service = await service_commands.get_service(appointment.get('service_id'))
        if service:
            service_info = service.get('name')
        
        master = await master_commands.get_master(appointment.get('master_id'))
        if master:
            master_info = master.get('name')
        
        # Notify the client that their appointment is confirmed
        try:
            await bot.send_message(
                user_id,
                f"✅ Ваша запись подтверждена!\n\nУслуга: {service_info}\nДата: {appointment.get('date')}\nВремя: {appointment.get('time')}\nМастер: {master_info}"
            )
        except Exception as e:
            print(f"Error sending confirmation to user: {e}")
        
        await callback.message.edit_text(
            "✅ Запись подтверждена. Клиент добавлен в список проверенных.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось подтвердить запись. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Update existing handlers
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

# Add handlers for appointment status updates
async def mark_completed(callback: CallbackQuery, role: str, bot: Bot):
    """Mark an appointment as completed"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[2]
    
    # Update appointment status
    success = await appointment_commands.complete_appointment(appointment_id)
    
    if success:
        # Get appointment details
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        await callback.message.edit_text(
            f"✅ Запись #{appointment_id} отмечена как выполненная.",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, "completed")
        )
        
        # Notify the client
        try:
            user_id = appointment.get('user_id')
            if user_id:
                await bot.send_message(
                    user_id,
                    f"✅ Ваша запись #{appointment_id} отмечена как выполненная."
                )
        except Exception as e:
            print(f"Error sending message to user: {e}")
    else:
        await callback.message.edit_text(
            "❌ Не удалось обновить статус записи. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def mark_paid(callback: CallbackQuery, role: str, bot: Bot):
    """Mark an appointment as paid"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[2]
    
    # Update appointment status
    success = await appointment_commands.update_appointment_status(appointment_id, "paid")
    
    if success:
        # Get appointment details
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        await callback.message.edit_text(
            f"✅ Запись #{appointment_id} отмечена как оплаченная.",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, "paid")
        )
        
        # Notify the client
        try:
            user_id = appointment.get('user_id')
            if user_id:
                await bot.send_message(
                    user_id,
                    f"✅ Ваша запись #{appointment_id} отмечена как оплаченная."
                )
        except Exception as e:
            print(f"Error sending message to user: {e}")
    else:
        await callback.message.edit_text(
            "❌ Не удалось обновить статус записи. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

async def set_payment_method(callback: CallbackQuery, role: str):
    """Set payment method for an appointment"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract data from callback data
    parts = callback.data.split('_')
    method = parts[2]
    appointment_id = parts[3]
    
    # Update appointment payment method
    success = await appointment_commands.update_appointment_payment(appointment_id, method)
    
    if success:
        # Get appointment details
        appointment = await appointment_commands.get_appointment(appointment_id)
        
        payment_text = {
            'cash': 'наличными',
            'card': 'картой/через терминал',
            'transfer': 'переводом'
        }.get(method, method)
        
        await callback.message.edit_text(
            f"✅ Способ оплаты для записи #{appointment_id} изменен на {payment_text}.",
            reply_markup=admin_keyboards.get_appointment_actions_keyboard(appointment_id, appointment.get('status', 'confirmed'))
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось обновить способ оплаты. Пожалуйста, попробуйте еще раз позже.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    
    await callback.answer()

# Handler for appointments by date
async def admin_appointments_date(callback: CallbackQuery, role: str):
    """Handle viewing appointments for a specific date"""
    # Check if user has admin or ceo role
    if role not in ["admin", "ceo"]:
        await callback.answer("Доступ запрещен. Это действие доступно только администраторам.")
        return
    
    # Extract date from callback data
    date = callback.data.split('_')[3]
    
    # Get appointments for this date
    appointments = await appointment_commands.get_appointments_by_date(date)
    
    if not appointments:
        await callback.message.edit_text(
            f"Нет записей на {date}.",
            reply_markup=admin_keyboards.get_back_to_admin_keyboard()
        )
    else:
        await callback.message.edit_text(
            f"Записи на {date}:",
            reply_markup=admin_keyboards.get_date_appointments_admin_keyboard(appointments, date)
        )
    
    await callback.answer()

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
    
    # Service management handlers
    dp.callback_query.register(add_service_start, F.data == "add_service")
    dp.message.register(add_service_name, AdminServiceStates.adding_name)
    dp.message.register(add_service_description, AdminServiceStates.adding_description)
    dp.message.register(add_service_price, AdminServiceStates.adding_price)
    dp.message.register(add_service_duration, AdminServiceStates.adding_duration)
    dp.callback_query.register(add_service_category, F.data.startswith("add_service_category_"))
    dp.callback_query.register(view_services, F.data == "view_services")
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
