
from utils.db_api.google_sheets import get_sheet, write_to_sheet
from utils.db_api.service_commands import get_service, get_offer
from utils.db_api.master_commands import get_master
import utils.db_api.user_commands as user_commands

# Sheet name
APPOINTMENTS_SHEET = "Appointments"
VERIFIED_USERS_SHEET = "VerifiedUsers"

async def get_all_appointments():
    """Get all appointments from the database"""
    appointments = await get_sheet(APPOINTMENTS_SHEET)
    return appointments

async def get_appointment(appointment_id):
    """Get an appointment by its ID"""
    appointments = await get_all_appointments()
    for appointment in appointments:
        if appointment.get('id') == appointment_id:
            return appointment
    return None

async def get_user_appointments(user_id):
    """Get all appointments for a specific user"""
    appointments = await get_all_appointments()
    user_appointments = []
    
    for appointment in appointments:
        if str(appointment.get('user_id')) == str(user_id):
            # Add service and master info to appointment
            service_id = appointment.get('service_id')
            if service_id:
                # First try to get as a regular service
                service = await get_service(service_id)
                if not service:
                    # If not a regular service, try as an offer
                    service = await get_offer(service_id)
                if service:
                    appointment['service_name'] = service.get('name')
                    appointment['service_price'] = service.get('price')
            
            master_id = appointment.get('master_id')
            if master_id:
                master = await get_master(master_id)
                if master:
                    appointment['master_name'] = master.get('name')
            
            user_appointments.append(appointment)
    
    return user_appointments

async def get_master_appointments(master_id):
    """Get all appointments for a specific master"""
    appointments = await get_all_appointments()
    master_appointments = []
    
    for appointment in appointments:
        if appointment.get('master_id') == master_id:
            # Add service and user info
            service_id = appointment.get('service_id')
            if service_id:
                # First try to get as a regular service
                service = await get_service(service_id)
                if not service:
                    # If not a regular service, try as an offer
                    service = await get_offer(service_id)
                if service:
                    appointment['service_name'] = service.get('name')
                    appointment['service_price'] = service.get('price')
            
            user_id = appointment.get('user_id')
            if user_id:
                user = await user_commands.get_user(user_id)
                if user:
                    appointment['user_name'] = user.get('name', 'Unknown')
                    appointment['user_username'] = user.get('username', None)
            
            master_appointments.append(appointment)
    
    return master_appointments

async def get_appointments_by_date(date):
    """Get all appointments for a specific date"""
    appointments = await get_all_appointments()
    date_appointments = []
    
    for appointment in appointments:
        if appointment.get('date') == date:
            # Add service, master and user info
            service_id = appointment.get('service_id')
            if service_id:
                # Try both regular service and offer
                service = await get_service(service_id)
                if not service:
                    service = await get_offer(service_id)
                if service:
                    appointment['service_name'] = service.get('name')
                    appointment['service_price'] = service.get('price')
            
            master_id = appointment.get('master_id')
            if master_id:
                master = await get_master(master_id)
                if master:
                    appointment['master_name'] = master.get('name')
            
            user_id = appointment.get('user_id')
            if user_id:
                user = await user_commands.get_user(user_id)
                if user:
                    appointment['user_name'] = user.get('name', 'Unknown')
                    appointment['user_username'] = user.get('username', None)
            
            date_appointments.append(appointment)
    
    return date_appointments

async def add_appointment(user_id, service_id, date, time, master_id=None, payment_method=None):
    """Add a new appointment to the database"""
    appointments = await get_all_appointments()
    
    # Generate a new ID
    new_id = "1"
    if appointments:
        new_id = str(max([int(appointment.get('id', 0)) for appointment in appointments]) + 1)
    
    # Check if user is verified
    verified_users = await get_sheet(VERIFIED_USERS_SHEET)
    is_verified = any(str(user.get('user_id')) == str(user_id) for user in verified_users)
    
    # Set initial status based on verification
    initial_status = "confirmed" if is_verified else "pending"
    
    # Create new appointment
    new_appointment = {
        'id': new_id,
        'user_id': user_id,
        'service_id': service_id,
        'date': date,
        'time': time,
        'status': initial_status
    }
    
    # Add master_id if provided
    if master_id:
        new_appointment['master_id'] = master_id
    
    # Add payment_method if provided (только администратор может установить)
    if payment_method:
        new_appointment['payment_method'] = payment_method
    
    # Store user's username and name for easier reporting
    try:
        user = await user_commands.get_user(user_id)
        if user:
            new_appointment['user_name'] = user.get('name', '')
            username = user.get('username')
            if username:
                new_appointment['user_username'] = username
    except Exception as e:
        print(f"Error getting user info: {e}")
    
    # Add to sheet
    appointments.append(new_appointment)
    await write_to_sheet(APPOINTMENTS_SHEET, appointments)
    
    return new_appointment

