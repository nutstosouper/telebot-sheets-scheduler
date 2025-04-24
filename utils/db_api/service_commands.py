
from utils.db_api.google_sheets import get_sheet, write_to_sheet
import json

# Sheet names
SERVICES_SHEET = "Services"
CATEGORIES_SHEET = "Categories"
OFFERS_SHEET = "Offers"
TEMPLATES_SHEET = "ServiceTemplates"

async def get_all_services():
    """Get all services from the database"""
    services = await get_sheet(SERVICES_SHEET)
    return services

async def get_service(service_id):
    """Get a service by its ID"""
    services = await get_all_services()
    for service in services:
        if service.get('id') == service_id:
            return service
    return None

async def get_services_by_category():
    """Get services grouped by category"""
    services = await get_all_services()
    categories = await get_all_categories()
    
    # Create a lookup dictionary for category names
    category_lookup = {category['id']: category['name'] for category in categories}
    
    # Group services by category
    services_by_category = {}
    for service in services:
        category_id = service.get('category_id', 'uncategorized')
        category_name = category_lookup.get(category_id, 'Без категории')
        
        if category_name not in services_by_category:
            services_by_category[category_name] = []
        
        services_by_category[category_name].append(service)
    
    return services_by_category

async def get_services_in_category(category_id):
    """Get all services in a specific category"""
    services = await get_all_services()
    return [service for service in services if service.get('category_id') == category_id]

async def get_services_by_category_name(category_name):
    """Get all services in a category by name"""
    services = await get_all_services()
    categories = await get_all_categories()
    
    # Find category ID by name
    category_id = None
    for category in categories:
        if category.get('name') == category_name:
            category_id = category.get('id')
            break
    
    if not category_id:
        return []
    
    # Get services in this category
    return [service for service in services if service.get('category_id') == category_id]

async def add_service(name, description, price, duration, category_id=None):
    """Add a new service to the database"""
    services = await get_all_services()
    
    # Generate a new ID
    new_id = "1"
    if services:
        new_id = str(max([int(service.get('id', 0)) for service in services]) + 1)
    
    # Create new service
    new_service = {
        'id': new_id,
        'name': name,
        'description': description,
        'price': price,
        'duration': duration
    }
    
    # Add category ID if provided
    if category_id:
        new_service['category_id'] = category_id
    
    # Add to sheet
    services.append(new_service)
    await write_to_sheet(SERVICES_SHEET, services)
    
    return new_service

async def update_service(service_id, name=None, description=None, price=None, duration=None, category_id=None):
    """Update a service in the database"""
    services = await get_all_services()
    updated = False
    
    for i, service in enumerate(services):
        if service.get('id') == service_id:
            # Update fields if provided
            if name is not None:
                services[i]['name'] = name
            if description is not None:
                services[i]['description'] = description
            if price is not None:
                services[i]['price'] = price
            if duration is not None:
                services[i]['duration'] = duration
            if category_id is not None:
                services[i]['category_id'] = category_id
            
            updated = True
            break
    
    if updated:
        await write_to_sheet(SERVICES_SHEET, services)
    
    return updated

async def delete_service(service_id):
    """Delete a service from the database"""
    services = await get_all_services()
    
    # Filter out the service to delete
    updated_services = [service for service in services if service.get('id') != service_id]
    
    # Check if a service was removed
    if len(updated_services) < len(services):
        await write_to_sheet(SERVICES_SHEET, updated_services)
        return True
    
    return False

# Category functions
async def get_all_categories():
    """Get all categories from the database"""
    categories = await get_sheet(CATEGORIES_SHEET)
    return categories

async def get_categories():
    """Alias for get_all_categories"""
    return await get_all_categories()

async def get_category(category_id):
    """Get a category by its ID"""
    categories = await get_all_categories()
    for category in categories:
        if category.get('id') == category_id:
            return category
    return None

async def get_category_by_name(name):
    """Get a category by its name"""
    categories = await get_all_categories()
    for category in categories:
        if category.get('name').lower() == name.lower():
            return category
    return None

