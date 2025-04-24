
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_keyboard():
    """Get main admin keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="🛠 Управление услугами", callback_data="admin_services")
    builder.button(text="👤 Управление мастерами", callback_data="admin_masters")
    builder.button(text="📅 Управление записями", callback_data="admin_appointments")
    builder.button(text="🌟 Специальные предложения", callback_data="admin_offers")
    builder.button(text="🗂 Управление категориями", callback_data="admin_categories")
    
    builder.adjust(1)
    return builder.as_markup()

def get_services_management_keyboard():
    """Get service management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✨ Быстрое создание услуг", callback_data="template_categories")
    builder.button(text="➕ Добавить услугу", callback_data="add_service")
    builder.button(text="📋 Просмотреть услуги", callback_data="view_services")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_template_categories_keyboard(categories):
    """Get keyboard with template service categories"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.button(text=f"🔹 {category}", callback_data=f"template_category_{category}")
    
    builder.button(text="◀️ Назад", callback_data="admin_services")
    
    builder.adjust(1)
    return builder.as_markup()

def get_category_services_price_keyboard(category_id):
    """Get keyboard to set prices for category services"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="💰 Установить цену для всех услуг", callback_data=f"update_category_price_{category_id}")
    builder.button(text="📋 Просмотреть услуги в категории", callback_data=f"view_category_{category_id}")
    builder.button(text="◀️ Назад", callback_data="admin_services")
    
    builder.adjust(1)
    return builder.as_markup()

def get_service_categories_keyboard(services_by_category):
    """Get keyboard with service categories"""
    builder = InlineKeyboardBuilder()
    
    for category, services in services_by_category.items():
        builder.button(text=f"📁 {category} ({len(services)})", callback_data=f"view_category_services_{category}")
    
    builder.button(text="◀️ Назад", callback_data="admin_services")
    
    builder.adjust(1)
    return builder.as_markup()

def get_category_services_keyboard(services, category_name):
    """Get keyboard with services in a category"""
    builder = InlineKeyboardBuilder()
    
    for service in services:
        builder.button(text=f"🔸 {service['name']} - {service.get('price', '0')} руб.", callback_data=f"admin_view_service_{service['id']}")
    
    builder.button(text="◀️ Назад к категориям", callback_data="view_services")
    builder.button(text="◀️ Назад к управлению услугами", callback_data="admin_services")
    
    builder.adjust(1)
    return builder.as_markup()

def get_back_to_services_keyboard():
    """Get back to services keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="◀️ Назад к услугам", callback_data="admin_services")
    
    return builder.as_markup()

def get_service_actions_keyboard(service_id):
    """Get keyboard with service actions"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Редактировать", callback_data=f"edit_service_{service_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_service_confirm_{service_id}")
    builder.button(text="◀️ Назад", callback_data="view_services")
    
    builder.adjust(1)
    return builder.as_markup()

def get_edit_service_keyboard(service_id):
    """Get keyboard for editing service"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить название", callback_data=f"edit_service_name_{service_id}")
    builder.button(text="📝 Изменить описание", callback_data=f"edit_service_description_{service_id}")
    builder.button(text="💰 Изменить цену", callback_data=f"edit_service_price_{service_id}")
    builder.button(text="⏱ Изменить продолжительность", callback_data=f"edit_service_duration_{service_id}")
    builder.button(text="📁 Изменить категорию", callback_data=f"edit_service_category_{service_id}")
    builder.button(text="◀️ Назад", callback_data=f"admin_view_service_{service_id}")
    
    builder.adjust(1)
    return builder.as_markup()

def get_masters_management_keyboard():
    """Get masters management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Добавить мастера", callback_data="add_master")
    builder.button(text="👤 Просмотр мастеров", callback_data="view_masters_admin")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_master_actions_keyboard(master_id):
    """Get keyboard with master actions"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Редактировать", callback_data=f"edit_master_{master_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_master_confirm_{master_id}")
    builder.button(text="◀️ Назад", callback_data="view_masters_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_edit_master_keyboard(master_id):
    """Get keyboard for editing master"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить имя", callback_data=f"edit_master_name_{master_id}")
    builder.button(text="📱 Изменить Telegram", callback_data=f"edit_master_telegram_{master_id}")
    builder.button(text="📍 Изменить адрес", callback_data=f"edit_master_address_{master_id}")
    builder.button(text="🗺 Изменить местоположение", callback_data=f"edit_master_location_{master_id}")
    builder.button(text="◀️ Назад", callback_data=f"admin_view_master_{master_id}")
    
    builder.adjust(1)
    return builder.as_markup()

