
import os
import gspread
import logging
import time
import asyncio
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Spreadsheet details
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')

# Initialize Google Sheets client
client = None
sheet = None

# Cache for read operations (to reduce API calls)
sheet_cache = {}
cache_ttl = 60  # Cache TTL in seconds

async def setup():
    """Setup Google Sheets connection"""
    global client, sheet
    
    # If already set up, just return the sheet
    if sheet is not None:
        return sheet
    
    # Validate environment variables
    if not SPREADSHEET_ID:
        logging.error("SPREADSHEET_ID is not set in the .env file")
        raise ValueError("SPREADSHEET_ID is not set in the .env file")
    
    if not CREDENTIALS_FILE:
        logging.error("GOOGLE_CREDENTIALS_FILE is not set in the .env file")
        raise ValueError("GOOGLE_CREDENTIALS_FILE is not set in the .env file")
    
    if not os.path.exists(CREDENTIALS_FILE):
        logging.error(f"Credentials file not found at: {CREDENTIALS_FILE}")
        raise FileNotFoundError(f"Credentials file not found at: {CREDENTIALS_FILE}")
    
    try:
        # Create credentials from the service account file
        creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        
        # Authorize with Google
        client = gspread.authorize(creds)
        
        # Open the spreadsheet with timeout and retry
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                sheet = client.open_by_key(SPREADSHEET_ID, timeout=30)  # Set timeout to 30 seconds
                break
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise
                logging.warning(f"Retry {retry_count}/{max_retries} opening spreadsheet: {str(e)}")
                await asyncio.sleep(2)  # Wait before retrying
        
        # Ensure all required worksheets exist
        worksheets = [ws.title for ws in sheet.worksheets()]
        
        required_sheets = [
            'Services', 'Clients', 'Appointments', 'History', 'Masters', 
            'Categories', 'Offers', 'VerifiedUsers', 'ServiceTemplates', 
            'Subscriptions', 'ServiceCosts', 'FinanceAnalytics', 'ClientStats',
            'Payments'  # Add payments sheet
        ]
        
        for required in required_sheets:
            if required not in worksheets:
                # Create the worksheet if it doesn't exist
                sheet.add_worksheet(title=required, rows=1000, cols=20)
                
                # Add headers based on worksheet
                if required == 'Services':
                    sheet.worksheet(required).append_row(['id', 'name', 'description', 'price', 'duration', 'category_id'])
                elif required == 'Clients':
                    sheet.worksheet(required).append_row(['user_id', 'username', 'full_name', 'role', 'master_id'])
                elif required == 'Appointments':
                    sheet.worksheet(required).append_row(['id', 'user_id', 'service_id', 'date', 'time', 'status', 'master_id', 'payment_method'])
                elif required == 'History':
                    sheet.worksheet(required).append_row(['timestamp', 'user_id', 'service_id', 'date', 'time', 'amount', 'master_id', 'payment_method'])
                elif required == 'Masters':
                    sheet.worksheet(required).append_row(['id', 'telegram_id', 'name', 'telegram', 'phone', 'specialties', 'location', 'description'])
                elif required == 'Categories':
                    sheet.worksheet(required).append_row(['id', 'name'])
                elif required == 'Offers':
                    sheet.worksheet(required).append_row(['id', 'name', 'description', 'price', 'duration_days'])  # Changed from 'duration' to 'duration_days'
                elif required == 'VerifiedUsers':
                    sheet.worksheet(required).append_row(['user_id'])
                elif required == 'ServiceTemplates':
                    sheet.worksheet(required).append_row(['category_name', 'service_name', 'description', 'default_duration', 'category_id'])
                elif required == 'Subscriptions':
                    sheet.worksheet(required).append_row(['user_id', 'start_date', 'end_date', 'trial', 'referrer_id'])
                elif required == 'ServiceCosts':
                    sheet.worksheet(required).append_row(['service_id', 'materials_cost', 'time_cost', 'other_costs', 'last_updated'])
                elif required == 'FinanceAnalytics':
                    sheet.worksheet(required).append_row(['admin_id', 'date', 'total_income', 'total_expenses', 'profit', 'appointments_count'])
                elif required == 'ClientStats':
                    sheet.worksheet(required).append_row(['client_id', 'total_visits', 'total_spent', 'last_visit', 'favorite_service', 'vip_status', 'notes'])
                elif required == 'Payments':
                    sheet.worksheet(required).append_row(['id', 'user_id', 'plan_months', 'amount', 'payment_date', 'payment_method', 'verified'])
        
        # Initialize template services if ServiceTemplates is empty
        templates_sheet = sheet.worksheet('ServiceTemplates')
        if len(templates_sheet.get_all_records()) == 0:
            # Setup in a separate function to avoid timeout
            asyncio.create_task(initialize_template_services_async())
        
        logging.info("Successfully connected to Google Sheets")
        return sheet
    
    except Exception as e:
        logging.error(f"Error connecting to Google Sheets: {str(e)}")
        if "MalformedError" in str(e):
            logging.error("Your credentials file appears to be invalid. Please verify it contains all required fields.")
            logging.error("Run the verify_credentials.py script to check your credentials file.")
        return None

