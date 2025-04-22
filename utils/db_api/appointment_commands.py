
from utils.db_api.google_sheets import sheet, setup
from datetime import datetime

def standardize_appointment(appointment):
    """Standardize appointment keys to lowercase without spaces"""
    standardized = {}
    # Map from possible variants to standardized keys
    key_mapping = {
        'id': 'id',
        'Appointment ID': 'id',
        'user_id': 'user_id',
        'User ID': 'user_id',
        'service_id': 'service_id',
        'Service ID': 'service_id',
        'date': 'date',
        'Date': 'date',
        'time': 'time',
        'Time': 'time',
        'status': 'status',
        'Status': 'status'
    }
    
    for key, value in appointment.items():
        if key in key_mapping:
            standardized[key_mapping[key]] = value
    
    return standardized

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
        
        # Debug information
        if records:
            print(f"Looking for appointments for user_id: {user_id}, type: {type(user_id)}")
            first_record = records[0]
            print(f"First appointment record: {first_record}")
            
            # Standardize records
            standardized_records = [standardize_appointment(record) for record in records]
            
            # Filter records for the specific user
            user_appointments = []
            for appointment in standardized_records:
                appt_user_id = appointment.get('user_id')
                # Convert both to string for comparison to avoid type issues
                if str(appt_user_id) == str(user_id):
                    user_appointments.append(appointment)
            
            print(f"Found {len(user_appointments)} appointments for user {user_id}")
            return user_appointments
        return []
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
        
        # Standardize all records
        standardized_records = [standardize_appointment(record) for record in records]
        return standardized_records
    except Exception as e:
        print(f"Error getting all appointments: {e}")
        return []

async def add_appointment(user_id, service_id, date, time):
    """Add a new appointment"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error adding appointment: sheet is not initialized")
            return None
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Get all appointments to determine next ID
        appointments = await get_all_appointments()
        next_id = 1
        if appointments:
            # Find the maximum ID and increment by 1
            next_id = max(int(appointment.get('id', 0)) for appointment in appointments) + 1
        
        # Add the new appointment with "confirmed" status by default
        appointments_sheet.append_row([
            str(next_id),
            str(user_id),
            str(service_id),
            date,
            time,
            "confirmed"
        ])
        
        # Add to history
        try:
            history_sheet = sheet.worksheet('History')
            # Get service price for the history record
            services_sheet = sheet.worksheet('Services')
            service_cell = services_sheet.find(str(service_id), in_column=1)
            price = "0"
            if service_cell:
                price = services_sheet.cell(service_cell.row, 4).value
            
            # Add to history
            history_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(user_id),
                str(service_id),
                date,
                time,
                price
            ])
        except Exception as e:
            print(f"Error adding to history: {e}")
        
        # Return the newly created appointment
        return {
            'id': next_id,
            'user_id': user_id,
            'service_id': service_id,
            'date': date,
            'time': time,
            'status': "confirmed"
        }
    except Exception as e:
        print(f"Error adding appointment: {e}")
        return None

async def update_appointment_status(appointment_id, new_status):
    """Update appointment status"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error updating appointment: sheet is not initialized")
            return False
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Find the appointment by ID
        cell = appointments_sheet.find(str(appointment_id), in_column=1)
        if not cell:
            print(f"Appointment {appointment_id} not found")
            return False
        
        # Update the status (column 6)
        print(f"Updating appointment {appointment_id} status to {new_status}")
        appointments_sheet.update_cell(cell.row, 6, new_status)
        return True
    except Exception as e:
        print(f"Error updating appointment: {e}")
        return False

async def get_appointment(appointment_id):
    """Get appointment by ID"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting appointment: sheet is not initialized")
            return None
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Find the appointment by ID
        cell = appointments_sheet.find(str(appointment_id), in_column=1)
        if not cell:
            return None
        
        # Get the row values
        row = appointments_sheet.row_values(cell.row)
        
        # Check that we have enough values
        if len(row) < 6:
            print(f"Warning: Appointment {appointment_id} has incomplete data: {row}")
            return None
            
        return {
            'id': row[0],
            'user_id': row[1],
            'service_id': row[2],
            'date': row[3],
            'time': row[4],
            'status': row[5]
        }
    except Exception as e:
        print(f"Error getting appointment: {e}")
        return None

# Debug function for tracing appointment issues
async def debug_appointment_data():
    """Print debug information about appointments"""
    global sheet
    if sheet is None:
        sheet = await setup()
        
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        records = appointments_sheet.get_all_records()
        
        print("==== DEBUG: APPOINTMENT DATA ====")
        print(f"Total records: {len(records)}")
        if records:
            print(f"First record keys: {list(records[0].keys())}")
            print(f"First record: {records[0]}")
            
            # Test standardization
            std_record = standardize_appointment(records[0])
            print(f"Standardized first record: {std_record}")
        else:
            print("No appointment records found")
        print("=================================")
        
        return records
    except Exception as e:
        print(f"Error debugging appointments: {e}")
        return []
