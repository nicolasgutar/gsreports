import os
import sys
import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import google.auth
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# --- CONSTANTS ---

# File names for OAuth 2.0
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

# Scopes define the permissions your app will ask for
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

# --- COLORS ---

# Colors for Balance Sheet (Old)
COLOR_MAJOR_HEADER_BG = {"red": 0.35, "green": 0.30, "blue": 0.29}
COLOR_HEADER_FONT = {"red": 1.0, "green": 1.0, "blue": 1.0}

# Colors for P&L Sheet
COLOR_INCOME_BG = {"red": 0.92, "green": 0.96, "blue": 0.9}     # Light Green
COLOR_PURPLE_HEADER = {"red": 0.44, "green": 0.19, "blue": 0.63}

# --- NEW: Colors for new Balance Sheet Style ---
COLOR_BS_ASSET_HEADER_BG = {"red": 0.35, "green": 0.35, "blue": 0.35} # Dark Grey
COLOR_BS_LE_HEADER_BG = {"red": 0.8, "green": 0.4, "blue": 0.2}     # Dark Orange
COLOR_BS_LE_SUBHEADER_BG = {"red": 0.95, "green": 0.75, "blue": 0.6} # Light Orange
COLOR_BS_TOTAL_BG = {"red": 0.95, "green": 0.75, "blue": 0.6}       # Light Orange
COLOR_BS_NOTE_RED = {"red": 1.0, "green": 0.0, "blue": 0.0}       # Red Text

def get_google_credentials():
    """
    Handles the OAuth 2.0 user flow to get valid credentials.
    Checks for client_secret.json and existing token.json.
    """

    if not os.path.exists(CLIENT_SECRET_FILE):
        print(f"❌ ERROR: Credentials file '{CLIENT_SECRET_FILE}' not found.")
        print("   Please download your OAuth 2.0 Client ID (Desktop app) and rename it.")
        sys.exit(1)

    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("No valid credentials found. Please authorize in the browser...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            print(f"Credentials saved to {TOKEN_FILE}")

    return creds

def build_services(creds):
    """
    Builds and returns the Drive, Sheets, and gspread client services.
    """
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)
        gc = gspread.authorize(creds)
        return drive_service, sheets_service, gc
    except Exception as e:
        print(f"❌ Error building Google services: {e}")
        sys.exit(1)

def share_spreadsheet_publicly(drive_service, spreadsheet_id):
    """
    Makes a given spreadsheet ID public (read-only) for anyone with the link.
    """
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission
        ).execute()
        print("✓ Sheet made public (read-only) for anyone with the link.")
    except Exception as e:
        print(f"⚠ Could not make file public: {e}")