async def update_appointment_status(appointment_id, status):
    """Update an appointment's status"""
    appointments = await get_all_appointments()
    updated = False
    
    for i, appointment in enumerate(appointments):
        if appointment.get('id') == appointment_id:
            appointments[i]['status'] = status
            updated = True
            break
    
    if updated:
        await write_to_sheet(APPOINTMENTS_SHEET, appointments)
    
    return updated

async def update_appointment_payment(appointment_id, payment_method):
    """Update an appointment's payment method"""
    appointments = await get_all_appointments()
    updated = False
    
    for i, appointment in enumerate(appointments):
        if appointment.get('id') == appointment_id:
            appointments[i]['payment_method'] = payment_method
            updated = True
            break
    
    if updated:
        await write_to_sheet(APPOINTMENTS_SHEET, appointments)
    
    return updated

async def cancel_appointment(appointment_id):
    """Cancel an appointment by updating its status"""
    return await update_appointment_status(appointment_id, "canceled")

async def complete_appointment(appointment_id):
    """Mark an appointment as completed"""
    return await update_appointment_status(appointment_id, "completed")

async def verify_user(user_id):
    """Add a user to the verified users list"""
    verified_users = await get_sheet(VERIFIED_USERS_SHEET)
    
    # Check if user is already verified
    if any(str(user.get('user_id')) == str(user_id) for user in verified_users):
        return True
    
    # Add user to verified list
    verified_users.append({'user_id': user_id})
    await write_to_sheet(VERIFIED_USERS_SHEET, verified_users)
    
    # Also update any pending appointments for this user to confirmed
    appointments = await get_all_appointments()
    updated = False
    
    for i, appointment in enumerate(appointments):
        if str(appointment.get('user_id')) == str(user_id) and appointment.get('status') == 'pending':
            appointments[i]['status'] = 'confirmed'
            updated = True
    
    if updated:
        await write_to_sheet(APPOINTMENTS_SHEET, appointments)
    
    return True

async def verify_user_by_username(username):
    """Verify user by Telegram username"""
    if not username:
        return False
    
    # Normalize username (remove @ if present)
    if username.startswith('@'):
        username = username[1:]
    
    # Find user by username
    user = await user_commands.get_user_by_username(username)
    if not user:
        return False
    
    # Verify user by ID
    return await verify_user(user.get('id'))

async def is_user_verified(user_id):
    """Check if a user is verified"""
    verified_users = await get_sheet(VERIFIED_USERS_SHEET)
    return any(str(user.get('user_id')) == str(user_id) for user in verified_users)

async def get_appointments_statistics(master_id=None, start_date=None, end_date=None):
    """Get statistics for appointments"""
    appointments = await get_all_appointments()
    filtered_appointments = appointments
    
    # Filter by master if provided
    if master_id:
        filtered_appointments = [a for a in filtered_appointments if a.get('master_id') == master_id]
    
    # Filter by date range if provided
    if start_date:
        filtered_appointments = [a for a in filtered_appointments if a.get('date') >= start_date]
    if end_date:
        filtered_appointments = [a for a in filtered_appointments if a.get('date') <= end_date]
    
    # Calculate statistics
    total_count = len(filtered_appointments)
    completed_count = len([a for a in filtered_appointments if a.get('status') == 'completed'])
    paid_count = len([a for a in filtered_appointments if a.get('status') == 'paid'])
    canceled_count = len([a for a in filtered_appointments if a.get('status') == 'canceled'])
    
    # Calculate revenue
    revenue = 0
    for appointment in filtered_appointments:
        if appointment.get('status') in ['completed', 'paid']:
            service_id = appointment.get('service_id')
            if service_id:
                # Try both regular service and offer
                service = await get_service(service_id)
                if not service:
                    service = await get_offer(service_id)
                if service:
                    price = float(service.get('price', 0))
                    revenue += price
    
    return {
        'total_count': total_count,
        'completed_count': completed_count,
        'paid_count': paid_count,
        'canceled_count': canceled_count,
        'revenue': revenue
    }

# Группировка записей по датам
async def get_appointments_grouped_by_date(user_id=None, master_id=None):
    """Get appointments grouped by date"""
    appointments = await get_all_appointments()
    
    # Filter appointments by user or master if provided
    if user_id:
        appointments = [a for a in appointments if str(a.get('user_id')) == str(user_id)]
    if master_id:
        appointments = [a for a in appointments if a.get('master_id') == master_id]
    
    # Group appointments by date
    grouped = {}
    for appointment in appointments:
        date = appointment.get('date')
        if date not in grouped:
            grouped[date] = []
        
        # Добавляем информацию об услуге и мастере
        service_id = appointment.get('service_id')
        if service_id:
            # Try both regular service and offer
            service = await get_service(service_id)
            if not service:
                service = await get_offer(service_id)
            if service:
                appointment['service_name'] = service.get('name')
                appointment['service_price'] = service.get('price')
        
        master_id = appointment.get('master_id')
        if master_id:
            master = await get_master(master_id)
            if master:
                appointment['master_name'] = master.get('name')
        
        grouped[date].append(appointment)
    
    return grouped
