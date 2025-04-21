
from utils.db_api.google_sheets import sheet, setup
from datetime import datetime

async def get_user_appointments(user_id):
    """Get all appointments for a specific user"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting appointments: sheet is not initialized")
            return []
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Get all records
        records = appointments_sheet.get_all_records()
        
        # Debug: Print user_id and first few appointments to check format
        print(f"Looking for appointments for user_id: {user_id}, type: {type(user_id)}")
        if records and len(records) > 0:
            print(f"First appointment record: {records[0]}")
            # Check if we have the new column format (with spaces) or the old format
            if 'User ID' in records[0]:
                print(f"First appointment user_id: {records[0].get('User ID')}, type: {type(records[0].get('User ID'))}")
            else:
                print(f"First appointment user_id: {records[0].get('user_id')}, type: {type(records[0].get('user_id'))}")
        
        # Filter records for the specific user with support for both column naming formats
        user_appointments = []
        for appointment in records:
            # Handle potential different column naming conventions
            appointment_user_id = None
            if 'user_id' in appointment:
                appointment_user_id = appointment.get('user_id')
            elif 'User ID' in appointment:
                appointment_user_id = appointment.get('User ID')
            
            # Convert both to strings for comparison to avoid type mismatch
            if appointment_user_id is not None and str(appointment_user_id) == str(user_id):
                # Create a standardized appointment object regardless of original column names
                standardized_appointment = {
                    'id': appointment.get('id', appointment.get('Appointment ID', '')),
                    'user_id': appointment_user_id,
                    'service_id': appointment.get('service_id', appointment.get('Service ID', '')),
                    'date': appointment.get('date', appointment.get('Date', '')),
                    'time': appointment.get('time', appointment.get('Time', '')),
                    'status': appointment.get('status', appointment.get('Status', 'confirmed'))
                }
                user_appointments.append(standardized_appointment)
        
        print(f"Found {len(user_appointments)} appointments for user {user_id}")
        return user_appointments
    except Exception as e:
        print(f"Error getting appointments: {e}")
        return []

async def get_all_appointments():
    """Get all appointments"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting all appointments: sheet is not initialized")
            return []
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Get all records except header
        records = appointments_sheet.get_all_records()
        
        # Standardize appointment records
        standardized_records = []
        for appointment in records:
            standardized_appointment = {
                'id': appointment.get('id', appointment.get('Appointment ID', '')),
                'user_id': appointment.get('user_id', appointment.get('User ID', '')),
                'service_id': appointment.get('service_id', appointment.get('Service ID', '')),
                'date': appointment.get('date', appointment.get('Date', '')),
                'time': appointment.get('time', appointment.get('Time', '')),
                'status': appointment.get('status', appointment.get('Status', 'confirmed'))
            }
            standardized_records.append(standardized_appointment)
            
        return standardized_records
    except Exception as e:
        print(f"Error getting all appointments: {e}")
        return []

# ... keep existing code (add_appointment, update_appointment_status, get_appointment functions)

# Updated debug function to check the structure of the Appointments worksheet
async def debug_appointments_structure():
    """Debug function to check the Appointments worksheet structure"""
    global sheet
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            return "Error: sheet is not initialized"
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Get all values including header
        all_values = appointments_sheet.get_all_values()
        
        if not all_values:
            return "Appointments worksheet is empty"
        
        # Get header (column names)
        header = all_values[0]
        
        # Get sample data
        sample_data = [row for row in all_values[1:6]] if len(all_values) > 1 else ["No data"]
        
        # Get all records to check dictionary keys
        records = appointments_sheet.get_all_records()
        record_keys = "No records found"
        if records and len(records) > 0:
            record_keys = list(records[0].keys())
        
        return f"Header: {header}\nSample data (up to 5 rows): {sample_data}\nRecord keys: {record_keys}"
    except Exception as e:
        return f"Error checking appointments structure: {e}"
