
import os
import gspread
import logging
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
        
        # Open the spreadsheet
        sheet = client.open_by_key(SPREADSHEET_ID)
        
        # Ensure all required worksheets exist
        worksheets = [ws.title for ws in sheet.worksheets()]
        
        required_sheets = ['Services', 'Clients', 'Appointments', 'History', 'Masters']
        
        for required in required_sheets:
            if required not in worksheets:
                # Create the worksheet if it doesn't exist
                sheet.add_worksheet(title=required, rows=1000, cols=20)
                
                # Add headers based on worksheet
                if required == 'Services':
                    sheet.worksheet(required).append_row(['id', 'name', 'description', 'price', 'duration'])
                elif required == 'Clients':
                    sheet.worksheet(required).append_row(['user_id', 'username', 'full_name', 'role', 'master_id'])
                elif required == 'Appointments':
                    sheet.worksheet(required).append_row(['id', 'user_id', 'service_id', 'date', 'time', 'status', 'master_id', 'payment_method'])
                elif required == 'History':
                    sheet.worksheet(required).append_row(['timestamp', 'user_id', 'service_id', 'date', 'time', 'amount', 'master_id', 'payment_method'])
                elif required == 'Masters':
                    sheet.worksheet(required).append_row(['id', 'user_id', 'name', 'telegram', 'address', 'location', 'notification_enabled', 'work_hours'])
        
        logging.info("Successfully connected to Google Sheets")
        return sheet
    
    except Exception as e:
        logging.error(f"Error connecting to Google Sheets: {str(e)}")
        if "MalformedError" in str(e):
            logging.error("Your credentials file appears to be invalid. Please verify it contains all required fields.")
            logging.error("Run the verify_credentials.py script to check your credentials file.")
        return None
