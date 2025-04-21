
from utils.db_api.google_sheets import sheet, setup

async def get_all_services():
    """Get all available services"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting services: sheet is not initialized")
            return []
    
    try:
        services_sheet = sheet.worksheet('Services')
        # Get all records except header
        records = services_sheet.get_all_records()
        return records
    except Exception as e:
        print(f"Error getting services: {e}")
        return []

async def add_service(name, description, price):
    """Add a new service"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error adding service: sheet is not initialized")
            return None
    
    try:
        services_sheet = sheet.worksheet('Services')
        # Get all services to determine next ID
        services = await get_all_services()
        next_id = 1
        if services:
            # Find the maximum ID and increment by 1
            next_id = max(int(service.get('id', 0)) for service in services) + 1
        
        # Add the new service
        services_sheet.append_row([
            str(next_id),
            name,
            description,
            str(price)
        ])
        
        # Return the newly created service
        return {
            'id': next_id,
            'name': name,
            'description': description,
            'price': price
        }
    except Exception as e:
        print(f"Error adding service: {e}")
        return None

async def delete_service(service_id):
    """Delete a service by ID"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error deleting service: sheet is not initialized")
            return False
    
    try:
        services_sheet = sheet.worksheet('Services')
        # Find the service by ID
        cell = services_sheet.find(str(service_id), in_column=1)
        if cell:
            services_sheet.delete_row(cell.row)
            return True
        return False
    except Exception as e:
        print(f"Error deleting service: {e}")
        return False

async def update_service(service_id, name=None, description=None, price=None):
    """Update service details"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error updating service: sheet is not initialized")
            return False
    
    try:
        services_sheet = sheet.worksheet('Services')
        # Find the service by ID
        cell = services_sheet.find(str(service_id), in_column=1)
        if not cell:
            return False
        
        row = cell.row
        if name is not None:
            services_sheet.update_cell(row, 2, name)
        if description is not None:
            services_sheet.update_cell(row, 3, description)
        if price is not None:
            services_sheet.update_cell(row, 4, str(price))
        
        return True
    except Exception as e:
        print(f"Error updating service: {e}")
        return False
