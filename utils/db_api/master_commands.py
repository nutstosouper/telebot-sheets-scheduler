
# This file includes functions for working with master data
from utils.db_api.google_sheets import get_sheet, write_to_sheet
from datetime import datetime, timedelta

# Sheet name for masters
MASTERS_SHEET = "Masters"

async def get_all_masters():
    """Get all masters from the database"""
    masters = await get_sheet(MASTERS_SHEET)
    return masters

async def get_masters():
    """Alias for get_all_masters"""
    return await get_all_masters()

async def get_master(master_id):
    """Get a master by their ID"""
    masters = await get_all_masters()
    for master in masters:
        if master.get('id') == master_id:
            return master
    return None

async def get_master_by_telegram_id(telegram_id):
    """Get a master by their Telegram ID"""
    masters = await get_all_masters()
    for master in masters:
        if str(master.get('telegram_id')) == str(telegram_id):
            return master
    return None

async def get_master_by_username(username):
    """Get a master by their Telegram username"""
    if not username:
        return None
        
    # Normalize username (remove @ if present)
    if username.startswith('@'):
        username = username[1:]
        
    masters = await get_all_masters()
    for master in masters:
        master_username = master.get('telegram')
        if master_username:
            if master_username.startswith('@'):
                master_username = master_username[1:]
            if master_username.lower() == username.lower():
                return master
    return None

async def add_master(name, telegram_id=None, phone=None, specialties=None, telegram=None, location=None, description=None):
    """Add a new master to the database"""
    masters = await get_all_masters()
    
    # Check if master with this Telegram ID already exists
    if telegram_id:
        for master in masters:
            if str(master.get('telegram_id')) == str(telegram_id):
                return master
    
    # Generate a new ID
    new_id = "1"
    if masters:
        new_id = str(max([int(master.get('id', 0)) for master in masters]) + 1)
    
    # Create new master
    new_master = {
        'id': new_id,
        'name': name
    }
    
    # Add optional fields if provided
    if telegram_id:
        new_master['telegram_id'] = telegram_id
    if phone:
        new_master['phone'] = phone
    if specialties:
        new_master['specialties'] = specialties
    if telegram:
        new_master['telegram'] = telegram
    if location:
        new_master['location'] = location
    if description:
        new_master['description'] = description
    
    # Add to sheet
    masters.append(new_master)
    await write_to_sheet(MASTERS_SHEET, masters)
    
    return new_master

async def update_master(master_id, name=None, telegram_id=None, phone=None, specialties=None, telegram=None, location=None, description=None):
    """Update a master in the database"""
    masters = await get_all_masters()
    updated = False
    
    for i, master in enumerate(masters):
        if master.get('id') == master_id:
            # Update fields if provided
            if name is not None:
                masters[i]['name'] = name
            if telegram_id is not None:
                masters[i]['telegram_id'] = telegram_id
            if phone is not None:
                masters[i]['phone'] = phone
            if specialties is not None:
                masters[i]['specialties'] = specialties
            if telegram is not None:
                masters[i]['telegram'] = telegram
            if location is not None:
                masters[i]['location'] = location
            if description is not None:
                masters[i]['description'] = description
            
            updated = True
            break
    
    if updated:
        await write_to_sheet(MASTERS_SHEET, masters)
    
    return updated

async def delete_master(master_id):
    """Delete a master from the database"""
    masters = await get_all_masters()
    
    # Filter out the master to delete
    updated_masters = [master for master in masters if master.get('id') != master_id]
    
    # Check if a master was removed
    if len(updated_masters) < len(masters):
        await write_to_sheet(MASTERS_SHEET, updated_masters)
        return True
    
    return False

# Working hours functions
async def get_master_working_hours(master_id):
    """Get working hours for a specific master"""
    master = await get_master(master_id)
    if not master:
        return {}
    
    working_hours = master.get('working_hours')
    if not working_hours:
        # Default working hours (10:00 - 19:00 every day)
        return {
            "1": {"start": "10:00", "end": "19:00"},  # Monday
            "2": {"start": "10:00", "end": "19:00"},  # Tuesday
            "3": {"start": "10:00", "end": "19:00"},  # Wednesday
            "4": {"start": "10:00", "end": "19:00"},  # Thursday
            "5": {"start": "10:00", "end": "19:00"},  # Friday
            "6": {"start": "10:00", "end": "19:00"},  # Saturday
            "7": {"start": "10:00", "end": "19:00"}   # Sunday
        }
    
    # Parse working hours from string if needed
    if isinstance(working_hours, str):
        try:
            import json
            return json.loads(working_hours)
        except:
            return {}
    
    return working_hours

async def update_master_working_hours(master_id, working_hours):
    """Update working hours for a specific master"""
    masters = await get_all_masters()
    updated = False
    
    for i, master in enumerate(masters):
        if master.get('id') == master_id:
            # Convert to string for storage if needed
            if not isinstance(working_hours, str):
                import json
                working_hours = json.dumps(working_hours)
            
            masters[i]['working_hours'] = working_hours
            updated = True
            break
    
    if updated:
        await write_to_sheet(MASTERS_SHEET, masters)
        return True
    
    return False

# Service association functions
async def get_master_services(master_id):
    """Get services associated with a specific master"""
    master = await get_master(master_id)
    if not master:
        return []
    
    services = master.get('services')
    if not services:
        return []
    
    # Parse services from string if needed
    if isinstance(services, str):
        try:
            import json
            return json.loads(services)
        except:
            return []
    
    return services

async def update_master_services(master_id, service_ids):
    """Update services associated with a specific master"""
    masters = await get_all_masters()
    updated = False
    
    for i, master in enumerate(masters):
        if master.get('id') == master_id:
            # Convert to string for storage if needed
            if not isinstance(service_ids, str):
                import json
                service_ids = json.dumps(service_ids)
            
            masters[i]['services'] = service_ids
            updated = True
            break
    
    if updated:
        await write_to_sheet(MASTERS_SHEET, masters)
        return True
    
    return False

# Availability functions
async def get_master_availability(master_id, date):
    """Get availability for a specific master on a specific date"""
    # This is a placeholder implementation
    # In a real application, this would check the master's working hours,
    # existing appointments, and any other factors that affect availability
    
    # Get master's working hours
    working_hours = await get_master_working_hours(master_id)
    
    # Get day of week (1-7, Monday=1)
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_of_week = str(date_obj.isoweekday())
    except:
        return []
    
    # Check if master works on this day
    if day_of_week not in working_hours:
        return []
    
    # Get start and end hours
    hours = working_hours.get(day_of_week)
    if not hours:
        return []
    
    start_time = hours.get('start', '10:00')
    end_time = hours.get('end', '19:00')
    
    # Parse times
    start_hour, start_minute = map(int, start_time.split(':'))
    end_hour, end_minute = map(int, end_time.split(':'))
    
    # Generate time slots every 30 minutes
    time_slots = []
    current = datetime(date_obj.year, date_obj.month, date_obj.day, start_hour, start_minute)
    end = datetime(date_obj.year, date_obj.month, date_obj.day, end_hour, end_minute)
    
    while current < end:
        time_slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=30)
    
    # Filter out already booked time slots
    # (would need appointment data from database)
    
    return time_slots