async def add_category(name):
    """Add a new category to the database"""
    categories = await get_all_categories()
    
    # Check if category already exists
    for category in categories:
        if category.get('name').lower() == name.lower():
            return category
    
    # Generate a new ID
    new_id = "1"
    if categories:
        new_id = str(max([int(category.get('id', 0)) for category in categories]) + 1)
    
    # Create new category
    new_category = {
        'id': new_id,
        'name': name
    }
    
    # Add to sheet
    categories.append(new_category)
    await write_to_sheet(CATEGORIES_SHEET, categories)
    
    return new_category

async def update_category(category_id, name=None):
    """Update a category in the database"""
    categories = await get_all_categories()
    updated = False
    
    for i, category in enumerate(categories):
        if category.get('id') == category_id:
            # Update fields if provided
            if name is not None:
                categories[i]['name'] = name
            
            updated = True
            break
    
    if updated:
        await write_to_sheet(CATEGORIES_SHEET, categories)
    
    return updated

async def delete_category(category_id):
    """Delete a category from the database"""
    categories = await get_all_categories()
    
    # Filter out the category to delete
    updated_categories = [category for category in categories if category.get('id') != category_id]
    
    # Check if a category was removed
    if len(updated_categories) < len(categories):
        await write_to_sheet(CATEGORIES_SHEET, updated_categories)
        
        # Also update any services that had this category
        services = await get_all_services()
        updated = False
        
        for i, service in enumerate(services):
            if service.get('category_id') == category_id:
                # Remove the category reference
                if 'category_id' in services[i]:
                    del services[i]['category_id']
                updated = True
        
        if updated:
            await write_to_sheet(SERVICES_SHEET, services)
        
        return True
    
    return False

# Special offers functions
async def get_all_offers():
    """Get all special offers from the database"""
    offers = await get_sheet(OFFERS_SHEET)
    return offers

async def get_offers():
    """Alias for get_all_offers"""
    return await get_all_offers()

async def get_offer(offer_id):
    """Get a special offer by its ID"""
    offers = await get_all_offers()
    for offer in offers:
        if offer.get('id') == offer_id:
            return offer
    return None

async def add_offer(name, description, price, duration):
    """Add a new special offer to the database"""
    offers = await get_all_offers()
    
    # Generate a new ID
    new_id = "1"
    if offers:
        new_id = str(max([int(offer.get('id', 0)) for offer in offers]) + 1)
    
    # Create new offer
    new_offer = {
        'id': new_id,
        'name': name,
        'description': description,
        'price': price,
        'duration': duration
    }
    
    # Add to sheet
    offers.append(new_offer)
    await write_to_sheet(OFFERS_SHEET, offers)
    
    return new_offer

async def update_offer(offer_id, name=None, description=None, price=None, duration=None):
    """Update a special offer in the database"""
    offers = await get_all_offers()
    updated = False
    
    for i, offer in enumerate(offers):
        if offer.get('id') == offer_id:
            # Update fields if provided
            if name is not None:
                offers[i]['name'] = name
            if description is not None:
                offers[i]['description'] = description
            if price is not None:
                offers[i]['price'] = price
            if duration is not None:
                offers[i]['duration'] = duration
            
            updated = True
            break
    
    if updated:
        await write_to_sheet(OFFERS_SHEET, offers)
    
    return updated

async def delete_offer(offer_id):
    """Delete a special offer from the database"""
    offers = await get_all_offers()
    
    # Filter out the offer to delete
    updated_offers = [offer for offer in offers if offer.get('id') != offer_id]
    
    # Check if an offer was removed
    if len(updated_offers) < len(offers):
        await write_to_sheet(OFFERS_SHEET, updated_offers)
        return True
    
    return False

# Template service functions
async def get_all_template_categories():
    """Get all unique category names from the templates"""
    templates = await get_sheet(TEMPLATES_SHEET)
    # Extract unique category names
    categories = set()
    for template in templates:
        categories.add(template.get('category_name', ''))
    
    # Convert to list and sort
    return sorted(list(categories))