async def initialize_template_services_async():
    """Initialize template services asynchronously to avoid timeouts"""
    global sheet
    
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            return
    
    try:
        templates_sheet = sheet.worksheet('ServiceTemplates')
        initialize_template_services(templates_sheet)
    except Exception as e:
        logging.error(f"Error initializing template services: {str(e)}")

def initialize_template_services(worksheet):
    """Initialize template services with category_id"""
    # Get all categories or create them if they don't exist
    category_ids = {}
    
    templates = [
        # Format: category_name, service_name, description, default_duration
        # Маникюр
        ['Маникюр', 'Классический маникюр', 'Обрезной маникюр с обработкой кутикулы', 45],
        ['Маникюр', 'Аппаратный маникюр', 'Маникюр с использованием аппарата без повреждения кутикулы', 60],
        # More templates...
    ]
    
    # Add just a few templates for testing instead of all
    test_templates = templates[:10]  # Just add first 10 templates for now
    
    # Add template services in batches to avoid API limits
    batch_size = 5
    for i in range(0, len(test_templates), batch_size):
        batch = test_templates[i:i+batch_size]
        
        # Add category_id field to each template service
        enhanced_batch = []
        for template in batch:
            category_name = template[0]
            # We'll set a placeholder for category_id - it will be updated later
            enhanced_template = template + [""]
            enhanced_batch.append(enhanced_template)
            
        worksheet.append_rows(enhanced_batch)
        time.sleep(1)  # Avoid rate limits
    
    return True

async def get_sheet(sheet_name):
    """Get data from a specific sheet with caching"""
    global sheet, sheet_cache
    
    # Check cache first
    cache_key = f"sheet_{sheet_name}"
    if cache_key in sheet_cache:
        cache_entry = sheet_cache[cache_key]
        if time.time() - cache_entry['timestamp'] < cache_ttl:
            return cache_entry['data']
    
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            logging.error(f"Error getting sheet {sheet_name}: sheet is not initialized")
            return []
    
    try:
        # Get the worksheet with retry
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get the worksheet
                worksheet = sheet.worksheet(sheet_name)
                
                # Get all data from the sheet
                data = worksheet.get_all_records()
                
                # Cache the result
                sheet_cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                
                return data
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logging.error(f"Failed to get sheet {sheet_name} after {max_retries} retries: {str(e)}")
                    return []
                
                logging.warning(f"Retry {retry_count}/{max_retries} getting sheet {sheet_name}: {str(e)}")
                await asyncio.sleep(2)  # Wait before retrying
        
        return []
    except Exception as e:
        logging.error(f"Error getting sheet {sheet_name}: {str(e)}")
        return []

async def write_to_sheet(sheet_name, data):
    """Write data to a specific sheet"""
    global sheet, sheet_cache
    
    # Ensure sheet is initialized
    if sheet is None:
        sheet = await setup()
        if sheet is None:
            logging.error(f"Error writing to sheet {sheet_name}: sheet is not initialized")
            return False
    
    try:
        # Get the worksheet with retry
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Get the worksheet
                worksheet = sheet.worksheet(sheet_name)
                
                # Get the headers
                headers = worksheet.row_values(1)
                
                # Clear the sheet (except headers)
                if worksheet.row_count > 1:
                    worksheet.delete_rows(2, worksheet.row_count)
                
                # Write the data in batches
                batch_size = 10
                rows = []
                
                for item in data:
                    row = []
                    for header in headers:
                        row.append(item.get(header, ""))
                    rows.append(row)
                
                # Write data in batches
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i+batch_size]
                    if batch:
                        worksheet.append_rows(batch)
                        time.sleep(1)  # Avoid rate limits
                
                # Invalidate cache
                cache_key = f"sheet_{sheet_name}"
                if cache_key in sheet_cache:
                    del sheet_cache[cache_key]
                
                return True
            
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    logging.error(f"Failed to write to sheet {sheet_name} after {max_retries} retries: {str(e)}")
                    return False
                
                logging.warning(f"Retry {retry_count}/{max_retries} writing to sheet {sheet_name}: {str(e)}")
                await asyncio.sleep(2)  # Wait before retrying
        
        return False
    except Exception as e:
        logging.error(f"Error writing to sheet {sheet_name}: {str(e)}")
        return False

# Function to clear cache
async def clear_cache():
    """Clear sheet cache to force fresh data"""
    global sheet_cache
    sheet_cache = {}
    return True
