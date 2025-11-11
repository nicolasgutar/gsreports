import gspread

CREDENTIALS_FILE = 'apachurrao.json'

def cleanup_service_account_drive():
    """
    Lists and optionally deletes all files in the service account's Drive.
    """
    try:
        print("Connecting to Google Drive...")
        gc = gspread.service_account(filename=CREDENTIALS_FILE)

        # List all files in the service account's Drive
        files = gc.list_spreadsheet_files()

        if not files:
            print("No files found in service account's Drive.")
            return

        print(f"\nFound {len(files)} file(s) in service account's Drive:")
        print("-" * 80)
        for idx, file in enumerate(files, 1):
            print(f"{idx}. {file['name']} (ID: {file['id']})")
        print("-" * 80)

        # Ask user for confirmation
        response = input("\nDo you want to delete ALL these files? (yes/no): ").strip().lower()

        if response == 'yes':
            print("\nDeleting files...")
            for file in files:
                try:
                    gc.del_spreadsheet(file['id'])
                    print(f"✓ Deleted: {file['name']}")
                except Exception as e:
                    print(f"✗ Failed to delete {file['name']}: {e}")
            print("\n✅ Cleanup complete!")
        else:
            print("Cleanup cancelled.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup_service_account_drive()