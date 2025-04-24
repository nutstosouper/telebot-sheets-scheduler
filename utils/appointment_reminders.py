
import asyncio
import logging
from datetime import datetime, time, timedelta
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.db_api import appointment_commands, master_commands, service_commands

async def get_today_uncompleted_appointments():
    """Get all appointments for today that are not marked as completed or canceled"""
    today = datetime.now().strftime("%Y-%m-%d")
    appointments = await appointment_commands.get_appointments_by_date(today)
    
    # Filter for appointments that are not completed or canceled
    uncompleted = []
    for appointment in appointments:
        if appointment.get('status') not in ['completed', 'canceled', 'paid']:
            # Add service info
            service_id = appointment.get('service_id')
            if service_id:
                service = await service_commands.get_service(service_id)
                if service:
                    appointment['service_name'] = service.get('name')
                    
            # Add master info
            master_id = appointment.get('master_id')
            if master_id:
                master = await master_commands.get_master(master_id)
                if master:
                    appointment['master_name'] = master.get('name')
            
            uncompleted.append(appointment)
    
    return uncompleted

async def send_completion_reminder(bot, admin_id, appointment):
    """Send reminder to admin to mark appointment status"""
    # Create keyboard with action buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершено и оплачено", callback_data=f"complete_paid_{appointment['id']}")],
        [InlineKeyboardButton(text="✅ Завершено, не оплачено", callback_data=f"complete_unpaid_{appointment['id']}")],
        [InlineKeyboardButton(text="❌ Отменено", callback_data=f"admin_cancel_appointment_{appointment['id']}")],
        [InlineKeyboardButton(text="⏩ Отложить напоминание", callback_data=f"remind_later_{appointment['id']}")],
    ])
    
    # Get service and client info
    service_name = appointment.get('service_name', 'Услуга')
    client_id = appointment.get('user_id', 'Неизвестно')
    time_slot = appointment.get('time', 'Неизвестно')
    master_name = appointment.get('master_name', 'Неизвестно')
    
    # Send message to admin
    await bot.send_message(
        admin_id,
        f"📋 Статус записи не обновлен:\n\n"
        f"🕒 Время: {time_slot}\n"
        f"💇 Услуга: {service_name}\n"
        f"👤 Клиент ID: {client_id}\n"
        f"👨‍💼 Мастер: {master_name}\n\n"
        f"Пожалуйста, обновите статус записи:",
        reply_markup=keyboard
    )

async def check_daily_appointments(bot, admin_ids):
    """Check for uncompleted appointments at the end of the day and send reminders"""
    # Get current hour
    now = datetime.now()
    current_hour = now.hour
    
    # Only run at the end of the day (between 19:00 and 23:59)
    if 19 <= current_hour <= 23:
        logging.info("Running end-of-day appointment status check")
        
        try:
            # Get uncompleted appointments for today
            uncompleted = await get_today_uncompleted_appointments()
            
            if uncompleted:
                logging.info(f"Found {len(uncompleted)} uncompleted appointments for today")
                
                # Send reminders to all admins
                for admin_id in admin_ids:
                    for appointment in uncompleted:
                        await send_completion_reminder(bot, admin_id, appointment)
                        # Add small delay to avoid flood limit
                        await asyncio.sleep(0.3)
            else:
                logging.info("No uncompleted appointments found for today")
        
        except Exception as e:
            logging.error(f"Error in daily appointment check: {str(e)}")

async def start_reminder_scheduler(bot, admin_ids):
    """Start the scheduler for appointment reminders"""
    while True:
        await check_daily_appointments(bot, admin_ids)
        
        # Calculate time until next check (run every hour during evening)
        now = datetime.now()
        if now.hour >= 23:
            # Next check tomorrow at 19:00
            next_check = datetime.combine(now.date() + timedelta(days=1), time(19, 0))
        else:
            # Next check in one hour
            next_check = now + timedelta(hours=1)
        
        # Calculate seconds to sleep
        seconds_to_sleep = (next_check - now).total_seconds()
        await asyncio.sleep(seconds_to_sleep)
