
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import datetime
import logging
import re
from utils.db_api import finance_commands, service_commands, user_commands, appointment_commands
from keyboards import finance_keyboards

router = Router()

# Определяем состояния для финансовой аналитики
class FinanceStates(StatesGroup):
    setup_materials = State()
    setup_rent = State()
    setup_salary = State()
    setup_other = State()
    
    edit_material_cost = State()
    edit_time_cost = State()
    edit_other_cost = State()
    
    add_client_note = State()
    
    enter_custom_start_date = State()
    enter_custom_end_date = State()

# Обработка команд финансового меню
@router.callback_query(F.data == "finance_menu")
async def show_finance_menu(callback: types.CallbackQuery):
    """Show finance main menu"""
    # Проверяем роль пользователя (только admin)
    user = await user_commands.get_user(callback.from_user.id)
    if not user or user.get("role", "") != "admin":
        await callback.answer("Доступ только для администраторов", show_alert=True)
        return
    
    keyboard = await finance_keyboards.get_finance_main_menu()
    await callback.message.edit_text(
        "📊 *Финансы и аналитика*\n\n"
        "Добро пожаловать в раздел управления финансами. "
        "Здесь вы можете отслеживать доходы, расходы, анализировать "
        "прибыльность услуг и получать персонализированные рекомендации.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработка возврата в финансовое меню
@router.callback_query(F.data == "back_to_finance")
async def back_to_finance(callback: types.CallbackQuery):
    """Return to finance menu"""
    await show_finance_menu(callback)

# Обработка меню доходов и прибыли
@router.callback_query(F.data == "finance_income")
async def show_finance_income(callback: types.CallbackQuery):
    """Show finance income menu"""
    keyboard = await finance_keyboards.get_finance_period_menu()
    await callback.message.edit_text(
        "📊 *Доход и прибыль*\n\n"
        "Выберите период для анализа доходов и прибыли:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработка выбора периода
@router.callback_query(F.data.startswith("finance_period_"))
async def handle_finance_period(callback: types.CallbackQuery):
    """Handle finance period selection"""
    period = callback.data.replace("finance_period_", "")
    
    # Получаем текущую дату
    today = datetime.datetime.now().date()
    
    # Определяем период в зависимости от выбора
    if period == "today":
        start_date = today.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "сегодня"
    elif period == "yesterday":
        yesterday = today - datetime.timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d")
        end_date = yesterday.strftime("%Y-%m-%d")
        period_name = "вчера"
    elif period == "week":
        # Неделя начинается с понедельника
        start_date = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "текущую неделю"
    elif period == "month":
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "текущий месяц"
    elif period == "30days":
        start_date = (today - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        period_name = "последние 30 дней"
    elif period == "custom":
        # Запросим пользовательский период
        await callback.message.edit_text(
            "Введите начальную дату периода в формате ГГГГ-ММ-ДД (например, 2023-01-01):"
        )
        await callback.answer()
        
        # Устанавливаем состояние для последующего ввода дат
        state = FSMContext(callback.bot, callback.from_user.id, {"user_id": callback.from_user.id})
        await state.set_state(FinanceStates.enter_custom_start_date)
        return
    
    # Получаем данные за выбранный период
    analytics = await finance_commands.get_analytics_period(callback.from_user.id, start_date, end_date)
    
    if not analytics or len(analytics.get("daily_data", [])) == 0:
        await callback.message.edit_text(
            f"📊 *Доход и прибыль за {period_name}*\n\n"
            f"За выбранный период нет данных. Пожалуйста, выберите другой период или "
            f"внесите данные о доходах и расходах.",
            reply_markup=await finance_keyboards.get_finance_period_menu(),
            parse_mode="Markdown"
        )
    else:
        message = f"📊 *Доход и прибыль за {period_name}*\n\n"
        message += f"🔸 Общий доход: {analytics['total_income']} руб.\n"
        message += f"🔸 Общие расходы: {analytics['total_expenses']} руб.\n"
        message += f"🔸 Чистая прибыль: {analytics['total_profit']} руб.\n"
        message += f"🔸 Количество записей: {analytics['total_appointments']}\n"
        
        # Если есть данные по дням и их больше 1, добавляем статистику по дням
        if len(analytics["daily_data"]) > 1:
            message += "\n*Статистика по дням:*\n"
            
            # Сортируем дни по дате
            sorted_days = sorted(analytics["daily_data"], key=lambda x: x["date"])
            
            for day_data in sorted_days[:5]:  # Показываем только первые 5 дней для краткости
                day_date = datetime.datetime.strptime(day_data["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
                message += f"\n{day_date}:\n"
                message += f"- Доход: {day_data['total_income']} руб.\n"
                message += f"- Прибыль: {day_data['profit']} руб.\n"
            
            # Если дней больше 5, добавляем сообщение
            if len(analytics["daily_data"]) > 5:
                message += f"\n... и еще {len(analytics['daily_data']) - 5} дней."
        
        await callback.message.edit_text(
            message,
            reply_markup=await finance_keyboards.get_finance_period_menu(),
            parse_mode="Markdown"
        )
    
    await callback.answer()

# Обработка ввода начальной даты для пользовательского периода
@router.message(StateFilter(FinanceStates.enter_custom_start_date))
async def process_custom_start_date(message: types.Message, state: FSMContext):
    """Process custom start date input"""
    # Проверяем формат даты
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", message.text):
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (например, 2023-01-01):")
        return
    
    # Сохраняем начальную дату
    await state.update_data(start_date=message.text)
    
    await message.answer("Теперь введите конечную дату периода в формате ГГГГ-ММ-ДД (например, 2023-01-31):")
    await state.set_state(FinanceStates.enter_custom_end_date)

# Обработка ввода конечной даты для пользовательского периода
@router.message(StateFilter(FinanceStates.enter_custom_end_date))
async def process_custom_end_date(message: types.Message, state: FSMContext):
    """Process custom end date input"""
    # Проверяем формат даты
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", message.text):
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (например, 2023-01-31):")
        return
    
    # Получаем сохраненную начальную дату
    data = await state.get_data()
    start_date = data.get("start_date")
    end_date = message.text
    
    # Сбрасываем состояние
    await state.clear()
    
    # Получаем данные за выбранный период
    analytics = await finance_commands.get_analytics_period(message.from_user.id, start_date, end_date)
    
    if not analytics or len(analytics.get("daily_data", [])) == 0:
        await message.answer(
            f"📊 *Доход и прибыль за период с {start_date} по {end_date}*\n\n"
            f"За выбранный период нет данных. Пожалуйста, выберите другой период или "
            f"внесите данные о доходах и расходах.",
            reply_markup=await finance_keyboards.get_finance_period_menu(),
            parse_mode="Markdown"
        )
    else:
        message_text = f"📊 *Доход и прибыль за период с {start_date} по {end_date}*\n\n"
        message_text += f"🔸 Общий доход: {analytics['total_income']} руб.\n"
        message_text += f"🔸 Общие расходы: {analytics['total_expenses']} руб.\n"
        message_text += f"🔸 Чистая прибыль: {analytics['total_profit']} руб.\n"
        message_text += f"🔸 Количество записей: {analytics['total_appointments']}\n"
        
        # Если есть данные по дням и их больше 1, добавляем статистику по дням
        if len(analytics["daily_data"]) > 1:
            message_text += "\n*Статистика по дням:*\n"
            
            # Сортируем дни по дате
            sorted_days = sorted(analytics["daily_data"], key=lambda x: x["date"])
            
            for day_data in sorted_days[:5]:  # Показываем только первые 5 дней для краткости
                day_date = datetime.datetime.strptime(day_data["date"], "%Y-%m-%d").strftime("%d.%m.%Y")
                message_text += f"\n{day_date}:\n"
                message_text += f"- Доход: {day_data['total_income']} руб.\n"
                message_text += f"- Прибыль: {day_data['profit']} руб.\n"
            
            # Если дней больше 5, добавляем сообщение
            if len(analytics["daily_data"]) > 5:
                message_text += f"\n... и еще {len(analytics['daily_data']) - 5} дней."
        
        await message.answer(
            message_text,
            reply_markup=await finance_keyboards.get_finance_period_menu(),
            parse_mode="Markdown"
        )

# Обработка меню "Расходы на услуги"
@router.callback_query(F.data == "finance_services")
async def show_finance_services(callback: types.CallbackQuery):
    """Show finance services menu"""
    # Получаем список услуг
    services = await service_commands.get_all_services()
    
    if not services:
        await callback.message.edit_text(
            "📋 *Расходы на услуги*\n\n"
            "У вас еще нет созданных услуг. Пожалуйста, сначала создайте услуги.",
            reply_markup=await finance_keyboards.get_back_to_finance_keyboard(),
            parse_mode="Markdown"
        )
    else:
        keyboard = await finance_keyboards.get_finance_services_menu(services)
        
        await callback.message.edit_text(
            "📋 *Расходы на услуги*\n\n"
            "Выберите услугу для просмотра и редактирования информации о расходах:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback.answer()

# Обработка выбора услуги
@router.callback_query(F.data.startswith("finance_service_"))
async def show_service_costs(callback: types.CallbackQuery):
    """Show service costs"""
    service_id = callback.data.replace("finance_service_", "")
    
    # Получаем данные услуги
    service = await service_commands.get_service(service_id)
    if not service:
        await callback.answer("Услуга не найдена", show_alert=True)
        return
    
    # Получаем расходы на услугу
    costs = await finance_commands.get_service_costs(service_id)
    
    # Получаем прибыль
    profit_data = await finance_commands.calculate_service_profit(service_id)
    
    message = f"📋 *{service['name']}*\n\n"
    message += f"💵 Цена услуги: {service['price']} руб.\n\n"
    
    message += f"*Расходы:*\n"
    message += f"🔹 Материалы: {costs['materials_cost']} руб.\n"
    message += f"🔹 Время: {costs['time_cost']} руб.\n"
    message += f"🔹 Другие расходы: {costs['other_costs']} руб.\n"
    
    total_cost = float(costs['materials_cost']) + float(costs['time_cost']) + float(costs['other_costs'])
    message += f"🔹 *Общие расходы: {total_cost} руб.*\n\n"
    
    if profit_data:
        message += f"*Прибыльность:*\n"
        message += f"💰 Прибыль с услуги: {profit_data['profit']} руб.\n"
        message += f"📊 Маржа: {profit_data['margin_percent']}%\n"
    
    # Добавляем кнопки для редактирования расходов
    keyboard = await finance_keyboards.get_finance_service_cost_menu(service_id)
    
    await callback.message.edit_text(
        message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка редактирования стоимости материалов
@router.callback_query(F.data.startswith("edit_material_cost_"))
async def edit_material_cost(callback: types.CallbackQuery, state: FSMContext):
    """Edit material cost"""
    service_id = callback.data.replace("edit_material_cost_", "")
    
    # Сохраняем ID услуги в состоянии
    await state.update_data(service_id=service_id)
    
    # Получаем текущие расходы
    costs = await finance_commands.get_service_costs(service_id)
    
    await callback.message.edit_text(
        f"Введите стоимость материалов для услуги (текущее значение: {costs['materials_cost']} руб.):"
    )
    
    await state.set_state(FinanceStates.edit_material_cost)
    await callback.answer()

# Обработка редактирования стоимости времени
@router.callback_query(F.data.startswith("edit_time_cost_"))
async def edit_time_cost(callback: types.CallbackQuery, state: FSMContext):
    """Edit time cost"""
    service_id = callback.data.replace("edit_time_cost_", "")
    
    # Сохраняем ID услуги в состоянии
    await state.update_data(service_id=service_id)
    
    # Получаем текущие расходы
    costs = await finance_commands.get_service_costs(service_id)
    
    await callback.message.edit_text(
        f"Введите стоимость времени для услуги (текущее значение: {costs['time_cost']} руб.):"
    )
    
    await state.set_state(FinanceStates.edit_time_cost)
    await callback.answer()

# Обработка редактирования других расходов
@router.callback_query(F.data.startswith("edit_other_cost_"))
async def edit_other_cost(callback: types.CallbackQuery, state: FSMContext):
    """Edit other costs"""
    service_id = callback.data.replace("edit_other_cost_", "")
    
    # Сохраняем ID услуги в состоянии
    await state.update_data(service_id=service_id)
    
    # Получаем текущие расходы
    costs = await finance_commands.get_service_costs(service_id)
    
    await callback.message.edit_text(
        f"Введите другие расходы для услуги (текущее значение: {costs['other_costs']} руб.):"
    )
    
    await state.set_state(FinanceStates.edit_other_cost)
    await callback.answer()

# Обработка ввода стоимости материалов
@router.message(StateFilter(FinanceStates.edit_material_cost))
async def process_material_cost(message: types.Message, state: FSMContext):
    """Process material cost input"""
    try:
        cost = float(message.text)
        
        # Получаем ID услуги из состояния
        data = await state.get_data()
        service_id = data.get("service_id")
        
        # Получаем текущие расходы
        costs = await finance_commands.get_service_costs(service_id)
        
        # Обновляем стоимость материалов
        await finance_commands.add_service_costs(
            service_id,
            cost,
            costs["time_cost"],
            costs["other_costs"]
        )
        
        await message.answer("✅ Стоимость материалов успешно обновлена.")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Возвращаемся к просмотру расходов на услугу
        callback = types.CallbackQuery(
            id="1",
            from_user=message.from_user,
            chat_instance="1",
            message=message,
            data=f"finance_service_{service_id}"
        )
        
        await show_service_costs(callback)
        
    except ValueError:
        await message.answer("Ошибка: введите числовое значение (например, 100 или 150.50):")

# Обработка ввода стоимости времени
@router.message(StateFilter(FinanceStates.edit_time_cost))
async def process_time_cost(message: types.Message, state: FSMContext):
    """Process time cost input"""
    try:
        cost = float(message.text)
        
        # Получаем ID услуги из состояния
        data = await state.get_data()
        service_id = data.get("service_id")
        
        # Получаем текущие расходы
        costs = await finance_commands.get_service_costs(service_id)
        
        # Обновляем стоимость времени
        await finance_commands.add_service_costs(
            service_id,
            costs["materials_cost"],
            cost,
            costs["other_costs"]
        )
        
        await message.answer("✅ Стоимость времени успешно обновлена.")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Возвращаемся к просмотру расходов на услугу
        callback = types.CallbackQuery(
            id="1",
            from_user=message.from_user,
            chat_instance="1",
            message=message,
            data=f"finance_service_{service_id}"
        )
        
        await show_service_costs(callback)
        
    except ValueError:
        await message.answer("Ошибка: введите числовое значение (например, 100 или 150.50):")

# Обработка ввода других расходов
@router.message(StateFilter(FinanceStates.edit_other_cost))
async def process_other_cost(message: types.Message, state: FSMContext):
    """Process other costs input"""
    try:
        cost = float(message.text)
        
        # Получаем ID услуги из состояния
        data = await state.get_data()
        service_id = data.get("service_id")
        
        # Получаем текущие расходы
        costs = await finance_commands.get_service_costs(service_id)
        
        # Обновляем другие расходы
        await finance_commands.add_service_costs(
            service_id,
            costs["materials_cost"],
            costs["time_cost"],
            cost
        )
        
        await message.answer("✅ Другие расходы успешно обновлены.")
        
        # Сбрасываем состояние
        await state.clear()
        
        # Возвращаемся к просмотру расходов на услугу
        callback = types.CallbackQuery(
            id="1",
            from_user=message.from_user,
            chat_instance="1",
            message=message,
            data=f"finance_service_{service_id}"
        )
        
        await show_service_costs(callback)
        
    except ValueError:
        await message.answer("Ошибка: введите числовое значение (например, 100 или 150.50):")

# Обработка возврата к списку услуг
@router.callback_query(F.data == "back_to_finance_services")
async def back_to_finance_services(callback: types.CallbackQuery):
    """Return to finance services menu"""
    await show_finance_services(callback)

# Обработка меню "Статистика клиентов"
@router.callback_query(F.data == "finance_clients")
async def show_finance_clients(callback: types.CallbackQuery):
    """Show finance clients menu"""
    keyboard = await finance_keyboards.get_finance_clients_menu()
    
    await callback.message.edit_text(
        "👥 *Статистика клиентов*\n\n"
        "Выберите тип статистики для анализа:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка возврата к меню статистики клиентов
@router.callback_query(F.data == "back_to_finance_clients")
async def back_to_finance_clients(callback: types.CallbackQuery):
    """Return to finance clients menu"""
    await show_finance_clients(callback)

# Обработка меню "VIP клиенты"
@router.callback_query(F.data == "finance_vip_clients")
async def show_finance_vip_clients(callback: types.CallbackQuery):
    """Show VIP clients"""
    # Получаем список VIP клиентов
    vip_clients = await finance_commands.get_vip_clients()
    
    if not vip_clients:
        await callback.message.edit_text(
            "👑 *VIP клиенты*\n\n"
            "У вас пока нет VIP клиентов. VIP-статус присваивается автоматически клиентам, "
            "которые совершили более 10 визитов или потратили более 15 000 рублей.",
            reply_markup=await finance_keyboards.get_back_to_finance_clients_keyboard(),
            parse_mode="Markdown"
        )
    else:
        keyboard = await finance_keyboards.get_vip_clients_menu(vip_clients)
        
        message = "👑 *VIP клиенты*\n\n"
        message += "Список ваших VIP клиентов:\n\n"
        
        for i, client in enumerate(vip_clients[:5], 1):
            message += f"{i}. {client['name']}\n"
            message += f"   Визитов: {client['total_visits']}, Потрачено: {client['total_spent']} руб.\n\n"
        
        if len(vip_clients) > 5:
            message += f"... и еще {len(vip_clients) - 5} клиентов\n\n"
        
        message += "Выберите клиента для просмотра подробной информации:"
        
        await callback.message.edit_text(
            message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    
    await callback.answer()

# Обработка возврата к VIP клиентам
@router.callback_query(F.data == "back_to_finance_vip")
async def back_to_finance_vip(callback: types.CallbackQuery):
    """Return to VIP clients menu"""
    await show_finance_vip_clients(callback)

# Обработка выбора клиента
@router.callback_query(F.data.startswith("finance_client_"))
async def show_client_stats(callback: types.CallbackQuery):
    """Show client statistics"""
    client_id = callback.data.replace("finance_client_", "")
    
    # Получаем данные о клиенте
    client = await user_commands.get_user(client_id)
    if not client:
        await callback.answer("Клиент не найден", show_alert=True)
        return
    
    # Получаем статистику клиента
    stats = await finance_commands.get_client_stats(client_id)
    
    # Получаем историю записей клиента
    appointments = await appointment_commands.get_client_appointments(client_id)
    
    # Формируем сообщение
    message = f"👤 *{client.get('full_name', 'Клиент')}*\n\n"
    
    message += f"📊 *Статистика:*\n"
    message += f"🔸 Визитов: {stats['total_visits']}\n"
    message += f"🔸 Потрачено: {stats['total_spent']} руб.\n"
    message += f"🔸 Последний визит: {stats['last_visit'] if stats['last_visit'] else 'Нет данных'}\n"
    message += f"🔸 Любимая услуга: {stats['favorite_service'] if stats['favorite_service'] else 'Нет данных'}\n"
    message += f"🔸 VIP-статус: {'Да' if stats['vip_status'] == 'Yes' else 'Нет'}\n"
    
    if stats.get('notes'):
        message += f"\n📝 *Заметки:*\n{stats['notes']}\n"
    
    message += f"\n📅 *Последние записи:*\n"
    
    if not appointments:
        message += "Нет данных о записях\n"
    else:
        for i, appt in enumerate(sorted(appointments, key=lambda x: x["date"], reverse=True)[:3]):
            service = await service_commands.get_service(appt["service_id"])
            service_name = service["name"] if service else "Неизвестная услуга"
            message += f"{i+1}. {appt['date']} - {service_name}\n"
    
    # Добавляем кнопки для работы с клиентом
    keyboard = await finance_keyboards.get_client_stats_menu(client_id)
    
    await callback.message.edit_text(
        message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка добавления заметки о клиенте
@router.callback_query(F.data.startswith("add_client_note_"))
async def add_client_note(callback: types.CallbackQuery, state: FSMContext):
    """Add client note"""
    client_id = callback.data.replace("add_client_note_", "")
    
    # Получаем данные о клиенте
    client = await user_commands.get_user(client_id)
    if not client:
        await callback.answer("Клиент не найден", show_alert=True)
        return
    
    # Получаем текущую заметку
    stats = await finance_commands.get_client_stats(client_id)
    current_note = stats.get("notes", "")
    
    # Сохраняем ID клиента в состоянии
    await state.update_data(client_id=client_id)
    
    await callback.message.edit_text(
        f"Добавьте заметку о клиенте *{client.get('full_name', 'Клиент')}*:\n\n"
        f"Текущая заметка: {current_note if current_note else 'Отсутствует'}\n\n"
        f"Введите новый текст заметки:",
        parse_mode="Markdown"
    )
    
    await state.set_state(FinanceStates.add_client_note)
    await callback.answer()

# Обработка ввода заметки о клиенте
@router.message(StateFilter(FinanceStates.add_client_note))
async def process_client_note(message: types.Message, state: FSMContext):
    """Process client note input"""
    # Получаем ID клиента из состояния
    data = await state.get_data()
    client_id = data.get("client_id")
    
    # Обновляем заметку
    await finance_commands.update_client_note(client_id, message.text)
    
    await message.answer("✅ Заметка успешно обновлена.")
    
    # Сбрасываем состояние
    await state.clear()
    
    # Возвращаемся к просмотру статистики клиента
    callback = types.CallbackQuery(
        id="1",
        from_user=message.from_user,
        chat_instance="1",
        message=message,
        data=f"finance_client_{client_id}"
    )
    
    await show_client_stats(callback)

# Обработка отправки напоминания клиенту
@router.callback_query(F.data.startswith("send_client_reminder_"))
async def send_client_reminder(callback: types.CallbackQuery):
    """Send reminder to client"""
    client_id = callback.data.replace("send_client_reminder_", "")
    
    # Получаем данные о клиенте
    client = await user_commands.get_user(client_id)
    if not client:
        await callback.answer("Клиент не найден", show_alert=True)
        return
    
    # Создаем клавиатуру для отметки о напоминании
    keyboard = await finance_keyboards.get_reminder_menu(client_id)
    
    await callback.message.edit_text(
        f"📱 *Напоминание клиенту*\n\n"
        f"Когда вы свяжетесь с клиентом *{client.get('full_name', 'Клиент')}*, "
        f"отметьте это здесь:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка отметки о напоминании
@router.callback_query(F.data.startswith("reminder_"))
async def handle_reminder_action(callback: types.CallbackQuery):
    """Handle reminder action"""
    action, client_id = callback.data.replace("reminder_", "").split("_")
    
    # Получаем данные о клиенте
    client = await user_commands.get_user(client_id)
    if not client:
        await callback.answer("Клиент не найден", show_alert=True)
        return
    
    if action == "called":
        message = f"✅ Вы отметили, что позвонили клиенту {client.get('full_name', 'Клиент')}."
    elif action == "messaged":
        message = f"✅ Вы отметили, что написали клиенту {client.get('full_name', 'Клиент')} в WhatsApp."
    else:  # cancel
        message = f"❌ Вы отменили напоминание клиенту {client.get('full_name', 'Клиент')}."
    
    await callback.answer(message, show_alert=True)
    
    # Возвращаемся к просмотру статистики клиента
    await show_client_stats(callback)

# Обработка меню "Активность клиентов"
@router.callback_query(F.data == "finance_client_activity")
async def show_client_activity(callback: types.CallbackQuery):
    """Show client activity"""
    # Получаем данные о записях
    appointments = await appointment_commands.get_all_appointments()
    
    if not appointments:
        await callback.message.edit_text(
            "👥 *Активность клиентов*\n\n"
            "У вас пока нет записей клиентов для анализа.",
            reply_markup=await finance_keyboards.get_back_to_finance_clients_keyboard(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Анализируем активность по дням недели
    weekday_counts = [0, 0, 0, 0, 0, 0, 0]  # Пн, Вт, ..., Вс
    month_counts = [0] * 12  # Янв, Фев, ..., Дек
    
    for appt in appointments:
        try:
            date_obj = datetime.datetime.strptime(appt["date"], "%Y-%m-%d")
            weekday = date_obj.weekday()
            month = date_obj.month - 1  # Индекс с 0
            
            weekday_counts[weekday] += 1
            month_counts[month] += 1
        except:
            pass
    
    # Находим самый и наименее популярный день недели
    max_weekday = weekday_counts.index(max(weekday_counts))
    min_weekday = weekday_counts.index(min(weekday_counts[:5]))  # Исключаем выходные
    
    weekdays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    months = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
    
    # Находим самый популярный месяц
    max_month = month_counts.index(max(month_counts))
    
    message = "👥 *Активность клиентов*\n\n"
    
    message += "📊 *Распределение по дням недели:*\n"
    for i, count in enumerate(weekday_counts):
        message += f"- {weekdays[i].capitalize()}: {count} записей\n"
    
    message += f"\n🔝 Самый популярный день: *{weekdays[max_weekday].capitalize()}* ({weekday_counts[max_weekday]} записей)\n"
    message += f"🔻 Наименее популярный будний день: *{weekdays[min_weekday].capitalize()}* ({weekday_counts[min_weekday]} записей)\n"
    
    message += f"\n📅 Самый популярный месяц: *{months[max_month].capitalize()}* ({month_counts[max_month]} записей)\n"
    
    message += "\n💡 *Рекомендации:*\n"
    message += f"- Запустите акцию в {weekdays[min_weekday]} для повышения загруженности\n"
    message += "- Рассмотрите повышение цен в наиболее популярные дни\n"
    message += "- Предлагайте бонусы за записи в непопулярное время"
    
    await callback.message.edit_text(
        message,
        reply_markup=await finance_keyboards.get_back_to_finance_clients_keyboard(),
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка меню "Прогноз доходов"
@router.callback_query(F.data == "finance_forecast")
async def show_finance_forecast(callback: types.CallbackQuery):
    """Show finance forecast"""
    keyboard = await finance_keyboards.get_finance_forecast_menu()
    
    # Получаем персонализированный прогноз
    forecast_message = await finance_commands.get_daily_forecast_message(callback.from_user.id)
    
    await callback.message.edit_text(
        forecast_message,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка выбора периода прогноза
@router.callback_query(F.data.startswith("forecast_"))
async def handle_forecast_period(callback: types.CallbackQuery):
    """Handle forecast period selection"""
    days = int(callback.data.replace("forecast_", "").replace("_days", ""))
    
    # Получаем прогноз на указанный период
    forecast = await finance_commands.calculate_profit_forecast(callback.from_user.id, days)
    
    if not forecast:
        await callback.message.edit_text(
            f"🔮 *Прогноз на {days} дней*\n\n"
            f"Недостаточно данных для составления прогноза. "
            f"Пожалуйста, внесите информацию о доходах и расходах за предыдущие периоды.",
            reply_markup=await finance_keyboards.get_finance_forecast_menu(),
            parse_mode="Markdown"
        )
    else:
        confidence = {
            "low": "низкая",
            "medium": "средняя",
            "high": "высокая"
        }
        
        message = f"🔮 *Прогноз на {days} дней*\n\n"
        message += f"💰 Ожидаемый доход: *{forecast['estimated_income']} руб.*\n"
        message += f"💸 Ожидаемые расходы: *{forecast['estimated_expenses']} руб.*\n"
        message += f"📈 Ожидаемая прибыль: *{forecast['estimated_profit']} руб.*\n\n"
        
        message += f"⚖️ Достоверность прогноза: *{confidence[forecast['confidence']]}*\n\n"
        
        # Добавляем рекомендации
        message += "💡 *Рекомендации:*\n"
        
        if forecast['estimated_profit'] > 0:
            message += "- Рассмотрите возможность инвестиций в оборудование или обучение\n"
            message += "- Запланируйте маркетинговые активности для привлечения новых клиентов\n"
        else:
            message += "- Пересмотрите прайс-лист и оптимизируйте расходные материалы\n"
            message += "- Запустите акции для увеличения количества клиентов\n"
        
        message += "- Проанализируйте рентабельность каждой услуги с помощью раздела \"Расходы на услуги\"\n"
        
        await callback.message.edit_text(
            message,
            reply_markup=await finance_keyboards.get_finance_forecast_menu(),
            parse_mode="Markdown"
        )
    
    await callback.answer()

# Обработка меню "Советы по бизнесу"
@router.callback_query(F.data == "finance_tips")
async def show_finance_tips(callback: types.CallbackQuery):
    """Show finance tips"""
    keyboard = await finance_keyboards.get_finance_tips_menu()
    
    await callback.message.edit_text(
        "💡 *Советы по бизнесу*\n\n"
        "Выберите категорию советов:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка выбора совета
@router.callback_query(F.data.startswith("tip_"))
async def show_specific_tip(callback: types.CallbackQuery):
    """Show specific business tip"""
    tip_type = callback.data.replace("tip_", "")
    
    if tip_type == "increase_profit":
        message = "🚀 *Как увеличить прибыль*\n\n"
        message += "1️⃣ *Оптимизируйте ценообразование*\n"
        message += "• Изучите цены конкурентов и позиционируйтесь соответственно\n"
        message += "• Введите систему скидок: утренние часы дешевле, вечерние — дороже\n"
        message += "• Создайте комплексные услуги с более высокой маржой\n\n"
        
        message += "2️⃣ *Увеличьте среднюю сумму чека*\n"
        message += "• Предлагайте дополнительные услуги во время визита\n"
        message += "• Используйте апселлинг («бесплатная укладка при окрашивании»)\n"
        message += "• Создайте карты лояльности с кешбэком на следующее посещение\n\n"
        
        message += "3️⃣ *Оптимизируйте рабочий процесс*\n"
        message += "• Автоматизируйте запись клиентов через этого бота\n"
        message += "• Правильно планируйте рабочее время мастеров\n"
        message += "• Используйте систему напоминаний клиентам для снижения неявок\n\n"
        
        message += "4️⃣ *Увеличьте частоту визитов*\n"
        message += "• Внедрите абонементы на несколько посещений\n"
        message += "• Проводите акции «Приведи друга» с бонусами\n"
        message += "• Делайте персональные предложения постоянным клиентам"
        
    elif tip_type == "optimize_costs":
        message = "💼 *Как оптимизировать расходы*\n\n"
        message += "1️⃣ *Профессиональная косметика*\n"
        message += "• Закупайте оптом базовые позиции\n"
        message += "• Рассчитывайте расход материала на 1 процедуру\n"
        message += "• Контролируйте использование продукции мастерами\n\n"
        
        message += "2️⃣ *Оптимизация аренды*\n"
        message += "• Заполняйте все рабочие дни равномерно\n"
        message += "• Оптимизируйте режим работы под клиентский поток\n"
        message += "• Рассмотрите работу с коллегами для деления арендной платы\n\n"
        
        message += "3️⃣ *Коммунальные платежи*\n"
        message += "• Используйте LED-освещение\n"
        message += "• Установите таймеры или датчики для света и электроприборов\n"
        message += "• Оптимизируйте использование кондиционера\n\n"
        
        message += "4️⃣ *Расходные материалы*\n"
        message += "• Проведите аудит использования расходников\n"
        message += "• Отслеживайте сроки годности всех продуктов\n"
        message += "• Используйте многоразовые альтернативы там, где это возможно"
        
    elif tip_type == "retain_clients":
        message = "👥 *Как удержать клиентов*\n\n"
        message += "1️⃣ *Качество обслуживания*\n"
        message += "• Придерживайтесь стандартов качества для всех услуг\n"
        message += "• Персонализируйте общение с клиентом\n"
        message += "• Собирайте и анализируйте обратную связь\n\n"
        
        message += "2️⃣ *Система лояльности*\n"
        message += "• Внедрите накопительные скидки постоянным клиентам\n"
        message += "• Создайте VIP-программу для самых ценных клиентов\n"
        message += "• Делайте небольшие приятные сюрпризы постоянным клиентам\n\n"
        
        message += "3️⃣ *Работа с клиентской базой*\n"
        message += "• Ведите учет предпочтений клиентов\n"
        message += "• Напоминайте о записи до того, как они сами об этом подумают\n"
        message += "• Поздравляйте клиентов с праздниками\n\n"
        
        message += "4️⃣ *Отслеживание неактивных клиентов*\n"
        message += "• Анализируйте, почему клиенты перестают приходить\n"
        message += "• Делайте специальные предложения тем, кто давно не был\n"
        message += "• Собирайте отзывы от ушедших клиентов для улучшения сервиса"
        
    elif tip_type == "get_reviews":
        message = "🔄 *Как получать больше отзывов*\n\n"
        message += "1️⃣ *Момент запроса*\n"
        message += "• Просите отзыв в конце успешной процедуры\n"
        message += "• Отправляйте сообщение через день после услуги\n"
        message += "• Упростите процесс оставления отзыва\n\n"
        
        message += "2️⃣ *Мотивация клиентов*\n"
        message += "• Предлагайте небольшую скидку за развернутый отзыв\n"
        message += "• Устраивайте ежемесячный розыгрыш среди оставивших отзывы\n"
        message += "• Благодарите лично за каждый отзыв\n\n"
        
        message += "3️⃣ *Работа с отзывами*\n"
        message += "• Отвечайте на каждый отзыв, особенно негативный\n"
        message += "• Используйте отзывы для улучшения сервиса\n"
        message += "• Размещайте лучшие отзывы в социальных сетях\n\n"
        
        message += "4️⃣ *Инструменты для сбора*\n"
        message += "• Создайте QR-коды, ведущие на платформы с отзывами\n"
        message += "• Используйте автоматические рассылки с просьбой оставить отзыв\n"
        message += "• Сделайте карточки с просьбой об отзыве и ссылками/QR-кодами"
    
    else:
        message = "Совет не найден"
    
    await callback.message.edit_text(
        message,
        reply_markup=await finance_keyboards.get_finance_tips_menu(),
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка команды /finance
@router.message(Command("finance"))
async def finance_command(message: types.Message):
    """Finance command handler"""
    # Проверяем роль пользователя (только admin)
    user = await user_commands.get_user(message.from_user.id)
    if not user or user.get("role", "") != "admin":
        await message.answer("⛔ Доступ только для администраторов")
        return
    
    keyboard = await finance_keyboards.get_finance_main_menu()
    await message.answer(
        "📊 *Финансы и аналитика*\n\n"
        "Добро пожаловать в раздел управления финансами. "
        "Здесь вы можете отслеживать доходы, расходы, анализировать "
        "прибыльность услуг и получать персонализированные рекомендации.",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Обработка интерактивной настройки
@router.callback_query(F.data == "start_finance_setup")
async def start_finance_setup(callback: types.CallbackQuery, state: FSMContext):
    """Start interactive finance setup"""
    # Устанавливаем первое состояние
    await state.set_state(FinanceStates.setup_materials)
    
    await callback.message.edit_text(
        "👋 *Бот-консультант по настройке финансов*\n\n"
        "Привет! Я помогу настроить финансовый учёт для вашего бизнеса.\n\n"
        "Давайте начнем с простого вопроса: *сколько в среднем у вас уходит на материалы для одной услуги?*\n"
        "(например, для маникюра введите среднюю стоимость в рублях)",
        parse_mode="Markdown"
    )
    
    await callback.answer()

# Обработка ответа на вопрос о материалах
@router.message(StateFilter(FinanceStates.setup_materials))
async def process_setup_materials(message: types.Message, state: FSMContext):
    """Process setup materials answer"""
    try:
        # Пытаемся преобразовать ответ в число
        materials_cost = float(message.text.replace(',', '.'))
        
        # Сохраняем ответ
        await state.update_data(materials_cost=materials_cost)
        
        # Переходим к следующему вопросу
        await state.set_state(FinanceStates.setup_rent)
        
        await message.answer(
            "✅ Отлично! Теперь давайте посчитаем аренду.\n\n"
            "*Сколько вы платите за аренду помещения в месяц?*\n"
            "(введите сумму в рублях, или введите 0, если у вас нет расходов на аренду)",
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение. Например: 200 или 350.50")

# Обработка ответа на вопрос об аренде
@router.message(StateFilter(FinanceStates.setup_rent))
async def process_setup_rent(message: types.Message, state: FSMContext):
    """Process setup rent answer"""
    try:
        # Пытаемся преобразовать ответ в число
        rent_cost = float(message.text.replace(',', '.'))
        
        # Сохраняем ответ
        await state.update_data(rent_cost=rent_cost)
        
        # Переходим к следующему вопросу
        await state.set_state(FinanceStates.setup_salary)
        
        await message.answer(
            "✅ Понял! А теперь о фонде заработной платы.\n\n"
            "*Какой процент от стоимости услуги вы отдаете мастеру?*\n"
            "(введите число от 0 до 100, например: 50 - если вы отдаете мастеру половину стоимости услуги)",
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение. Например: 15000 или 20000")

# Обработка ответа на вопрос о зарплате
@router.message(StateFilter(FinanceStates.setup_salary))
async def process_setup_salary(message: types.Message, state: FSMContext):
    """Process setup salary answer"""
    try:
        # Пытаемся преобразовать ответ в число
        salary_percent = float(message.text.replace(',', '.'))
        
        if salary_percent < 0 or salary_percent > 100:
            await message.answer("Пожалуйста, введите значение от 0 до 100")
            return
        
        # Сохраняем ответ
        await state.update_data(salary_percent=salary_percent)
        
        # Переходим к следующему вопросу
        await state.set_state(FinanceStates.setup_other)
        
        await message.answer(
            "✅ Хорошо! Осталось узнать о прочих расходах.\n\n"
            "*Какие еще ежемесячные расходы у вас есть?*\n"
            "(введите сумму в рублях - коммунальные услуги, интернет, реклама и т.д.)",
            parse_mode="Markdown"
        )
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение. Например: 50 или 60")

# Обработка ответа на вопрос о прочих расходах
@router.message(StateFilter(FinanceStates.setup_other))
async def process_setup_other(message: types.Message, state: FSMContext):
    """Process setup other costs answer"""
    try:
        # Пытаемся преобразовать ответ в число
        other_costs = float(message.text.replace(',', '.'))
        
        # Сохраняем ответ
        await state.update_data(other_costs=other_costs)
        
        # Получаем все собранные данные
        data = await state.get_data()
        
        # Рассчитываем некоторые показатели
        materials_cost = data.get("materials_cost", 0)
        rent_cost = data.get("rent_cost", 0)
        salary_percent = data.get("salary_percent", 0)
        other_costs = data.get("other_costs", 0)
        
        # Предполагаем среднюю стоимость услуги 1500 руб.
        avg_service_price = 1500
        
        # Рассчитываем затраты на одну услугу
        avg_service_cost = materials_cost + (rent_cost / 22 / 8)  # Предполагаем 22 рабочих дня, 8 услуг в день
        
        # Добавляем зарплату мастера
        salary_cost = avg_service_price * (salary_percent / 100)
        avg_service_cost += salary_cost
        
        # Добавляем прочие расходы
        other_per_service = other_costs / 22 / 8  # Предполагаем 22 рабочих дня, 8 услуг в день
        avg_service_cost += other_per_service
        
        # Рассчитываем прибыль и маржинальность
        profit = avg_service_price - avg_service_cost
        margin = (profit / avg_service_price) * 100
        
        # Формируем сообщение с результатами
        message_text = "📊 *Анализ финансовых показателей*\n\n"
        message_text += f"На основе предоставленных данных, вот ваши примерные показатели:\n\n"
        message_text += f"🔸 Средняя стоимость услуги: {avg_service_price} руб.\n"
        message_text += f"🔸 Расходы на материалы: {materials_cost} руб.\n"
        message_text += f"🔸 Зарплата мастера: {salary_cost} руб. ({salary_percent}%)\n"
        message_text += f"🔸 Доля аренды на услугу: {round(rent_cost / 22 / 8, 2)} руб.\n"
        message_text += f"🔸 Прочие расходы на услугу: {round(other_per_service, 2)} руб.\n\n"
        
        message_text += f"💰 *Прибыль с одной услуги: {round(profit, 2)} руб.*\n"
        message_text += f"📈 *Маржинальность: {round(margin, 2)}%*\n\n"
        
        # Даем рекомендации в зависимости от показателей
        message_text += "💡 *Рекомендации:*\n"
        
        if margin < 20:
            message_text += "❗ Ваша маржинальность слишком низкая. Рекомендуется:\n"
            message_text += "- Пересмотреть прайс-лист и повысить цены\n"
            message_text += "- Искать более доступные материалы без потери качества\n"
            message_text += "- Оптимизировать расход материалов\n"
        elif margin < 40:
            message_text += "⚠️ Ваша маржинальность в пределах нормы, но её можно улучшить:\n"
            message_text += "- Добавьте услуги с более высокой маржинальностью\n"
            message_text += "- Оптимизируйте время выполнения услуг\n"
            message_text += "- Рассмотрите возможность групповых закупок материалов\n"
        else:
            message_text += "✅ Ваша маржинальность на хорошем уровне! Рекомендации:\n"
            message_text += "- Масштабируйте бизнес и привлекайте больше клиентов\n"
            message_text += "- Инвестируйте в обучение и новое оборудование\n"
            message_text += "- Рассмотрите возможность расширения спектра услуг\n"
        
        message_text += "\nТеперь вы можете использовать раздел 'Финансы и аналитика' для отслеживания доходов и расходов."
        
        # Сбрасываем состояние
        await state.clear()
        
        # Отправляем сообщение с результатами и возвращаемся в финансовое меню
        await message.answer(
            message_text,
            parse_mode="Markdown",
            reply_markup=await finance_keyboards.get_finance_main_menu()
        )
    except ValueError:
        await message.answer("Пожалуйста, введите числовое значение. Например: 5000 или 7500")

# Функция для еженедельного напоминания о расходах
async def send_weekly_expense_reminder(bot):
    """Send weekly expense reminder to admins"""
    try:
        # Получаем список всех пользователей
        users = await user_commands.get_all_users()
        
        # Фильтруем только администраторов
        admins = [user for user in users if user.get("role", "") == "admin"]
        
        # Текущая дата и день недели
        now = datetime.datetime.now()
        
        # Проверяем, что сегодня воскресенье (6 - это воскресенье в Python)
        if now.weekday() == 6:
            for admin in admins:
                try:
                    admin_id = admin["user_id"]
                    
                    await bot.send_message(
                        admin_id,
                        "📝 *Еженедельное напоминание*\n\n"
                        "Привет! Не забудьте записать ваши расходы за прошедшую неделю. "
                        "Это поможет вести точный финансовый учет и получать корректные аналитические данные.\n\n"
                        "Хотите внести расходы прямо сейчас?",
                        parse_mode="Markdown",
                        reply_markup=await finance_keyboards.get_finance_main_menu()
                    )
                except Exception as e:
                    logging.error(f"Error sending reminder to admin {admin.get('user_id')}: {str(e)}")
    except Exception as e:
        logging.error(f"Error in send_weekly_expense_reminder: {str(e)}")
