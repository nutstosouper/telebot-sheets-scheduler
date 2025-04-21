
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
        # Filter records for the specific user
        user_appointments = [
            appointment for appointment in records 
            if str(appointment.get('user_id', '')) == str(user_id)
        ]
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
        return records
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
            return False
        
        # Update the status (column 6)
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
