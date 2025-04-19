
"""
A utility script to verify your Google service account credentials file.
Run this script to check if your credentials file is correctly formatted.
"""

import json
import os
import sys
from dotenv import load_dotenv

def verify_credentials():
    # Load environment variables
    load_dotenv()
    
    # Get credentials file path from .env
    creds_file = os.getenv('GOOGLE_CREDENTIALS_FILE')
    
    if not creds_file:
        print("ERROR: GOOGLE_CREDENTIALS_FILE is not set in your .env file")
        print("Please add this variable to your .env file with the path to your Google credentials JSON file")
        return False
    
    print(f"Looking for credentials file at: {creds_file}")
    
    if not os.path.exists(creds_file):
        print(f"ERROR: Credentials file not found at: {creds_file}")
        print("Please make sure the file exists and the path is correct in your .env file")
        return False
    
    try:
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        # Check for required fields
        required_fields = ['client_email', 'token_uri', 'private_key', 'type', 'project_id']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"ERROR: Your credentials file is missing the following required fields: {', '.join(missing_fields)}")
            print("\nPlease make sure you downloaded the correct JSON key file from Google Cloud Console")
            print("The file should look something like this:")
            print("""
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "abcdef1234567890...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account..."
}
            """)
            return False
        
        # Check that this is a service account
        if creds_data.get('type') != 'service_account':
            print("ERROR: Your credentials file is not for a service account")
            print("Make sure you created a service account in Google Cloud Console and downloaded its key")
            return False
        
        print("\nSUCCESS: Your credentials file appears to be valid!")
        print(f"Service Account Email: {creds_data['client_email']}")
        print(f"Project ID: {creds_data['project_id']}")
        
        # Also check if SPREADSHEET_ID is set
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not spreadsheet_id:
            print("\nWARNING: SPREADSHEET_ID is not set in your .env file")
            print("Make sure to add this to connect to your Google Sheet")
        else:
            print(f"Spreadsheet ID: {spreadsheet_id}")
        
        return True
    
    except json.JSONDecodeError:
        print("ERROR: Your credentials file is not valid JSON")
        print("Please make sure you downloaded the correct JSON key file from Google Cloud Console")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while checking your credentials file: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== Google Service Account Credentials Verification ===\n")
    success = verify_credentials()
    
    if success:
        print("\nYour credentials file looks good! Make sure you've shared your Google Sheet with the service account email listed above.")
        print("Next steps:")
        print("1. Run 'python main.py' to start your bot")
        print("2. If you encounter any issues, check that your Google Sheet permissions are correctly set")
    else:
        print("\nPlease fix the issues above before starting your bot.")
        sys.exit(1)
