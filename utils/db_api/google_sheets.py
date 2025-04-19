
import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# Configure Google Sheets client
client = None
sheet = None

# Spreadsheet details
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')

async def setup():
    """Setup Google Sheets connection"""
    global client, sheet
    
    # Create credentials from the service account file
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
    
    # Authorize with Google
    client = gspread.authorize(creds)
    
    # Open the spreadsheet
    sheet = client.open_by_key(SPREADSHEET_ID)
    
    # Ensure all required worksheets exist
    worksheets = [ws.title for ws in sheet.worksheets()]
    
    required_sheets = ['Services', 'Clients', 'Appointments', 'History']
    
    for required in required_sheets:
        if required not in worksheets:
            # Create the worksheet if it doesn't exist
            sheet.add_worksheet(title=required, rows=1000, cols=20)
            
            # Add headers based on worksheet
            if required == 'Services':
                sheet.worksheet(required).append_row(['id', 'name', 'description', 'price'])
            elif required == 'Clients':
                sheet.worksheet(required).append_row(['user_id', 'username', 'full_name', 'role'])
            elif required == 'Appointments':
                sheet.worksheet(required).append_row(['id', 'user_id', 'service_id', 'date', 'time', 'status'])
            elif required == 'History':
                sheet.worksheet(required).append_row(['timestamp', 'user_id', 'service_id', 'date', 'time', 'amount'])
    
    return sheet