async def get_template_services_by_category(category_name):
    """Get all template services for a specific category"""
    templates = await get_sheet(TEMPLATES_SHEET)
    return [t for t in templates if t.get('category_name') == category_name]

async def create_services_from_template(category_name):
    """Create services from a template category"""
    # Get category by name or create it
    category = await get_category_by_name(category_name)
    if not category:
        category = await add_category(category_name)
    
    if not category:
        return (False, "Не удалось создать категорию")
    
    category_id = category.get('id')
    
    # Get template services for this category
    templates = await get_template_services_by_category(category_name)
    if not templates:
        return (False, f"Шаблоны услуг для категории '{category_name}' не найдены")
    
    # Get existing services
    existing_services = await get_all_services()
    existing_names = {service.get('name') for service in existing_services 
                      if service.get('category_id') == category_id}
    
    # Add each template service if it doesn't already exist
    added_count = 0
    for template in templates:
        service_name = template.get('service_name')
        if service_name not in existing_names:
            # Placeholder price of 0, admin will set the actual price later
            await add_service(
                name=service_name,
                description=template.get('description', ''),
                price=0,  # Default price 0
                duration=template.get('default_duration', 60),
                category_id=category_id
            )
            added_count += 1
    
    return {"success": True, "message": f"Добавлено {added_count} новых услуг в категорию '{category_name}'", "category_id": category_id}

async def add_template_services_to_category(category_name):
    """Add all template services for a category to the services table"""
    return await create_services_from_template(category_name)

