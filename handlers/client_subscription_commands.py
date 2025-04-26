
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import client_keyboards
from utils.db_api import subscription_commands, user_commands
import logging

router = Router()

class SubscriptionStates(StatesGroup):
    selecting_plan = State()
    confirming_purchase = State()
    entering_referral = State()

@router.message(Command("subscription"))
async def cmd_subscription(message: Message, state: FSMContext, user: dict):
    """Handle subscription command - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await message.answer("Команда доступна только для администраторов.")
        return
    
    # Check current subscription status
    user_id = message.from_user.id
    status = await subscription_commands.check_subscription_status(user_id)
    
    # Show subscription menu
    keyboard = await client_keyboards.get_subscription_menu_keyboard(status['active'])
    
    if status['active']:
        await message.answer(f"Информация о подписке:\n{status['message']}", reply_markup=keyboard)
    else:
        await message.answer("У вас нет активной подписки. Выберите действие:", reply_markup=keyboard)

@router.callback_query(F.data == "subscription_menu")
async def subscription_menu(callback: CallbackQuery, user: dict):
    """Show subscription menu - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Меню подписки доступно только для администраторов.")
        await callback.message.answer("Эта функция доступна только для администраторов.")
        return
    
    user_id = callback.from_user.id
    status = await subscription_commands.check_subscription_status(user_id)
    
    keyboard = await client_keyboards.get_subscription_menu_keyboard(status['active'])
    
    if status['active']:
        await callback.message.edit_text(f"Информация о подписке:\n{status['message']}", reply_markup=keyboard)
    else:
        await callback.message.edit_text("У вас нет активной подписки. Выберите действие:", reply_markup=keyboard)
    
    await callback.answer()

@router.callback_query(F.data == "subscription_status")
async def subscription_status(callback: CallbackQuery, user: dict):
    """Show subscription status - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Статус подписки доступен только для администраторов.")
        return
    
    user_id = callback.from_user.id
    status = await subscription_commands.check_subscription_status(user_id)
    
    if status['active']:
        message_text = (
            f"Ваша {'пробная ' if status['trial'] else ''}подписка активна.\n"
            f"Дней осталось: {status['days_left']}\n"
            f"Дата окончания: {status['end_date']}"
        )
    else:
        message_text = "У вас нет активной подписки."
    
    await callback.message.edit_text(message_text, reply_markup=await client_keyboards.get_back_to_subscription_keyboard())
    await callback.answer()

@router.callback_query(F.data == "buy_subscription")
async def buy_subscription(callback: CallbackQuery, state: FSMContext, user: dict):
    """Show subscription plans - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Покупка подписки доступна только для администраторов.")
        return
    
    await callback.message.edit_text(
        "Выберите план подписки:\n\n"
        "1 месяц - 1999 руб\n"
        "2 месяца - 3998 руб\n"
        "3 месяца - 5697 руб (скидка 5%)\n"
        "6 месяцев - 10794 руб (скидка 10%)\n"
        "12 месяцев - 19190 руб (скидка 20%)",
        reply_markup=await client_keyboards.get_subscription_plans_keyboard()
    )
    
    await state.set_state(SubscriptionStates.selecting_plan)
    await callback.answer()

