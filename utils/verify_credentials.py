
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
        required_fields = ['client_email', 'token_uri', 'private_key', 'type']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"ERROR: Your credentials file is missing the following required fields: {', '.join(missing_fields)}")
            print("Please make sure you downloaded the correct JSON key file from Google Cloud Console")
            return False
        
        # Check that this is a service account
        if creds_data.get('type') != 'service_account':
            print("ERROR: Your credentials file is not for a service account")
            print("Make sure you created a service account in Google Cloud Console and downloaded its key")
            return False
        
        print("SUCCESS: Your credentials file appears to be valid!")
        print(f"Service Account Email: {creds_data['client_email']}")
        return True
    
    except json.JSONDecodeError:
        print("ERROR: Your credentials file is not valid JSON")
        print("Please make sure you downloaded the correct JSON key file from Google Cloud Console")
        return False
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while checking your credentials file: {str(e)}")
        return False

if __name__ == "__main__":
    success = verify_credentials()
    if not success:
        sys.exit(1)
