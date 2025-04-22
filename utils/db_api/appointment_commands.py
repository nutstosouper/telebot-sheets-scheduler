
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
        'Status': 'status',
        'master_id': 'master_id',
        'Master ID': 'master_id',
        'payment_method': 'payment_method',
        'Payment Method': 'payment_method'
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

async def get_master_appointments(master_id):
    """Get all appointments for a specific master"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting master appointments: sheet is not initialized")
            return []
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Get all records
        records = appointments_sheet.get_all_records()
        
        # Standardize records
        standardized_records = [standardize_appointment(record) for record in records]
        
        # Filter records for the specific master
        master_appointments = []
        for appointment in standardized_records:
            appt_master_id = appointment.get('master_id')
            # Convert both to string for comparison to avoid type issues
            if appt_master_id and str(appt_master_id) == str(master_id):
                master_appointments.append(appointment)
        
        return master_appointments
    except Exception as e:
        print(f"Error getting master appointments: {e}")
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

async def add_appointment(user_id, service_id, date, time, master_id=None, payment_method='cash'):
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
        
        # Prepare row data
        row_data = [
            str(next_id),
            str(user_id),
            str(service_id),
            date,
            time,
            "confirmed"  # Default status
        ]
        
        # Add master_id if provided
        if master_id:
            row_data.append(str(master_id))
        else:
            row_data.append("")  # Empty master_id
        
        # Add payment_method
        row_data.append(payment_method)
        
        # Add the new appointment
        appointments_sheet.append_row(row_data)
        
        # Add to history
        try:
            history_sheet = sheet.worksheet('History')
            # Get service price for the history record
            services_sheet = sheet.worksheet('Services')
            service_cell = services_sheet.find(str(service_id), in_column=1)
            price = "0"
            if service_cell:
                price = services_sheet.cell(service_cell.row, 4).value
            
            # Prepare history row data
            history_row = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(user_id),
                str(service_id),
                date,
                time,
                price
            ]
            
            # Add master_id if provided
            if master_id:
                history_row.append(str(master_id))
            else:
                history_row.append("")  # Empty master_id
            
            # Add payment_method
            history_row.append(payment_method)
            
            # Add to history
            history_sheet.append_row(history_row)
        except Exception as e:
            print(f"Error adding to history: {e}")
        
        # Return the newly created appointment
        appointment = {
            'id': next_id,
            'user_id': user_id,
            'service_id': service_id,
            'date': date,
            'time': time,
            'status': "confirmed"
        }
        
        # Add master_id if provided
        if master_id:
            appointment['master_id'] = master_id
        
        # Add payment_method
        appointment['payment_method'] = payment_method
        
        return appointment
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

async def update_appointment_payment_method(appointment_id, payment_method):
    """Update appointment payment method"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error updating appointment payment: sheet is not initialized")
            return False
    
    try:
        appointments_sheet = sheet.worksheet('Appointments')
        # Find the appointment by ID
        cell = appointments_sheet.find(str(appointment_id), in_column=1)
        if not cell:
            print(f"Appointment {appointment_id} not found")
            return False
        
        # Update the payment method (column 8)
        print(f"Updating appointment {appointment_id} payment method to {payment_method}")
        appointments_sheet.update_cell(cell.row, 8, payment_method)
        return True
    except Exception as e:
        print(f"Error updating appointment payment: {e}")
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
        
        # Create appointment dict with standard keys
        appointment = {
            'id': row[0],
            'user_id': row[1],
            'service_id': row[2],
            'date': row[3],
            'time': row[4],
            'status': row[5]
        }
        
        # Add master_id if available
        if len(row) > 6:
            appointment['master_id'] = row[6]
        
        # Add payment_method if available
        if len(row) > 7:
            appointment['payment_method'] = row[7]
        else:
            appointment['payment_method'] = 'cash'  # Default
            
        return appointment
    except Exception as e:
        print(f"Error getting appointment: {e}")
        return None

async def get_appointments_by_date_range(start_date, end_date, master_id=None):
    """Get appointments within a date range, optionally filtered by master"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting appointments by date range: sheet is not initialized")
            return []
    
    try:
        # Get all appointments
        all_appointments = await get_all_appointments()
        
        # Filter by date range
        filtered_appointments = []
        for appointment in all_appointments:
            appt_date = appointment.get('date', '')
            
            # Skip if date is missing
            if not appt_date:
                continue
                
            # Check if date is within range
            if start_date <= appt_date <= end_date:
                # Filter by master if specified
                if master_id is None or str(appointment.get('master_id', '')) == str(master_id):
                    filtered_appointments.append(appointment)
        
        return filtered_appointments
    except Exception as e:
        print(f"Error getting appointments by date range: {e}")
        return []

async def get_appointment_statistics(start_date=None, end_date=None, master_id=None):
    """Get appointment statistics for a date range and/or master"""
    global sheet
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            print(f"Error getting appointment statistics: sheet is not initialized")
            return {}
    
    try:
        # Get appointments based on filters
        appointments = []
        if start_date and end_date:
            appointments = await get_appointments_by_date_range(start_date, end_date, master_id)
        elif master_id:
            appointments = await get_master_appointments(master_id)
        else:
            appointments = await get_all_appointments()
        
        # Initialize statistics
        stats = {
            'total': len(appointments),
            'confirmed': 0,
            'canceled': 0,
            'completed': 0,
            'paid': 0,
            'revenue': 0,
            'by_payment_method': {
                'cash': 0,
                'card': 0,
                'transfer': 0,
                'other': 0
            }
        }
        
        # Process each appointment
        for appointment in appointments:
            status = appointment.get('status', '')
            payment_method = appointment.get('payment_method', 'other')
            
            # Count by status
            if status == 'confirmed':
                stats['confirmed'] += 1
            elif status == 'canceled':
                stats['canceled'] += 1
            elif status == 'completed':
                stats['completed'] += 1
            elif status == 'paid':
                stats['paid'] += 1
            
            # Count by payment method
            if payment_method in stats['by_payment_method']:
                stats['by_payment_method'][payment_method] += 1
            else:
                stats['by_payment_method']['other'] += 1
            
            # Calculate revenue for completed and paid appointments
            if status in ['completed', 'paid']:
                # Get service price
                service_id = appointment.get('service_id')
                if service_id:
                    try:
                        services_sheet = sheet.worksheet('Services')
                        service_cell = services_sheet.find(str(service_id), in_column=1)
                        if service_cell:
                            price_str = services_sheet.cell(service_cell.row, 4).value
                            try:
                                price = float(price_str)
                                stats['revenue'] += price
                            except (ValueError, TypeError):
                                pass  # Skip if price is not a valid number
                    except Exception as e:
                        print(f"Error getting service price: {e}")
        
        return stats
    except Exception as e:
        print(f"Error calculating appointment statistics: {e}")
        return {}

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
