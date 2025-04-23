
from utils.db_api.google_sheets import get_sheet, write_to_sheet

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

async def add_template_services_to_category(category_name):
    """Add all template services for a category to the services table"""
    # Get category by name or create it
    category = await get_category_by_name(category_name)
    if not category:
        category = await add_category(category_name)
    
    if not category:
        return False, "Не удалось создать категорию"
    
    category_id = category.get('id')
    
    # Get template services for this category
    templates = await get_template_services_by_category(category_name)
    if not templates:
        return False, f"Шаблоны услуг для категории '{category_name}' не найдены"
    
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
    
    return True, f"Добавлено {added_count} новых услуг в категорию '{category_name}'"
