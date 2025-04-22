
from utils.db_api.google_sheets import sheet, setup

def standardize_service(service):
    """Standardize service keys to lowercase without spaces"""
    standardized = {}
    # Map from possible variants to standardized keys
    key_mapping = {
        'id': 'id',
        'Service ID': 'id',
        'name': 'name',
        'Name': 'name',
        'description': 'description',
        'Description': 'description',
        'price': 'price',
        'Price': 'price',
        'duration': 'duration',
        'Duration': 'duration'
    }
    
    for key, value in service.items():
        if key in key_mapping:
            standardized[key_mapping[key]] = value
    
    # Set default duration if not present
    if 'duration' not in standardized:
        standardized['duration'] = '60'
        
    return standardized

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
        
        # Debug info
        if records and len(records) > 0:
            print(f"Service record keys: {list(records[0].keys())}")
        
        # Standardize all records
        standardized_services = [standardize_service(record) for record in records]
        return standardized_services
    except Exception as e:
        print(f"Error getting services: {e}")
        return []

async def add_service(name, description, price, duration=60):
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
        
        # Convert duration to string
        duration_str = str(duration)
        
        # Add the new service
        services_sheet.append_row([
            str(next_id),
            name,
            description,
            str(price),
            duration_str
        ])
        
        # Return the newly created service
        return {
            'id': next_id,
            'name': name,
            'description': description,
            'price': price,
            'duration': duration_str
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

async def update_service(service_id, name=None, description=None, price=None, duration=None):
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
        if duration is not None:
            services_sheet.update_cell(row, 5, str(duration))
        
        return True
    except Exception as e:
        print(f"Error updating service: {e}")
        return False

async def get_service(service_id):
    """Get service by ID"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting service: sheet is not initialized")
            return None
    
    try:
        services_sheet = sheet.worksheet('Services')
        # Find the service by ID
        cell = services_sheet.find(str(service_id), in_column=1)
        if not cell:
            return None
        
        # Get the row values
        row = services_sheet.row_values(cell.row)
        
        # Check that we have enough values
        if len(row) < 4:
            print(f"Warning: Service {service_id} has incomplete data: {row}")
            return None
        
        # Set default duration if not present
        duration = "60"
        if len(row) >= 5:
            duration = row[4]
            
        return {
            'id': row[0],
            'name': row[1],
            'description': row[2],
            'price': row[3],
            'duration': duration
        }
    except Exception as e:
        print(f"Error getting service: {e}")
        return None

async def get_services_by_master(master_id):
    """Get services offered by a specific master"""
    # In the current implementation, all masters offer all services
    # This can be extended in the future to support master-specific services
    return await get_all_services()