def get_appointments_management_keyboard():
    """Get appointments management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📅 Записи по дате", callback_data="admin_appointments_date")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_date_appointments_admin_keyboard(appointments, date):
    """Get keyboard with appointments for a specific date"""
    builder = InlineKeyboardBuilder()
    
    for appointment in appointments:
        builder.button(text=f"Запись {appointment['id']} - {appointment['time']}", callback_data=f"admin_view_appointment_{appointment['id']}")
    
    builder.button(text="◀️ Назад", callback_data="admin_appointments")
    
    builder.adjust(1)
    return builder.as_markup()

def get_appointment_actions_keyboard(appointment_id, status):
    """Get keyboard with appointment actions"""
    builder = InlineKeyboardBuilder()
    
    if status == "pending":
        builder.button(text="✅ Подтвердить", callback_data=f"admin_confirm_appointment_{appointment_id}")
    
    if status != "completed":
        builder.button(text="✓ Отметить выполненной", callback_data=f"mark_completed_{appointment_id}")
    
    if status != "paid":
        builder.button(text="💰 Отметить оплаченной", callback_data=f"mark_paid_{appointment_id}")
    
    builder.button(text="💵 Наличные", callback_data=f"set_payment_cash_{appointment_id}")
    builder.button(text="💳 Карта/Терминал", callback_data=f"set_payment_card_{appointment_id}")
    builder.button(text="📲 Перевод", callback_data=f"set_payment_transfer_{appointment_id}")
    builder.button(text="❌ Отменить запись", callback_data=f"admin_cancel_appointment_{appointment_id}")
    builder.button(text="◀️ Назад", callback_data="admin_appointments")
    
    builder.adjust(1)
    return builder.as_markup()

def get_cancel_appointment_keyboard(appointment_id):
    """Get keyboard for cancelling appointment"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Подтвердить отмену", callback_data=f"confirm_cancel_appointment_{appointment_id}")
    builder.button(text="◀️ Назад", callback_data=f"admin_view_appointment_{appointment_id}")
    
    builder.adjust(1)
    return builder.as_markup()

def get_categories_management_keyboard():
    """Get categories management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Добавить категорию", callback_data="add_category")
    builder.button(text="📋 Просмотр категорий", callback_data="view_categories")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_all_categories_keyboard(categories):
    """Get keyboard with all categories"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.button(text=f"📁 {category['name']}", callback_data=f"admin_view_category_{category['id']}")
    
    builder.button(text="◀️ Назад", callback_data="admin_categories")
    
    builder.adjust(1)
    return builder.as_markup()

def get_category_actions_keyboard(category_id):
    """Get keyboard with category actions"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Редактировать", callback_data=f"edit_category_{category_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_category_confirm_{category_id}")
    builder.button(text="📋 Услуги категории", callback_data=f"view_category_{category_id}")
    builder.button(text="◀️ Назад", callback_data="view_categories")
    
    builder.adjust(1)
    return builder.as_markup()

def get_edit_category_keyboard(category_id):
    """Get keyboard for editing category"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить название", callback_data=f"edit_category_name_{category_id}")
    builder.button(text="◀️ Назад", callback_data=f"admin_view_category_{category_id}")
    
    builder.adjust(1)
    return builder.as_markup()

def get_offers_management_keyboard():
    """Get offers management keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="➕ Добавить спец. предложение", callback_data="add_offer")
    builder.button(text="📋 Просмотреть спец. предложения", callback_data="view_offers")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_all_offers_keyboard(offers):
    """Get keyboard with all offers"""
    builder = InlineKeyboardBuilder()
    
    for offer in offers:
        builder.button(text=f"🌟 {offer['name']}", callback_data=f"admin_view_offer_{offer['id']}")
    
    builder.button(text="◀️ Назад", callback_data="admin_offers")
    
    builder.adjust(1)
    return builder.as_markup()

def get_offer_actions_keyboard(offer_id):
    """Get keyboard with offer actions"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✏️ Редактировать", callback_data=f"edit_offer_{offer_id}")
    builder.button(text="🗑 Удалить", callback_data=f"delete_offer_confirm_{offer_id}")
    builder.button(text="◀️ Назад", callback_data="view_offers")
    
    builder.adjust(1)
    return builder.as_markup()

def get_edit_offer_keyboard(offer_id):
    """Get keyboard for editing offer"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📝 Изменить название", callback_data=f"edit_offer_name_{offer_id}")
    builder.button(text="📝 Изменить описание", callback_data=f"edit_offer_description_{offer_id}")
    builder.button(text="💰 Изменить цену", callback_data=f"edit_offer_price_{offer_id}")
    builder.button(text="⏱ Изменить продолжительность", callback_data=f"edit_offer_duration_{offer_id}")
    builder.button(text="◀️ Назад", callback_data=f"admin_view_offer_{offer_id}")
    
    builder.adjust(1)
    return builder.as_markup()

def get_back_to_admin_keyboard():
    """Get back to admin keyboard"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="◀️ Назад в админ-панель", callback_data="back_to_admin")
    
    return builder.as_markup()

def get_confirm_delete_keyboard(entity_id, entity_type):
    """Get confirmation keyboard for deletion"""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="✅ Да, удалить", callback_data=f"confirm_delete_{entity_type}_{entity_id}")
    
    if entity_type == "service":
        builder.button(text="❌ Отмена", callback_data=f"admin_view_service_{entity_id}")
    elif entity_type == "category":
        builder.button(text="❌ Отмена", callback_data=f"admin_view_category_{entity_id}")
    elif entity_type == "master":
        builder.button(text="❌ Отмена", callback_data=f"admin_view_master_{entity_id}")
    elif entity_type == "offer":
        builder.button(text="❌ Отмена", callback_data=f"admin_view_offer_{entity_id}")
    else:
        builder.button(text="❌ Отмена", callback_data="back_to_admin")
    
    builder.adjust(1)
    return builder.as_markup()

def get_admin_appointments_keyboard():
    """Get admin appointments keyboard"""
    builder = InlineKeyboardBuilder()

    builder.button(text="Показать сегодняшние записи", callback_data="admin_appointments_today")
    builder.button(text="Показать все записи", callback_data="admin_appointments_all")
    builder.button(text="Показать записи за определенную дату", callback_data="admin_appointments_date")
    builder.button(text="◀️ Назад", callback_data="back_to_admin")

    builder.adjust(1)
    return builder.as_markup()
