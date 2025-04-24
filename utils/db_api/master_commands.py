
from utils.db_api.google_sheets import sheet, setup
import json

def standardize_master(master):
    """Standardize master keys to lowercase without spaces"""
    standardized = {}
    # Map from possible variants to standardized keys
    key_mapping = {
        'id': 'id',
        'Master ID': 'id',
        'user_id': 'user_id',
        'User ID': 'user_id',
        'name': 'name',
        'Name': 'name',
        'telegram': 'telegram',
        'Telegram': 'telegram',
        'address': 'address',
        'Address': 'address',
        'location': 'location',
        'Location': 'location',
        'notification_enabled': 'notification_enabled',
        'Notification Enabled': 'notification_enabled',
        'work_hours': 'work_hours',
        'Work Hours': 'work_hours'
    }
    
    for key, value in master.items():
        if key in key_mapping:
            standardized[key_mapping[key]] = value
    
    return standardized

async def get_all_masters():
    """Get all registered masters"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting masters: sheet is not initialized")
            return []
    
    try:
        masters_sheet = sheet.worksheet('Masters')
        # Get all records
        records = masters_sheet.get_all_records()
        
        # Standardize all records
        standardized_masters = [standardize_master(record) for record in records]
        return standardized_masters
    except Exception as e:
        print(f"Error getting masters: {e}")
        return []

async def get_masters():
    """Alias for get_all_masters"""
    return await get_all_masters()

async def get_master(master_id):
    """Get master by ID"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting master: sheet is not initialized")
            return None
    
    try:
        masters_sheet = sheet.worksheet('Masters')
        # Find the master by ID
        cell = masters_sheet.find(str(master_id), in_column=1)
        if not cell:
            return None
        
        # Get the row values
        row = masters_sheet.row_values(cell.row)
        
        # Check that we have enough values
        if len(row) < 7:
            print(f"Warning: Master {master_id} has incomplete data: {row}")
            return None
            
        return {
            'id': row[0],
            'user_id': row[1],
            'name': row[2],
            'telegram': row[3],
            'address': row[4],
            'location': row[5],
            'notification_enabled': row[6],
            'work_hours': row[7] if len(row) > 7 else "{}" 
        }
    except Exception as e:
        print(f"Error getting master: {e}")
        return None

async def add_master(user_id, name, telegram, address="", location="", notification_enabled=True):
    """Add a new master"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error adding master: sheet is not initialized")
            return None
    
    try:
        masters_sheet = sheet.worksheet('Masters')
        # Get all masters to determine next ID
        masters = await get_all_masters()
        next_id = 1
        if masters:
            # Find the maximum ID and increment by 1
            next_id = max(int(master.get('id', 0)) for master in masters) + 1
        
        # Default work hours
        default_work_hours = json.dumps({
            "Monday": {"start": "09:00", "end": "18:00", "enabled": True},
            "Tuesday": {"start": "09:00", "end": "18:00", "enabled": True},
            "Wednesday": {"start": "09:00", "end": "18:00", "enabled": True},
            "Thursday": {"start": "09:00", "end": "18:00", "enabled": True},
            "Friday": {"start": "09:00", "end": "18:00", "enabled": True},
            "Saturday": {"start": "10:00", "end": "16:00", "enabled": True},
            "Sunday": {"start": "10:00", "end": "16:00", "enabled": False}
        })
        
        # Add the new master
        masters_sheet.append_row([
            str(next_id),
            str(user_id),
            name,
            telegram,
            address,
            location,
            "true" if notification_enabled else "false",
            default_work_hours
        ])
        
        # Return the newly created master
        return {
            'id': next_id,
            'user_id': user_id,
            'name': name,
            'telegram': telegram,
            'address': address,
            'location': location,
            'notification_enabled': notification_enabled,
            'work_hours': default_work_hours
        }
    except Exception as e:
        print(f"Error adding master: {e}")
        return None

async def update_master(master_id, name=None, telegram=None, address=None, location=None, notification_enabled=None, work_hours=None):
    """Update master details"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error updating master: sheet is not initialized")
            return False
    
    try:
        masters_sheet = sheet.worksheet('Masters')
        # Find the master by ID
        cell = masters_sheet.find(str(master_id), in_column=1)
        if not cell:
            return False
        
        row = cell.row
        if name is not None:
            masters_sheet.update_cell(row, 3, name)
        if telegram is not None:
            masters_sheet.update_cell(row, 4, telegram)
        if address is not None:
            masters_sheet.update_cell(row, 5, address)
        if location is not None:
            masters_sheet.update_cell(row, 6, location)
        if notification_enabled is not None:
            masters_sheet.update_cell(row, 7, "true" if notification_enabled else "false")
        if work_hours is not None:
            if isinstance(work_hours, dict):
                work_hours = json.dumps(work_hours)
            masters_sheet.update_cell(row, 8, work_hours)
        
        return True
    except Exception as e:
        print(f"Error updating master: {e}")
        return False

async def get_master_by_user_id(user_id):
    """Get master by user ID"""
    masters = await get_all_masters()
    for master in masters:
        if str(master.get('user_id', '')) == str(user_id):
            return master
    return None

async def is_master(user_id):
    """Check if user is a master"""
    master = await get_master_by_user_id(user_id)
    return master is not None

async def get_master_working_hours(master_id):
    """Get master's working hours"""
    master = await get_master(master_id)
    if not master:
        return None
    
    work_hours = master.get('work_hours', '{}')
    if isinstance(work_hours, str):
        try:
            return json.loads(work_hours)
        except:
            return {}
    return work_hours

async def set_master_working_hours(master_id, day, start=None, end=None, enabled=None):
    """Update master's working hours for a specific day"""
    work_hours = await get_master_working_hours(master_id)
    if not work_hours:
        work_hours = {}
    
    if day not in work_hours:
        work_hours[day] = {"start": "09:00", "end": "18:00", "enabled": True}
    
    if start is not None:
        work_hours[day]["start"] = start
    if end is not None:
        work_hours[day]["end"] = end
    if enabled is not None:
        work_hours[day]["enabled"] = enabled
    
    return await update_master(master_id, work_hours=work_hours)
