from aiogram import F, Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import datetime
import logging

# Import utils and keyboards
from utils.db_api import service_commands, appointment_commands, master_commands
from keyboards import client_keyboards

# Temporary data storage (use this instead of bot['temp_data'])
temp_user_data = {}

router = Router()

class BookingStates(StatesGroup):
    select_category = State()
    select_service = State()
    select_master = State()
    select_date = State()
    select_time = State()
    confirm_booking = State()

# Command handlers
@router.message(Command("book"))
async def cmd_book(message: Message, state: FSMContext):
    # Start booking process
    await state.clear()
    await message.answer("Добро пожаловать в систему записи! Выберите категорию услуг:", 
                        reply_markup=await client_keyboards.get_categories_keyboard())
    await state.set_state(BookingStates.select_category)

# Category selection
@router.callback_query(BookingStates.select_category, F.data == "back_to_main")
async def back_to_main_from_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Главное меню:", reply_markup=await client_keyboards.get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(BookingStates.select_category)
async def select_category(callback: CallbackQuery, state: FSMContext):
    category_name = callback.data
    
    # Store selected category
    await state.update_data(selected_category=category_name)
    
    # Get services in this category
    services = await service_commands.get_services_by_category_name(category_name)
    
    if services:
        await callback.message.answer("Выберите услугу:", 
                                    reply_markup=await client_keyboards.get_services_keyboard(services))
        await state.set_state(BookingStates.select_service)
    else:
        await callback.message.answer("В данной категории нет услуг.")
        await state.set_state(BookingStates.select_category)
    
    await callback.answer()

# Service selection
@router.callback_query(BookingStates.select_service, F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите категорию услуг:", 
                                reply_markup=await client_keyboards.get_categories_keyboard())
    await state.set_state(BookingStates.select_category)
    await callback.answer()

@router.callback_query(BookingStates.select_service)
async def select_service(callback: CallbackQuery, state: FSMContext):
    service_id = callback.data
    
    # Store selected service
    await state.update_data(selected_service_id=service_id)
    
    # Get service details
    service = await service_commands.get_service(service_id)
    
    if service:
        # Get available masters for this service
        masters = await master_commands.get_masters()
        
        if masters:
            await callback.message.answer("Выберите мастера:", 
                                        reply_markup=await client_keyboards.get_masters_keyboard(masters))
            await state.set_state(BookingStates.select_master)
        else:
            await callback.message.answer("Нет доступных мастеров для данной услуги.")
            await state.set_state(BookingStates.select_service)
    else:
        await callback.message.answer("Услуга не найдена.")
        await state.set_state(BookingStates.select_service)
    
    await callback.answer()

# Master selection
@router.callback_query(BookingStates.select_master, F.data == "back_to_services")
async def back_to_services(callback: CallbackQuery, state: FSMContext):
    # Retrieve the selected category from the state
    data = await state.get_data()
    selected_category = data.get("selected_category")
    
    # If a category was previously selected, show services for that category
    if selected_category:
        services = await service_commands.get_services_by_category_name(selected_category)
        await callback.message.answer("Выберите услугу:", 
                                    reply_markup=await client_keyboards.get_services_keyboard(services))
        await state.set_state(BookingStates.select_service)
    else:
        # If no category was selected, go back to the category selection
        await callback.message.answer("Выберите категорию услуг:", 
                                    reply_markup=await client_keyboards.get_categories_keyboard())
        await state.set_state(BookingStates.select_category)
    
    await callback.answer()

@router.callback_query(BookingStates.select_master)
async def select_master(callback: CallbackQuery, state: FSMContext):
    master_id = callback.data
    
    # Store selected master
    await state.update_data(selected_master_id=master_id)
    
    # Ask for the desired date
    await callback.message.answer("Выберите желаемую дату (ГГГГ-ММ-ДД):")
    await state.set_state(BookingStates.select_date)
    
    await callback.answer()

# Date selection
@router.message(BookingStates.select_date)
async def select_date(message: Message, state: FSMContext):
    date = message.text
    
    # Validate date format
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return
    
    # Store selected date
    await state.update_data(selected_date=date)
    
    # Get data from state
    data = await state.get_data()
    master_id = data.get('selected_master_id')
    
    # Get available times for this master and date
    available_times = await master_commands.get_master_availability(master_id, date)
    
    if available_times:
        await message.answer("Выберите время:", 
                            reply_markup=await client_keyboards.get_times_keyboard(available_times))
        await state.set_state(BookingStates.select_time)
    else:
        await message.answer("Нет доступного времени на выбранную дату. Пожалуйста, выберите другую дату.")
        await state.set_state(BookingStates.select_date)

# Time selection
@router.callback_query(BookingStates.select_time, F.data == "back_to_date")
async def back_to_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Выберите желаемую дату (ГГГГ-ММ-ДД):")
    await state.set_state(BookingStates.select_date)
    await callback.answer()

@router.callback_query(BookingStates.select_time)
async def select_time(callback: CallbackQuery, state: FSMContext):
    time = callback.data
    
    # Store selected time
    await state.update_data(selected_time=time)
    
    # Get data from state
    data = await state.get_data()
    category_name = data.get('selected_category')
    service_id = data.get('selected_service_id')
    master_id = data.get('selected_master_id')
    date = data.get('selected_date')
    
    # Get service and master details
    service = await service_commands.get_service(service_id)
    master = await master_commands.get_master(master_id)
    
    if service and master:
        # Confirm booking
        confirmation_text = (
            f"Подтвердите запись:\n"
            f"Категория: {category_name}\n"
            f"Услуга: {service['name']}\n"
            f"Мастер: {master['name']}\n"
            f"Дата: {date}\n"
            f"Время: {time}"
        )
        await callback.message.answer(confirmation_text, 
                                    reply_markup=await client_keyboards.get_confirmation_keyboard())
        await state.set_state(BookingStates.confirm_booking)
    else:
        await callback.message.answer("Ошибка: Услуга или мастер не найдены. Пожалуйста, начните заново.")
        await state.clear()
        await state.set_state(BookingStates.select_category)
    
    await callback.answer()

# Confirmation
@router.callback_query(BookingStates.confirm_booking, F.data == "confirm")
async def confirm(callback: CallbackQuery, state: FSMContext):
    # Get data from state
    data = await state.get_data()
    user_id = callback.from_user.id
    service_id = data.get('selected_service_id')
    master_id = data.get('selected_master_id')
    date = data.get('selected_date')
    time = data.get('selected_time')
    
    # Create appointment
    appointment = await appointment_commands.add_appointment(
        user_id=user_id,
        service_id=service_id,
        master_id=master_id,
        date=date,
        time=time
    )
    
    if appointment:
        await callback.message.answer("Запись успешно создана!", 
                                    reply_markup=await client_keyboards.get_main_menu_keyboard())
    else:
        await callback.message.answer("Ошибка при создании записи. Пожалуйста, попробуйте еще раз.")
    
    await state.clear()
    await callback.answer()

@router.callback_query(BookingStates.confirm_booking, F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Запись отменена.")
    await callback.message.answer("Главное меню:", 
                               reply_markup=await client_keyboards.get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery, state: FSMContext):
    # Use temp_user_data dictionary instead of bot['temp_data']
    user_id = callback.from_user.id
    if user_id in temp_user_data:
        del temp_user_data[user_id]
    
    await state.clear()
    await callback.message.answer("Запись отменена.")
    await callback.message.answer("Главное меню:", 
                               reply_markup=await client_keyboards.get_main_menu_keyboard())
    await callback.answer()

# Make sure to replace all other instances of bot['temp_data'] with our temp_user_data dictionary
