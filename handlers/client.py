
from aiogram import Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from utils.db_api import service_commands, appointment_commands, master_commands
from keyboards import client_keyboards

# Define states for booking flow
class BookingStates(StatesGroup):
    selecting_master = State()
    selecting_service = State()
    selecting_date = State()
    selecting_time = State()
    selecting_payment = State()
    confirming = State()

async def cmd_start(message: Message):
    """Handle the /start command"""
    await message.answer(
        f"Здравствуйте, {message.from_user.first_name}! Добро пожаловать в сервис записи.",
        reply_markup=client_keyboards.get_main_menu_keyboard()
    )

async def cmd_help(message: Message):
    """Handle the /help command"""
    help_text = """
Доступные команды:
/start - Запустить бота и открыть главное меню
/help - Показать это сообщение

Чтобы записаться на услугу, выберите соответствующий пункт в меню.
"""
    await message.answer(help_text, reply_markup=client_keyboards.get_main_menu_keyboard())

async def main_menu(callback: CallbackQuery):
    """Handle main menu button click"""
    await callback.message.edit_text(
        f"Главное меню:",
        reply_markup=client_keyboards.get_main_menu_keyboard()
    )
    await callback.answer()

async def start_booking(callback: CallbackQuery, state: FSMContext):
    """Start the booking process"""
    # Reset state
    await state.clear()
    
    # Get available masters
    masters = await master_commands.get_all_masters()
    
    if not masters:
        await callback.message.edit_text(
            "К сожалению, в данный момент нет доступных мастеров. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        return
    
    # Set state to selecting master
    await state.set_state(BookingStates.selecting_master)
    
    # Show masters keyboard
    await callback.message.edit_text(
        "Пожалуйста, выберите мастера:",
        reply_markup=client_keyboards.get_masters_keyboard(masters)
    )
    await callback.answer()

async def view_masters(callback: CallbackQuery):
    """Show list of available masters"""
    # Get available masters
    masters = await master_commands.get_all_masters()
    
    if not masters:
        await callback.message.edit_text(
            "К сожалению, в данный момент нет доступных мастеров. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        return
    
    # Show masters keyboard
    await callback.message.edit_text(
        "Список доступных мастеров:",
        reply_markup=client_keyboards.get_masters_keyboard(masters)
    )
    await callback.answer()

async def master_selected(callback: CallbackQuery, state: FSMContext):
    """Handle master selection"""
    # Extract master ID from callback data
    master_id = callback.data.split('_')[1]
    
    # Store selected master ID in state
    await state.update_data(master_id=master_id)
    
    # Get master details
    master = await master_commands.get_master(master_id)
    
    if not master:
        await callback.message.edit_text(
            "Мастер не найден. Пожалуйста, выберите другого мастера.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Get available services
    services = await service_commands.get_all_services()
    
    if not services:
        await callback.message.edit_text(
            "К сожалению, в данный момент нет доступных услуг. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Set state to selecting service
    await state.set_state(BookingStates.selecting_service)
    
    # Show services keyboard
    await callback.message.edit_text(
        f"Вы выбрали мастера: {master['name']}\n\nПожалуйста, выберите услугу:",
        reply_markup=client_keyboards.get_services_keyboard(services)
    )
    
    # Answer callback query
    await callback.answer()

async def view_master_info(callback: CallbackQuery):
    """Handle viewing master information"""
    # Extract master ID from callback data
    master_id = callback.data.split('_')[1]
    
    # Get master details
    master = await master_commands.get_master(master_id)
    
    if not master:
        await callback.message.edit_text(
            "Мастер не найден. Пожалуйста, выберите другого мастера.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Format master information
    info_text = f"""
👨‍💼 **{master['name']}**

📱 Telegram: {master.get('telegram', 'Не указан')}
📍 Адрес: {master.get('address', 'Не указан')}

Для записи к мастеру нажмите кнопку ниже.
"""
    
    # Show master info
    await callback.message.edit_text(
        info_text,
        reply_markup=client_keyboards.get_master_info_keyboard(master),
        parse_mode="Markdown"
    )
    
    # Answer callback query
    await callback.answer()

async def book_with_master(callback: CallbackQuery, state: FSMContext):
    """Start booking with selected master"""
    # Extract master ID from callback data
    master_id = callback.data.split('_')[3]
    
    # Store selected master ID in state
    await state.update_data(master_id=master_id)
    
    # Get available services
    services = await service_commands.get_all_services()
    
    if not services:
        await callback.message.edit_text(
            "К сожалению, в данный момент нет доступных услуг. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Set state to selecting service
    await state.set_state(BookingStates.selecting_service)
    
    # Show services keyboard
    await callback.message.edit_text(
        "Пожалуйста, выберите услугу:",
        reply_markup=client_keyboards.get_services_keyboard(services)
    )
    
    # Answer callback query
    await callback.answer()

async def service_selected(callback: CallbackQuery, state: FSMContext):
    """Handle service selection"""
    # Extract service ID from callback data
    service_id = callback.data.split('_')[1]
    
    # Get service details for duration info
    service = await service_commands.get_service(service_id)
    if not service:
        await callback.message.edit_text(
            "Услуга не найдена. Пожалуйста, выберите другую услугу.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Store selected service ID and duration in state
    await state.update_data(service_id=service_id, duration=service.get('duration', 60))
    
    # Get state data to check if master is already selected
    data = await state.get_data()
    
    # If master is not selected, let user select a master
    if 'master_id' not in data:
        # Get available masters
        masters = await master_commands.get_all_masters()
        
        if not masters:
            await callback.message.edit_text(
                "К сожалению, в данный момент нет доступных мастеров. Пожалуйста, попробуйте позже.",
                reply_markup=client_keyboards.get_back_to_menu_keyboard()
            )
            await callback.answer()
            return
        
        # Set state to selecting master
        await state.set_state(BookingStates.selecting_master)
        
        # Show service details and masters keyboard
        service_text = f"""
Вы выбрали услугу: {service['name']}
Цена: {service['price']}
Длительность: {service.get('duration', 60)} мин

Описание: {service['description']}

Теперь выберите мастера:
"""
        
        await callback.message.edit_text(
            service_text,
            reply_markup=client_keyboards.get_masters_keyboard(masters)
        )
        
        # Answer callback query
        await callback.answer()
        return
    
    # Master is already selected, proceed to date selection
    # Set state to selecting date
    await state.set_state(BookingStates.selecting_date)
    
    # Show date selection keyboard
    await callback.message.edit_text(
        f"Вы выбрали услугу: {service['name']}\nЦена: {service['price']}\n\nПожалуйста, выберите дату для записи:",
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
    
    # Get state data
    data = await state.get_data()
    master_id = data.get('master_id')
    service_id = data.get('service_id')
    duration = data.get('duration', 60)
    
    # Set state to selecting time
    await state.set_state(BookingStates.selecting_time)
    
    # Show time selection keyboard
    await callback.message.edit_text(
        f"Выбранная дата: {date}\nПожалуйста, выберите время:",
        reply_markup=client_keyboards.get_time_keyboard(date, master_id, service_id, duration)
    )
    
    # Answer callback query
    await callback.answer()

async def time_selected(callback: CallbackQuery, state: FSMContext):
    """Handle time selection"""
    # Extract data from callback data
    parts = callback.data.split('_')
    date = parts[1]
    time = parts[2]
    
    # Check if master_id is in callback data
    master_id = None
    service_id = None
    if len(parts) > 3:
        if len(parts) > 4:
            master_id = parts[3]
            service_id = parts[4]
        else:
            master_id = parts[3]
    
    # Store selected time in state
    await state.update_data(time=time)
    if master_id:
        await state.update_data(master_id=master_id)
    if service_id:
        await state.update_data(service_id=service_id)
    
    # Get all stored data
    data = await state.get_data()
    master_id = data.get('master_id')
    service_id = data.get('service_id')
    
    # Get service details
    service = await service_commands.get_service(service_id)
    if not service:
        await callback.message.edit_text(
            "Извините, выбранная услуга больше недоступна.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await state.clear()
        await callback.answer()
        return
    
    # Get master details if available
    master_name = "Не выбран"
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_name = master.get('name', "Не указано")
    
    # Set state to selecting payment
    await state.set_state(BookingStates.selecting_payment)
    
    # Show payment method selection
    confirmation_text = f"""
Подтвердите детали записи:

Услуга: {service['name']}
Цена: {service['price']}
Дата: {date}
Время: {time}
Мастер: {master_name}

Выберите способ оплаты:
"""
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=client_keyboards.get_payment_method_keyboard(service_id, date, time, master_id)
    )
    
    # Answer callback query
    await callback.answer()

async def payment_selected(callback: CallbackQuery, state: FSMContext):
    """Handle payment method selection"""
    # Extract data from callback data
    parts = callback.data.split('_')
    payment_method = parts[1]
    service_id = parts[2]
    date = parts[3]
    time = parts[4]
    
    # Check if master_id is in callback data
    master_id = None
    if len(parts) > 5:
        master_id = parts[5]
    
    # Store payment method in state
    await state.update_data(payment_method=payment_method)
    
    # Set state to confirming
    await state.set_state(BookingStates.confirming)
    
    # Get all stored data
    data = await state.get_data()
    
    # Get service details
    service = await service_commands.get_service(service_id)
    
    # Get master details if available
    master_name = "Не выбран"
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_name = master.get('name', "Не указано")
    
    # Format payment method for display
    payment_display = {
        'cash': 'Наличные',
        'card': 'Карта/Терминал',
        'transfer': 'Перевод'
    }.get(payment_method, payment_method)
    
    # Show confirmation message and keyboard
    confirmation_text = f"""
Пожалуйста, подтвердите вашу запись:

Услуга: {service['name']}
Цена: {service['price']}
Дата: {date}
Время: {time}
Мастер: {master_name}
Способ оплаты: {payment_display}

Нажмите "Подтвердить" для завершения записи.
"""
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=client_keyboards.get_confirmation_keyboard(service_id, date, time, master_id)
    )
    
    # Answer callback query
    await callback.answer()

async def back_to_confirmation(callback: CallbackQuery, state: FSMContext):
    """Handle going back to confirmation"""
    # Extract data from callback data
    parts = callback.data.split('_')
    service_id = parts[2]
    date = parts[3]
    time = parts[4]
    
    # Check if master_id is in callback data
    master_id = None
    if len(parts) > 5:
        master_id = parts[5]
    
    # Set state to selecting payment
    await state.set_state(BookingStates.selecting_payment)
    
    # Get service details
    service = await service_commands.get_service(service_id)
    
    # Get master details if available
    master_name = "Не выбран"
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_name = master.get('name', "Не указано")
    
    # Show payment method selection
    confirmation_text = f"""
Подтвердите детали записи:

Услуга: {service['name']}
Цена: {service['price']}
Дата: {date}
Время: {time}
Мастер: {master_name}

Выберите способ оплаты:
"""
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=client_keyboards.get_payment_method_keyboard(service_id, date, time, master_id)
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
    
    # Check if master_id is in callback data
    master_id = None
    if len(parts) > 4:
        master_id = parts[4]
    
    # Get user ID
    user_id = callback.from_user.id
    
    # Get all stored data
    data = await state.get_data()
    payment_method = data.get('payment_method', 'cash')
    
    # Create appointment
    appointment = await appointment_commands.add_appointment(
        user_id=user_id,
        service_id=service_id,
        date=date,
        time=time,
        master_id=master_id,
        payment_method=payment_method
    )
    
    if appointment:
        # Get service details
        service = await service_commands.get_service(service_id)
        service_name = service['name'] if service else "Услуга"
        
        # Get master details
        master_name = "Не выбран"
        if master_id:
            master = await master_commands.get_master(master_id)
            if master:
                master_name = master.get('name', "Не указано")
        
        await callback.message.edit_text(
            f"✅ Ваша запись подтверждена!\n\nID: {appointment['id']}\nУслуга: {service_name}\nДата: {date}\nВремя: {time}\nМастер: {master_name}\n\nВы можете просмотреть или отменить ваши записи в разделе 'Мои записи'",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Извините, произошла ошибка при записи. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    
    # Clear state
    await state.clear()
    
    # Answer callback query
    await callback.answer()

async def booking_canceled(callback: CallbackQuery, state: FSMContext):
    """Handle booking cancellation"""
    await callback.message.edit_text(
        "Запись отменена. Вы можете начать новую запись через меню.",
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
        "Пожалуйста, выберите дату для записи:",
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
    
    # Get state data
    data = await state.get_data()
    master_id = data.get('master_id')
    service_id = data.get('service_id')
    duration = data.get('duration', 60)
    
    # Set state to selecting time
    await state.set_state(BookingStates.selecting_time)
    
    # Show time selection keyboard
    await callback.message.edit_text(
        f"Выбранная дата: {date}\nПожалуйста, выберите время:",
        reply_markup=client_keyboards.get_time_keyboard(date, master_id, service_id, duration)
    )
    
    # Answer callback query
    await callback.answer()

async def view_my_appointments(callback: CallbackQuery):
    """Handle viewing user's appointments"""
    user_id = callback.from_user.id
    
    # Get user appointments
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    if not appointments:
        await callback.message.edit_text(
            "У вас нет записей.",
            reply_markup=client_keyboards.get_main_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Show appointments
    await callback.message.edit_text(
        "Ваши записи:",
        reply_markup=client_keyboards.get_appointments_keyboard(appointments)
    )
    
    await callback.answer()

async def cmd_appointments(message: Message):
    """Handle the /appointments command"""
    user_id = message.from_user.id
    
    # Get user appointments
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    if not appointments:
        await message.answer(
            "У вас нет записей.",
            reply_markup=client_keyboards.get_main_menu_keyboard()
        )
        return
    
    # Show appointments
    await message.answer(
        "Ваши записи:",
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
            "Извините, эта запись больше недоступна.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Get service details
    service = await service_commands.get_service(appointment["service_id"])
    service_name = "Неизвестная услуга"
    if service:
        service_name = service["name"]
    
    # Get master details if available
    master_name = "Не указан"
    if appointment.get('master_id'):
        master = await master_commands.get_master(appointment['master_id'])
        if master:
            master_name = master.get('name', "Не указано")
    
    # Format status
    status_text = {
        'confirmed': '✅ Подтверждено',
        'canceled': '❌ Отменено',
        'completed': '✓ Выполнено',
        'paid': '💰 Оплачено'
    }.get(appointment.get('status', ''), appointment.get('status', 'Неизвестно'))
    
    # Format payment method
    payment_text = {
        'cash': '💵 Наличные',
        'card': '💳 Карта/Терминал',
        'transfer': '📲 Перевод'
    }.get(appointment.get('payment_method', ''), 'Не указан')
    
    # Show appointment details
    details_text = f"""
Детали записи:

ID: {appointment['id']}
Услуга: {service_name}
Дата: {appointment['date']}
Время: {appointment['time']}
Мастер: {master_name}
Статус: {status_text}
Способ оплаты: {payment_text}
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
            f"✅ Запись {appointment_id} была отменена.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отменить запись. Пожалуйста, попробуйте позже.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
    
    # Answer callback query
    await callback.answer()

async def book_again(callback: CallbackQuery, state: FSMContext):
    """Handle booking again from previous appointment"""
    # Extract appointment ID from callback data
    appointment_id = callback.data.split('_')[2]
    
    # Get appointment details
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Извините, информация о предыдущей записи недоступна.",
            reply_markup=client_keyboards.get_back_to_menu_keyboard()
        )
        await callback.answer()
        return
    
    # Reset state
    await state.clear()
    
    # Store service ID and master ID from previous appointment
    await state.update_data(
        service_id=appointment['service_id'],
        master_id=appointment.get('master_id')
    )
    
    # Set state to selecting date
    await state.set_state(BookingStates.selecting_date)
    
    # Show date selection keyboard
    await callback.message.edit_text(
        "Пожалуйста, выберите дату для новой записи:",
        reply_markup=client_keyboards.get_date_keyboard()
    )
    
    # Answer callback query
    await callback.answer()

async def back_to_menu(callback: CallbackQuery):
    """Handle going back to main menu"""
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=client_keyboards.get_main_menu_keyboard()
    )
    
    # Answer callback query
    await callback.answer()

async def help_callback(callback: CallbackQuery):
    """Handle help button click"""
    help_text = """
Доступные действия:

📅 Записаться на услугу - записаться к мастеру
🗓️ Мои записи - просмотр и управление вашими записями
👨‍💼 Список мастеров - просмотр доступных мастеров
ℹ️ Помощь - показать это сообщение

Если у вас есть вопросы, пожалуйста, обратитесь к администратору.
"""
    await callback.message.edit_text(
        help_text,
        reply_markup=client_keyboards.get_back_to_menu_keyboard()
    )
    
    # Answer callback query
    await callback.answer()

def register_handlers(dp: Dispatcher):
    """Register client handlers"""
    # Command handlers
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))
    dp.message.register(cmd_appointments, Command("appointments"))
    
    # Main menu handlers
    dp.callback_query.register(back_to_menu, F.data == "back_to_menu")
    dp.callback_query.register(start_booking, F.data == "start_booking")
    dp.callback_query.register(view_my_appointments, F.data == "view_my_appointments")
    dp.callback_query.register(view_masters, F.data == "view_masters")
    dp.callback_query.register(help_callback, F.data == "help")
    
    # Master selection handlers
    dp.callback_query.register(master_selected, F.data.startswith("master_"))
    dp.callback_query.register(view_master_info, F.data.startswith("master_"))
    dp.callback_query.register(book_with_master, F.data.startswith("book_with_master_"))
    
    # Booking flow handlers
    dp.callback_query.register(service_selected, F.data.startswith("service_"))
    dp.callback_query.register(date_selected, F.data.startswith("date_"))
    dp.callback_query.register(time_selected, F.data.startswith("time_"))
    dp.callback_query.register(payment_selected, F.data.startswith("payment_"))
    dp.callback_query.register(back_to_confirmation, F.data.startswith("back_to_confirmation_"))
    dp.callback_query.register(booking_confirmed, F.data.startswith("confirm_"))
    dp.callback_query.register(booking_canceled, F.data == "cancel_booking")
    dp.callback_query.register(back_to_dates, F.data == "back_to_dates")
    dp.callback_query.register(back_to_time, F.data.startswith("back_to_time_"))
    
    # Appointment management handlers
    dp.callback_query.register(view_appointment, F.data.startswith("view_appointment_"))
    dp.callback_query.register(cancel_appointment, F.data.startswith("cancel_appointment_"))
    dp.callback_query.register(book_again, F.data.startswith("book_again_"))