@router.callback_query(SubscriptionStates.selecting_plan, F.data.startswith("plan_"))
async def select_plan(callback: CallbackQuery, state: FSMContext, user: dict):
    """Handle subscription plan selection - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Выбор плана подписки доступен только для администраторов.")
        await state.clear()
        return
    
    plan = callback.data.split("_")[1]
    
    # Store selected plan
    await state.update_data(selected_plan=plan)
    
    # Calculate details
    months = int(plan)
    base_price = 1999
    
    if months >= 12:
        discount = 0.2  # 20% discount
        price = int(base_price * months * (1 - discount))
        discount_text = "20%"
    elif months >= 6:
        discount = 0.1  # 10% discount
        price = int(base_price * months * (1 - discount))
        discount_text = "10%"
    elif months >= 3:
        discount = 0.05  # 5% discount
        price = int(base_price * months * (1 - discount))
        discount_text = "5%"
    else:
        discount = 0
        price = base_price * months
        discount_text = "0%"
    
    # Save price information
    await state.update_data(price=price, months=months)
    
    # Confirmation message
    message_text = (
        f"Вы выбрали план на {months} {'месяц' if months == 1 else 'месяцев'}.\n"
        f"Стоимость: {price} руб.\n"
        f"Скидка: {discount_text}\n\n"
        "Для оформления подписки свяжитесь с администратором."
    )
    
    await callback.message.edit_text(
        message_text,
        reply_markup=await client_keyboards.get_subscription_confirm_keyboard()
    )
    
    await state.set_state(SubscriptionStates.confirming_purchase)
    await callback.answer()

@router.callback_query(SubscriptionStates.confirming_purchase, F.data == "confirm_subscription")
async def confirm_subscription(callback: CallbackQuery, state: FSMContext, user: dict):
    """Confirm subscription purchase - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Подтверждение подписки доступно только для администраторов.")
        await state.clear()
        return
    
    data = await state.get_data()
    months = data.get('months', 1)
    
    # This is a placeholder - in a real system, you'd process payment here
    # For this example, we'll just activate the subscription
    user_id = callback.from_user.id
    days = months * 30
    
    # Create/extend subscription
    await subscription_commands.create_subscription(user_id, days)
    
    await callback.message.edit_text(
        f"Поздравляем! Ваша подписка на {months} {'месяц' if months == 1 else 'месяцев'} активирована.",
        reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], True)
    )
    
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "referral_program")
async def referral_program(callback: CallbackQuery, state: FSMContext, user: dict):
    """Show referral program information - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Реферальная программа доступна только для администраторов.")
        return
    
    await callback.message.edit_text(
        "Реферальная программа:\n\n"
        "Пригласите друга использовать наш бот для управления бизнесом, "
        "и получите 1 месяц подписки бесплатно!\n\n"
        "Для получения бонуса, попросите вашего друга указать ваш Telegram ID при регистрации.",
        reply_markup=await client_keyboards.get_back_to_subscription_keyboard()
    )
    
    await callback.answer()

@router.callback_query(F.data == "enter_referral")
async def enter_referral(callback: CallbackQuery, state: FSMContext, user: dict):
    """Enter referral code - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Ввод реферального кода доступен только для администраторов.")
        return
    
    await callback.message.edit_text(
        "Пожалуйста, введите ID пригласившего вас пользователя:",
        reply_markup=await client_keyboards.get_back_to_subscription_keyboard()
    )
    
    await state.set_state(SubscriptionStates.entering_referral)
    await callback.answer()

@router.message(SubscriptionStates.entering_referral)
async def process_referral_code(message: Message, state: FSMContext, user: dict):
    """Process entered referral code - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await message.answer("Обработка реферального кода доступна только для администраторов.")
        await state.clear()
        return
    
    referrer_id = message.text.strip()
    
    try:
        # Validate that referrer_id is a number
        referrer_id_int = int(referrer_id)
        
        # Check if referrer exists and is an admin
        referrer = await user_commands.get_user(referrer_id_int)
        if not referrer or referrer["role"] != "admin":
            await message.answer(
                "Ошибка: указанный пользователь не найден или не является администратором.",
                reply_markup=await client_keyboards.get_back_to_subscription_keyboard()
            )
            return
            
        # Process referral
        await subscription_commands.process_referral(referrer_id_int)
        
        await message.answer(
            "Спасибо! Реферальный код принят. Пользователь получит 1 месяц подписки бесплатно.",
            reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], True)
        )
    except ValueError:
        await message.answer(
            "Ошибка: ID должен быть числом. Попробуйте снова.",
            reply_markup=await client_keyboards.get_back_to_subscription_keyboard()
        )
    
    await state.clear()

@router.callback_query(F.data == "back_to_subscription")
async def back_to_subscription(callback: CallbackQuery, state: FSMContext):
    """Go back to subscription menu"""
    await state.clear()
    await subscription_menu(callback, callback.message.db_data["user"] if hasattr(callback.message, "db_data") else {"role": "admin"})

@router.callback_query(F.data == "trial_subscription")
async def trial_subscription(callback: CallbackQuery, user: dict):
    """Create trial subscription - for admin users only"""
    # Verify user is an admin
    if user["role"] != "admin":
        await callback.answer("Пробная подписка доступна только для администраторов.")
        return
        
    user_id = callback.from_user.id
    
    # Check if user already has a subscription
    status = await subscription_commands.check_subscription_status(user_id)
    
    if status['active']:
        await callback.message.edit_text(
            "У вас уже есть активная подписка.",
            reply_markup=await client_keyboards.get_back_to_subscription_keyboard()
        )
    else:
        # Create 7-day trial subscription
        await subscription_commands.create_trial(user_id, 7)
        
        await callback.message.edit_text(
            "Поздравляем! Ваша 7-дневная пробная подписка активирована.",
            reply_markup=await client_keyboards.get_main_menu_keyboard(user["role"], True)
        )
    
    await callback.answer()
