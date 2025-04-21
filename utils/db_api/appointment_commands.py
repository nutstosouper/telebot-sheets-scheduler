
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
            print(f"Available keys in first record: {list(records[0].keys())}")
        
        # Filter records for the specific user with support for both column naming formats
        user_appointments = []
        for appointment in records:
            # Handle potential different column naming conventions
            appointment_user_id = None
            
            # Check various possible column names for user ID
            if 'user_id' in appointment:
                appointment_user_id = appointment.get('user_id')
            elif 'User ID' in appointment:
                appointment_user_id = appointment.get('User ID')
            elif 'User_ID' in appointment:
                appointment_user_id = appointment.get('User_ID')
            
            # Check if we got a user ID and compare as strings
            if appointment_user_id is not None:
                # Convert both to strings for comparison to avoid type mismatch
                if str(appointment_user_id) == str(user_id):
                    # Create a standardized appointment object
                    standardized_appointment = standardize_appointment(appointment)
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
        
        # Print keys in the first record for debugging
        if records and len(records) > 0:
            print(f"Appointment record keys: {list(records[0].keys())}")
        
        # Standardize all appointment records
        standardized_records = []
        for appointment in records:
            standardized_records.append(standardize_appointment(appointment))
            
        return standardized_records
    except Exception as e:
        print(f"Error getting all appointments: {e}")
        return []

def standardize_appointment(appointment):
    """Standardize appointment object with consistent keys"""
    # Check for 'id' or 'Appointment ID' or 'Appointment_ID'
    appointment_id = appointment.get('id', appointment.get('Appointment ID', appointment.get('Appointment_ID', '')))
    
    # Check for 'user_id' or 'User ID' or 'User_ID'
    user_id = appointment.get('user_id', appointment.get('User ID', appointment.get('User_ID', '')))
    
    # Check for 'service_id' or 'Service ID' or 'Service_ID'
    service_id = appointment.get('service_id', appointment.get('Service ID', appointment.get('Service_ID', '')))
    
    # Check for 'date' or 'Date'
    date = appointment.get('date', appointment.get('Date', ''))
    
    # Check for 'time' or 'Time'
    time = appointment.get('time', appointment.get('Time', ''))
    
    # Check for 'status' or 'Status'
    status = appointment.get('status', appointment.get('Status', 'confirmed'))
    
    return {
        'id': appointment_id,
        'user_id': user_id,
        'service_id': service_id,
        'date': date,
        'time': time,
        'status': status
    }

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
            # Print the first record for debugging
            first_record = records[0]
            
            # Try accessing with different key formats
            id_value = first_record.get('id', first_record.get('Appointment ID', 'Not found'))
            user_id_value = first_record.get('user_id', first_record.get('User ID', 'Not found'))
            
            return f"Header: {header}\nSample data (up to 5 rows): {sample_data}\nRecord keys: {record_keys}\nFirst ID value: {id_value}\nFirst User ID value: {user_id_value}"
        
        return f"Header: {header}\nSample data (up to 5 rows): {sample_data}\nRecord keys: {record_keys}"
    except Exception as e:
        return f"Error checking appointments structure: {e}"
