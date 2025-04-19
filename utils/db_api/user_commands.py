
from utils.db_api.google_sheets import sheet

async def get_user(user_id):
    """Get user by Telegram ID"""
    clients_sheet = sheet.worksheet('Clients')
    
    # Find the user by ID
    try:
        cell = clients_sheet.find(str(user_id), in_column=1)
        if cell:
            row = clients_sheet.row_values(cell.row)
            return {
                'user_id': int(row[0]),
                'username': row[1],
                'full_name': row[2],
                'role': row[3]
            }
        return None
    except:
        return None

async def add_user(user_id, username, full_name, role='client'):
    """Add a new user to the database"""
    clients_sheet = sheet.worksheet('Clients')
    
    # Check if user already exists
    existing_user = await get_user(user_id)
    if existing_user:
        return existing_user
    
    # Add the new user
    clients_sheet.append_row([
        str(user_id),
        username or '',
        full_name or '',
        role
    ])
    
    # Return the newly created user
    return {
        'user_id': user_id,
        'username': username or '',
        'full_name': full_name or '',
        'role': role
    }

async def update_user_role(user_id, new_role):
    """Update user role"""
    clients_sheet = sheet.worksheet('Clients')
    
    # Find the user by ID
    cell = clients_sheet.find(str(user_id), in_column=1)
    if cell:
        # Update the role cell (column 4)
        clients_sheet.update_cell(cell.row, 4, new_role)
        return True
    return False
