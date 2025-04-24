
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.client_keyboards import (
    get_main_menu_keyboard, get_services_keyboard, get_masters_keyboard,
    get_special_offers_keyboard, get_date_keyboard, get_time_keyboard,
    get_confirmation_keyboard, get_services_by_category_keyboard,
    get_services_in_category_keyboard
)
from utils.db_api import service_commands, master_commands, appointment_commands

# Create router
router = Router()

@router.message(Command("book"))
async def book_command(message: Message):
    """Handle /book command to start booking process"""
    await message.answer(
        "Добро пожаловать в систему записи на услуги. Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "start_booking")
async def start_booking(callback: CallbackQuery):
    """Start the booking process by showing service categories"""
    await callback.answer()
    
    services_by_category = await service_commands.get_services_by_category()
    
    if not services_by_category:
        await callback.message.edit_text(
            "К сожалению, на данный момент нет доступных услуг.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    await callback.message.edit_text(
        "Выберите категорию услуг:",
        reply_markup=get_services_by_category_keyboard(services_by_category)
    )

@router.callback_query(F.data.startswith("category_"))
async def category_selected(callback: CallbackQuery):
    """Handle category selection"""
    await callback.answer()
    
    category_name = callback.data.split("_", 1)[1]
    services_by_category = await service_commands.get_services_by_category()
    
    if category_name not in services_by_category:
        await callback.message.edit_text(
            "Категория не найдена. Пожалуйста, выберите из списка:",
            reply_markup=get_services_by_category_keyboard(services_by_category)
        )
        return
    
    services = services_by_category[category_name]
    
    if not services:
        await callback.message.edit_text(
            f"В категории '{category_name}' нет доступных услуг.",
            reply_markup=get_services_by_category_keyboard(services_by_category)
        )
        return
        
    await callback.message.edit_text(
        f"Выберите услугу из категории '{category_name}':",
        reply_markup=get_services_in_category_keyboard(services, category_name)
    )

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    """Go back to categories list"""
    await callback.answer()
    
    services_by_category = await service_commands.get_services_by_category()
    
    await callback.message.edit_text(
        "Выберите категорию услуг:",
        reply_markup=get_services_by_category_keyboard(services_by_category)
    )

@router.callback_query(F.data.startswith("service_"))
async def service_selected(callback: CallbackQuery):
    """Handle service selection and show available masters"""
    await callback.answer()
    
    service_id = callback.data.split("_")[1]
    service = await service_commands.get_service(service_id)
    
    if not service:
        # Debug information
        await callback.message.edit_text(
            f"Услуга с ID {service_id} не найдена. Пожалуйста, выберите другую услугу.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Store service ID in user data
    callback.bot['temp_data'][callback.from_user.id] = {
        'service_id': service_id
    }
    
    masters = await master_commands.get_all_masters()
    
    if not masters:
        await callback.message.edit_text(
            "К сожалению, нет доступных мастеров.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"Вы выбрали услугу: {service.get('name')} - {service.get('price')}\n\n"
        "Выберите специалиста:",
        reply_markup=get_masters_keyboard(masters)
    )

@router.callback_query(F.data.startswith("master_"))
async def master_selected(callback: CallbackQuery):
    """Handle master selection and show special offers or dates"""
    await callback.answer()
    
    master_id = callback.data.split("_")[1]
    master = await master_commands.get_master(master_id)
    
    if not master:
        await callback.message.edit_text(
            "Мастер не найден. Пожалуйста, выберите из списка:",
            reply_markup=get_masters_keyboard(await master_commands.get_all_masters())
        )
        return
    
    # Store master ID in user data
    if callback.from_user.id not in callback.bot['temp_data']:
        callback.bot['temp_data'][callback.from_user.id] = {}
    callback.bot['temp_data'][callback.from_user.id]['master_id'] = master_id
    
    # Check for special offers
    offers = await service_commands.get_all_offers()
    
    if offers:
        await callback.message.edit_text(
            f"Вы выбрали мастера: {master.get('name')}\n\n"
            "У нас есть специальные предложения. Хотите выбрать одно из них?",
            reply_markup=get_special_offers_keyboard(offers, master_id)
        )
    else:
        # No offers, show dates directly
        await show_dates(callback)

@router.callback_query(F.data.startswith("offer_"))
async def offer_selected(callback: CallbackQuery):
    """Handle special offer selection"""
    await callback.answer()
    
    # Parse offer_id and master_id from callback data
    parts = callback.data.split("_")
    offer_id = parts[1]
    master_id = parts[2] if len(parts) > 2 else None
    
    offer = await service_commands.get_offer(offer_id)
    
    if not offer:
        # Debug information
        await callback.message.edit_text(
            f"Спецпредложение с ID {offer_id} не найдено. Пожалуйста, выберите другое.",
            reply_markup=get_special_offers_keyboard(await service_commands.get_all_offers(), master_id)
        )
        return
    
    # Store offer ID instead of service ID in user data
    if callback.from_user.id not in callback.bot['temp_data']:
        callback.bot['temp_data'][callback.from_user.id] = {}
    
    callback.bot['temp_data'][callback.from_user.id]['service_id'] = offer_id
    callback.bot['temp_data'][callback.from_user.id]['is_offer'] = True
    
    # Show dates for booking
    await show_dates(callback)

@router.callback_query(F.data.startswith("skip_offers_"))
async def skip_offers(callback: CallbackQuery):
    """Skip offers and show dates for booking"""
    await callback.answer()
    
    # Extract master_id from callback data
    master_id = callback.data.split("_")[2]
    
    # Update user data with master ID if not already set
    if callback.from_user.id not in callback.bot['temp_data']:
        callback.bot['temp_data'][callback.from_user.id] = {}
    
    if 'master_id' not in callback.bot['temp_data'][callback.from_user.id]:
        callback.bot['temp_data'][callback.from_user.id]['master_id'] = master_id
    
    await show_dates(callback)

async def show_dates(callback: CallbackQuery):
    """Show available dates for booking"""
    # Ensure user has selected a service
    if (callback.from_user.id not in callback.bot['temp_data'] or 
            'service_id' not in callback.bot['temp_data'][callback.from_user.id]):
        await callback.message.edit_text(
            "Пожалуйста, сначала выберите услугу.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Get service or offer information
    user_data = callback.bot['temp_data'][callback.from_user.id]
    is_offer = user_data.get('is_offer', False)
    service_id = user_data['service_id']
    
    if is_offer:
        service = await service_commands.get_offer(service_id)
        service_type = "спецпредложение"
    else:
        service = await service_commands.get_service(service_id)
        service_type = "услугу"
    
    if not service:
        await callback.message.edit_text(
            f"Выбранное {service_type} не найдено. Пожалуйста, начните сначала.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Get master information
    master_id = user_data.get('master_id')
    master_info = ""
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_info = f"\nМастер: {master.get('name')}"
    
    await callback.message.edit_text(
        f"Вы выбрали {service_type}: {service.get('name')} - {service.get('price')}{master_info}\n\n"
        "Выберите дату посещения:",
        reply_markup=get_date_keyboard()
    )

@router.callback_query(F.data.startswith("date_"))
async def date_selected(callback: CallbackQuery):
    """Handle date selection and show available time slots"""
    await callback.answer()
    
    date = callback.data.split("_")[1]
    
    # Ensure user has selected a service
    if (callback.from_user.id not in callback.bot['temp_data'] or 
            'service_id' not in callback.bot['temp_data'][callback.from_user.id]):
        await callback.message.edit_text(
            "Пожалуйста, сначала выберите услугу.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Store date in user data
    callback.bot['temp_data'][callback.from_user.id]['date'] = date
    
    # Get service or offer information for duration
    user_data = callback.bot['temp_data'][callback.from_user.id]
    is_offer = user_data.get('is_offer', False)
    service_id = user_data['service_id']
    master_id = user_data.get('master_id')
    
    if is_offer:
        service = await service_commands.get_offer(service_id)
    else:
        service = await service_commands.get_service(service_id)
    
    # Default duration if service not found
    duration = 60
    if service:
        duration = service.get('duration', 60)
    
    await callback.message.edit_text(
        f"Вы выбрали дату: {date}\n\nТеперь выберите удобное время:",
        reply_markup=get_time_keyboard(date, master_id, service_id, duration)
    )

@router.callback_query(F.data == "back_to_dates")
async def back_to_dates(callback: CallbackQuery):
    """Go back to date selection"""
    await callback.answer()
    
    # Call show_dates to display date selection again
    await show_dates(callback)

@router.callback_query(F.data.startswith("time_"))
async def time_selected(callback: CallbackQuery):
    """Handle time selection and show booking confirmation"""
    await callback.answer()
    
    # Parse time callback data
    parts = callback.data.split("_")
    date = parts[1]
    time_slot = parts[2]
    
    # Optional master_id and service_id in callback
    master_id = parts[3] if len(parts) > 3 else None
    service_id = parts[4] if len(parts) > 4 else None
    
    # Store time in user data
    if callback.from_user.id not in callback.bot['temp_data']:
        callback.bot['temp_data'][callback.from_user.id] = {}
    
    user_data = callback.bot['temp_data'][callback.from_user.id]
    user_data['time'] = time_slot
    
    if 'date' not in user_data:
        user_data['date'] = date
    
    if master_id and 'master_id' not in user_data:
        user_data['master_id'] = master_id
    
    if service_id and 'service_id' not in user_data:
        user_data['service_id'] = service_id
    
    # Get service or offer information
    is_offer = user_data.get('is_offer', False)
    service_id = user_data.get('service_id')
    
    if not service_id:
        await callback.message.edit_text(
            "Произошла ошибка. Пожалуйста, начните запись сначала.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    if is_offer:
        service = await service_commands.get_offer(service_id)
        service_type = "спецпредложение"
    else:
        service = await service_commands.get_service(service_id)
        service_type = "услугу"
    
    if not service:
        await callback.message.edit_text(
            f"Выбранное {service_type} не найдено. Пожалуйста, начните сначала.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Get master information
    master_id = user_data.get('master_id')
    master_info = ""
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_info = f"\nМастер: {master.get('name')}"
    
    # Show booking confirmation
    await callback.message.edit_text(
        f"Пожалуйста, подтвердите запись:\n\n"
        f"{service_type.capitalize()}: {service.get('name')}\n"
        f"Цена: {service.get('price')}\n"
        f"Дата: {date}\n"
        f"Время: {time_slot}{master_info}",
        reply_markup=get_confirmation_keyboard(service_id, date, time_slot, master_id)
    )

@router.callback_query(F.data.startswith("confirm_"))
async def confirm_booking(callback: CallbackQuery):
    """Handle booking confirmation"""
    await callback.answer()
    
    # Parse confirmation callback data
    parts = callback.data.split("_")
    service_id = parts[1]
    date = parts[2]
    time_slot = parts[3]
    master_id = parts[4] if len(parts) > 4 else None
    
    user_id = callback.from_user.id
    user_data = callback.bot['temp_data'].get(user_id, {})
    is_offer = user_data.get('is_offer', False)
    
    # Add appointment to database
    try:
        appointment = await appointment_commands.add_appointment(
            user_id=user_id,
            service_id=service_id,
            date=date,
            time=time_slot,
            master_id=master_id
        )
        
        # Get service or offer information
        if is_offer:
            service = await service_commands.get_offer(service_id)
            service_type = "спецпредложение"
        else:
            service = await service_commands.get_service(service_id)
            service_type = "услугу"
        
        # Check if user is verified
        is_verified = await appointment_commands.is_user_verified(user_id)
        
        if is_verified:
            status_text = "подтверждена"
        else:
            status_text = "отправлена на подтверждение"
        
        # Get master information
        master_info = ""
        if master_id:
            master = await master_commands.get_master(master_id)
            if master:
                master_info = f"\nМастер: {master.get('name')}"
                
                # Send notification to master
                try:
                    master_telegram_id = master.get('telegram_id')
                    if master_telegram_id:
                        await callback.bot.send_message(
                            master_telegram_id,
                            f"📅 Новая запись!\n\n"
                            f"Клиент: {callback.from_user.full_name} (@{callback.from_user.username})\n"
                            f"Услуга: {service.get('name')}\n"
                            f"Дата: {date}\n"
                            f"Время: {time_slot}\n"
                            f"Статус: {status_text}"
                        )
                except Exception as e:
                    print(f"Ошибка отправки уведомления мастеру: {e}")
        
        # Send notification to admin
        try:
            admin_id = callback.bot['config'].admin_id
            if admin_id:
                verification_markup = None
                if not is_verified:
                    from aiogram.utils.keyboard import InlineKeyboardBuilder
                    verify_keyboard = InlineKeyboardBuilder()
                    verify_keyboard.button(
                        text="✅ Подтвердить клиента",
                        callback_data=f"verify_user_{user_id}"
                    )
                    verify_keyboard.button(
                        text="❌ Отклонить запись",
                        callback_data=f"reject_booking_{appointment['id']}"
                    )
                    verify_keyboard.adjust(1)
                    verification_markup = verify_keyboard.as_markup()
                
                await callback.bot.send_message(
                    admin_id,
                    f"📅 Новая запись!\n\n"
                    f"Клиент: {callback.from_user.full_name} (@{callback.from_user.username})\n"
                    f"Услуга: {service.get('name')}\n"
                    f"Дата: {date}\n"
                    f"Время: {time_slot}{master_info}\n"
                    f"Статус: {status_text}",
                    reply_markup=verification_markup
                )
        except Exception as e:
            print(f"Ошибка отправки уведомления админу: {e}")
        
        # Clear temporary data
        if user_id in callback.bot['temp_data']:
            del callback.bot['temp_data'][user_id]
        
        # Show success message
        await callback.message.edit_text(
            f"✅ Ваша запись {status_text}!\n\n"
            f"{service_type.capitalize()}: {service.get('name')}\n"
            f"Цена: {service.get('price')}\n"
            f"Дата: {date}\n"
            f"Время: {time_slot}{master_info}\n\n"
            f"Статус: {status_text}",
            reply_markup=get_main_menu_keyboard()
        )
        
    except Exception as e:
        # Show error message
        await callback.message.edit_text(
            f"❌ Произошла ошибка при создании записи: {str(e)}\n\n"
            "Пожалуйста, попробуйте еще раз или свяжитесь с администратором.",
            reply_markup=get_main_menu_keyboard()
        )

@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: CallbackQuery):
    """Cancel the current booking process"""
    await callback.answer()
    
    # Clear temporary data
    if callback.from_user.id in callback.bot['temp_data']:
        del callback.bot['temp_data'][callback.from_user.id]
    
    await callback.message.edit_text(
        "❌ Запись отменена.",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Return to the main menu"""
    await callback.answer()
    
    # Clear temporary data
    if callback.from_user.id in callback.bot['temp_data']:
        del callback.bot['temp_data'][callback.from_user.id]
    
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_main_menu_keyboard()
    )

@router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """Show help information"""
    await callback.answer()
    
    help_text = (
        "📝 *Как пользоваться сервисом записи:*\n\n"
        "1. Нажмите 'Записаться на услугу'\n"
        "2. Выберите категорию и услугу\n"
        "3. Выберите мастера\n"
        "4. Выберите дату и время\n"
        "5. Подтвердите запись\n\n"
        "📋 *Управление записями:*\n\n"
        "• Чтобы просмотреть свои записи, нажмите 'Мои записи'\n"
        "• Вы можете отменить запись не позднее чем за 24 часа\n\n"
        "📞 *Если возникли вопросы:*\n\n"
        "Свяжитесь с администратором через контакты в описании бота"
    )
    
    await callback.message.edit_text(
        help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

# View my appointments handlers
@router.callback_query(F.data == "view_my_appointments")
async def view_my_appointments(callback: CallbackQuery):
    """Show user's appointments"""
    await callback.answer()
    
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    if not appointments:
        await callback.message.edit_text(
            "У вас пока нет записей.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    from keyboards.client_keyboards import get_active_appointments_keyboard
    
    await callback.message.edit_text(
        "Ваши записи:",
        reply_markup=get_active_appointments_keyboard(appointments)
    )

@router.callback_query(F.data.startswith("active_page_"))
async def active_appointments_page(callback: CallbackQuery):
    """Handle pagination for active appointments"""
    await callback.answer()
    
    page = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    from keyboards.client_keyboards import get_active_appointments_keyboard
    
    await callback.message.edit_text(
        "Ваши активные записи:",
        reply_markup=get_active_appointments_keyboard(appointments, page)
    )

@router.callback_query(F.data == "filter_active")
async def filter_active_appointments(callback: CallbackQuery):
    """Show only active appointments"""
    await callback.answer()
    
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    from keyboards.client_keyboards import get_active_appointments_keyboard
    
    await callback.message.edit_text(
        "Ваши активные записи:",
        reply_markup=get_active_appointments_keyboard(appointments)
    )

@router.callback_query(F.data == "filter_all")
async def filter_all_appointments(callback: CallbackQuery):
    """Show all appointments"""
    await callback.answer()
    
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    from keyboards.client_keyboards import get_all_appointments_keyboard
    
    await callback.message.edit_text(
        "Все ваши записи:",
        reply_markup=get_all_appointments_keyboard(appointments)
    )

@router.callback_query(F.data.startswith("all_page_"))
async def all_appointments_page(callback: CallbackQuery):
    """Handle pagination for all appointments"""
    await callback.answer()
    
    page = int(callback.data.split("_")[2])
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    from keyboards.client_keyboards import get_all_appointments_keyboard
    
    await callback.message.edit_text(
        "Все ваши записи:",
        reply_markup=get_all_appointments_keyboard(appointments, page)
    )

@router.callback_query(F.data.startswith("expand_date_"))
async def expand_date_appointments(callback: CallbackQuery):
    """Expand appointments for a specific date"""
    await callback.answer()
    
    date = callback.data.split("_", 2)[2]
    user_id = callback.from_user.id
    appointments = await appointment_commands.get_user_appointments(user_id)
    
    # Filter appointments by date
    date_appointments = [a for a in appointments if a.get('date') == date]
    
    from keyboards.client_keyboards import get_date_appointments_keyboard
    
    await callback.message.edit_text(
        f"Ваши записи на {date}:",
        reply_markup=get_date_appointments_keyboard(date_appointments, date)
    )

@router.callback_query(F.data.startswith("view_appointment_"))
async def view_appointment_details(callback: CallbackQuery):
    """View details of a specific appointment"""
    await callback.answer()
    
    appointment_id = callback.data.split("_")[2]
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Запись не найдена.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Get service info
    service_id = appointment.get('service_id')
    service = await service_commands.get_service(service_id)
    
    service_info = "Услуга: Информация недоступна"
    if service:
        service_info = f"Услуга: {service.get('name')} - {service.get('price')}"
    
    # Get master info
    master_info = ""
    master_id = appointment.get('master_id')
    if master_id:
        master = await master_commands.get_master(master_id)
        if master:
            master_info = f"Мастер: {master.get('name')}\n"
    
    # Format status
    status_text = {
        'confirmed': '✅ Подтверждено',
        'canceled': '❌ Отменено',
        'completed': '✓ Выполнено',
        'paid': '💰 Оплачено',
        'pending': '⏳ Ожидает подтверждения'
    }.get(appointment.get('status'), 'Неизвестно')
    
    from keyboards.client_keyboards import get_appointment_actions_keyboard
    
    await callback.message.edit_text(
        f"📝 Детали записи:\n\n"
        f"{service_info}\n"
        f"Дата: {appointment.get('date')}\n"
        f"Время: {appointment.get('time')}\n"
        f"{master_info}"
        f"Статус: {status_text}",
        reply_markup=get_appointment_actions_keyboard(appointment)
    )

@router.callback_query(F.data.startswith("cancel_appointment_"))
async def cancel_appointment(callback: CallbackQuery):
    """Cancel an appointment"""
    await callback.answer()
    
    appointment_id = callback.data.split("_")[2]
    result = await appointment_commands.cancel_appointment(appointment_id)
    
    if result:
        await callback.message.edit_text(
            "✅ Запись успешно отменена.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "❌ Не удалось отменить запись. Возможно, она уже отменена или завершена.",
            reply_markup=get_main_menu_keyboard()
        )

@router.callback_query(F.data.startswith("book_again_"))
async def book_again(callback: CallbackQuery):
    """Book same service again"""
    await callback.answer()
    
    appointment_id = callback.data.split("_")[2]
    appointment = await appointment_commands.get_appointment(appointment_id)
    
    if not appointment:
        await callback.message.edit_text(
            "Запись не найдена.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Store service ID in user data
    service_id = appointment.get('service_id')
    if service_id:
        if callback.from_user.id not in callback.bot['temp_data']:
            callback.bot['temp_data'][callback.from_user.id] = {}
        
        callback.bot['temp_data'][callback.from_user.id]['service_id'] = service_id
        
        # Also store master ID if available
        master_id = appointment.get('master_id')
        if master_id:
            callback.bot['temp_data'][callback.from_user.id]['master_id'] = master_id
    
    # Show dates for new booking
    await show_dates(callback)

# Master list handling
@router.callback_query(F.data == "view_masters")
async def view_masters(callback: CallbackQuery):
    """Show list of masters"""
    await callback.answer()
    
    masters = await master_commands.get_all_masters()
    
    if not masters:
        await callback.message.edit_text(
            "К сожалению, нет доступных мастеров.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    await callback.message.edit_text(
        "Выберите мастера для просмотра информации:",
        reply_markup=get_masters_keyboard(masters)
    )

@router.callback_query(F.data.startswith("view_master_"))
async def view_master_info(callback: CallbackQuery):
    """View master information"""
    await callback.answer()
    
    master_id = callback.data.split("_")[2]
    master = await master_commands.get_master(master_id)
    
    if not master:
        await callback.message.edit_text(
            "Мастер не найден.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    from keyboards.client_keyboards import get_master_info_keyboard
    
    # Get master's specialties
    specialties = master.get('specialties', '')
    if specialties:
        specialties_text = f"Специализация: {specialties}\n"
    else:
        specialties_text = ""
    
    # Get master's description
    description = master.get('description', '')
    if description:
        description_text = f"{description}\n\n"
    else:
        description_text = ""
    
    await callback.message.edit_text(
        f"👨‍💼 {master.get('name')}\n\n"
        f"{description_text}"
        f"{specialties_text}",
        reply_markup=get_master_info_keyboard(master)
    )