# Initialize the template data
async def initialize_template_data():
    """Initialize template data with predefined categories and services"""
    templates = await get_sheet(TEMPLATES_SHEET)
    
    # Skip initialization if data already exists
    if templates:
        return
    
    template_data = [
        # Маникюр
        {"category_name": "Маникюр", "service_name": "Классический маникюр", 
         "description": "Традиционный маникюр с обработкой кутикулы", "default_duration": 40},
        {"category_name": "Маникюр", "service_name": "Аппаратный маникюр", 
         "description": "Аппаратный маникюр с использованием профессиональной фрезы", "default_duration": 50},
        {"category_name": "Маникюр", "service_name": "Комбинированный маникюр", 
         "description": "Комбинированный маникюр (аппаратный + классический)", "default_duration": 60},
        {"category_name": "Маникюр", "service_name": "Маникюр + покрытие гель-лак", 
         "description": "Маникюр с последующим покрытием гель-лаком", "default_duration": 90},
        {"category_name": "Маникюр", "service_name": "Укрепление ногтей (биогель/акрил)", 
         "description": "Укрепление ногтевой пластины биогелем или акрилом", "default_duration": 70},
        {"category_name": "Маникюр", "service_name": "Снятие гель-лака", 
         "description": "Бережное снятие гель-лака", "default_duration": 20},
        {"category_name": "Маникюр", "service_name": "Ремонт ногтя", 
         "description": "Ремонт сломанного ногтя", "default_duration": 15},
        {"category_name": "Маникюр", "service_name": "Дизайн 1-2 ногтя", 
         "description": "Художественное оформление 1-2 ногтей", "default_duration": 15},
        {"category_name": "Маникюр", "service_name": "Дизайн всех ногтей", 
         "description": "Художественное оформление всех ногтей", "default_duration": 30},
        
        # Педикюр
        {"category_name": "Педикюр", "service_name": "Классический педикюр", 
         "description": "Традиционный педикюр с обработкой кутикулы и стоп", "default_duration": 60},
        {"category_name": "Педикюр", "service_name": "Аппаратный педикюр", 
         "description": "Аппаратный педикюр с использованием профессиональной фрезы", "default_duration": 70},
        {"category_name": "Педикюр", "service_name": "Комбинированный педикюр", 
         "description": "Комбинированный педикюр (аппаратный + классический)", "default_duration": 80},
        {"category_name": "Педикюр", "service_name": "Педикюр + гель-лак", 
         "description": "Педикюр с последующим покрытием гель-лаком", "default_duration": 90},
        {"category_name": "Педикюр", "service_name": "Снятие покрытия", 
         "description": "Бережное снятие гель-лака с ногтей ног", "default_duration": 20},
        {"category_name": "Педикюр", "service_name": "Обработка трещин/мозолей", 
         "description": "Профессиональная обработка трещин и мозолей на стопах", "default_duration": 30},
        
        # Брови
        {"category_name": "Брови", "service_name": "Коррекция формы бровей", 
         "description": "Профессиональная коррекция формы бровей пинцетом", "default_duration": 30},
        {"category_name": "Брови", "service_name": "Окрашивание краской", 
         "description": "Окрашивание бровей профессиональной краской", "default_duration": 30},
        {"category_name": "Брови", "service_name": "Окрашивание хной", 
         "description": "Окрашивание бровей натуральной хной", "default_duration": 45},
        {"category_name": "Брови", "service_name": "Ламинирование бровей", 
         "description": "Ламинирование бровей для придания формы и объема", "default_duration": 60},
        {"category_name": "Брови", "service_name": "Архитектура бровей (комплекс)", 
         "description": "Комплексная услуга включающая коррекцию и окрашивание", "default_duration": 70},
        
        # Ресницы
        {"category_name": "Ресницы", "service_name": "Наращивание классика", 
         "description": "Классическое наращивание ресниц (1 к 1)", "default_duration": 120},
        {"category_name": "Ресницы", "service_name": "2D объем", 
         "description": "Наращивание ресниц с объемом 2D", "default_duration": 150},
        {"category_name": "Ресницы", "service_name": "3D объем", 
         "description": "Наращивание ресниц с объемом 3D", "default_duration": 180},
        {"category_name": "Ресницы", "service_name": "Мега-объем", 
         "description": "Наращивание ресниц с максимальным объемом", "default_duration": 210},
        {"category_name": "Ресницы", "service_name": "Снятие ресниц", 
         "description": "Бережное снятие нарощенных ресниц", "default_duration": 30},
        {"category_name": "Ресницы", "service_name": "Ламинирование ресниц", 
         "description": "Ламинирование натуральных ресниц для придания объема", "default_duration": 70},
        {"category_name": "Ресницы", "service_name": "Окрашивание ресниц", 
         "description": "Окрашивание ресниц профессиональной краской", "default_duration": 30},
        
        # Косметология / уход за лицом
        {"category_name": "Косметология", "service_name": "Чистка лица механическая", 
         "description": "Глубокая механическая чистка лица", "default_duration": 90},
        {"category_name": "Косметология", "service_name": "Чистка лица ультразвуковая", 
         "description": "Ультразвуковая чистка лица", "default_duration": 60},
        {"category_name": "Косметология", "service_name": "Чистка лица комбинированная", 
         "description": "Комбинированная чистка лица", "default_duration": 100},
        {"category_name": "Косметология", "service_name": "Пилинг", 
         "description": "Профессиональный химический пилинг", "default_duration": 45},
        {"category_name": "Косметология", "service_name": "Маска/уходовая процедура", 
         "description": "Профессиональная уходовая маска для лица", "default_duration": 40},
        {"category_name": "Косметология", "service_name": "Массаж лица", 
         "description": "Профессиональный массаж лица", "default_duration": 45},
        {"category_name": "Косметология", "service_name": "Карбокситерапия", 
         "description": "Омолаживающая процедура карбокситерапии", "default_duration": 50},
        {"category_name": "Косметология", "service_name": "Дарсонваль", 
         "description": "Процедура с использованием аппарата Дарсонваль", "default_duration": 30},
        
        # Массаж
        {"category_name": "Массаж", "service_name": "Классический массаж", 
         "description": "Классический общий массаж тела", "default_duration": 60},
        {"category_name": "Массаж", "service_name": "Антицеллюлитный массаж", 
         "description": "Интенсивный антицеллюлитный массаж", "default_duration": 60},
        {"category_name": "Массаж", "service_name": "Лимфодренажный массаж", 
         "description": "Лимфодренажный массаж для выведения жидкости", "default_duration": 70},
        {"category_name": "Массаж", "service_name": "Массаж спины", 
         "description": "Массаж спины и шейно-воротниковой зоны", "default_duration": 40},
        {"category_name": "Массаж", "service_name": "Массаж лица", 
         "description": "Профессиональный массаж лица", "default_duration": 30},
        {"category_name": "Массаж", "service_name": "Расслабляющий массаж", 
         "description": "Расслабляющий массаж всего тела", "default_duration": 90},
        
        # Парикмахерские услуги
        {"category_name": "Парикмахерские услуги", "service_name": "Женская стрижка", 
         "description": "Стрижка женская (мытье, сушка феном)", "default_duration": 60},
        {"category_name": "Парикмахерские услуги", "service_name": "Мужская стрижка", 
         "description": "Стрижка мужская (мытье, укладка)", "default_duration": 40},
        {"category_name": "Парикмахерские услуги", "service_name": "Детская стрижка", 
         "description": "Стрижка для детей до 10 лет", "default_duration": 30},
        {"category_name": "Парикмахерские услуги", "service_name": "Укладка", 
         "description": "Укладка волос (мытье, сушка феном)", "default_duration": 45},
        {"category_name": "Парикмахерские услуги", "service_name": "Окрашивание в один тон", 
         "description": "Окрашивание волос в один тон", "default_duration": 120},
        {"category_name": "Парикмахерские услуги", "service_name": "Мелирование", 
         "description": "Мелирование волос", "default_duration": 150},
        {"category_name": "Парикмахерские услуги", "service_name": "Балаяж", 
         "description": "Окрашивание волос в технике балаяж", "default_duration": 180},
        {"category_name": "Парикмахерские услуги", "service_name": "Ламинирование волос", 
         "description": "Ламинирование волос для блеска и защиты", "default_duration": 90},
        {"category_name": "Парикмахерские услуги", "service_name": "Кератиновое выпрямление", 
         "description": "Кератиновое выпрямление волос", "default_duration": 180},
        {"category_name": "Парикмахерские услуги", "service_name": "Ботокс для волос", 
         "description": "Процедура ботокса для восстановления волос", "default_duration": 120},
        
        # Депиляция / шугаринг
        {"category_name": "Депиляция", "service_name": "Ноги полностью", 
         "description": "Депиляция ног полностью", "default_duration": 70},
        {"category_name": "Депиляция", "service_name": "Ноги до колена", 
         "description": "Депиляция ног до колена", "default_duration": 40},
        {"category_name": "Депиляция", "service_name": "Руки полностью", 
         "description": "Депиляция рук полностью", "default_duration": 45},
        {"category_name": "Депиляция", "service_name": "Подмышечные впадины", 
         "description": "Депиляция подмышечных впадин", "default_duration": 20},
        {"category_name": "Депиляция", "service_name": "Бикини классическое", 
         "description": "Депиляция зоны классического бикини", "default_duration": 30},
        {"category_name": "Депиляция", "service_name": "Бикини глубокое", 
         "description": "Депиляция зоны глубокого бикини", "default_duration": 50},
        {"category_name": "Депиляция", "service_name": "Лицо", 
         "description": "Депиляция лица (верхняя губа, подбородок, щеки)", "default_duration": 30},
        {"category_name": "Депиляция", "service_name": "Мужская депиляция спины", 
         "description": "Депиляция мужской спины", "default_duration": 60},
        {"category_name": "Депиляция", "service_name": "Мужская депиляция груди", 
         "description": "Депиляция мужской груди", "default_duration": 50},
        {"category_name": "Депиляция", "service_name": "Уход после процедуры", 
         "description": "Успокаивающий уход после процедуры депиляции", "default_duration": 15}
    ]
    
    # Write template data to sheet
    await write_to_sheet(TEMPLATES_SHEET, template_data)
    
    return True
