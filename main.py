import sys
import pandas as pd
from googleapiclient.errors import HttpError

# Import functions from our modules
from utils import (
    get_google_credentials, build_services, share_spreadsheet_publicly
)
from pnl import generate_pnl_report, generate_pnl_report_by_account, apply_pnl_formatting
from balance_sheet import generate_balance_sheet, apply_balance_sheet_formatting
from config import Config
from db_connector import DatabaseConnector
from db_queries import get_user_transactions, get_transactions_grouped_by_category
from balance_sheet_queries import get_all_balance_sheet_data
from transaction_processor import (
    create_transactions_dataframe,
    apply_transactions_formatting,
    process_grouped_data_for_pnl
)


def create_reports_in_google_sheets(user_id: str, pnl_df: pd.DataFrame, bs_df: pd.DataFrame,
                                   transactions_df: pd.DataFrame, pnl_formatting_rows: dict,
                                   personal_pnl_df: pd.DataFrame = None, business_pnl_df: pd.DataFrame = None) -> str:
    """
    Creates a new Google Sheet, writes the P&L, Balance Sheet, and Transactions to separate tabs,
    including separate Personal and Business P&L sheets if provided,
    applies formatting, and makes the sheet public.
    """
    try:
        print("\n--- Connecting to Google Cloud ---")
        creds = get_google_credentials()
        drive_service, sheets_service, gc = build_services(creds)

        # 1. Create spreadsheet
        spreadsheet_title = f"Financial Reports for {user_id}"
        print(f"Creating new spreadsheet: '{spreadsheet_title}'...")
        spreadsheet_body = {'properties': {'title': spreadsheet_title}}
        spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet_body).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        print(f"✓ Spreadsheet created with ID: {spreadsheet_id}")

        # Open the new spreadsheet with gspread
        gspread_sheet = gc.open_by_key(spreadsheet_id)

        # --- 2. Write Balance Sheet (Tab 1) ---
        print("Writing Balance Sheet...")
        bs_worksheet = gspread_sheet.sheet1
        bs_worksheet.update_title("Balance Sheet")

        bs_data_to_write = [bs_df.columns.values.tolist()] + bs_df.values.tolist()
        bs_worksheet.update(bs_data_to_write, "A1")

        apply_balance_sheet_formatting(bs_worksheet, len(bs_df.index))
        print("✓ Balance Sheet tab complete.")

        # --- 3. Write P&L (Tab 2) ---
        print("Writing Profit & Loss...")
        pnl_worksheet = gspread_sheet.add_worksheet(title="Profit & Loss", rows=100, cols=20)

        pnl_data_to_write = [pnl_df.columns.values.tolist()] + pnl_df.values.tolist()
        pnl_worksheet.update(pnl_data_to_write, "A1")

        apply_pnl_formatting(pnl_worksheet, len(pnl_df.index), pnl_formatting_rows)
        print("✓ Profit & Loss tab complete.")

        # --- 4. Write Personal P&L (Tab 3) ---
        if personal_pnl_df is not None and not personal_pnl_df.empty:
            print("Writing Personal Profit & Loss...")
            personal_pnl_worksheet = gspread_sheet.add_worksheet(title="Personal Profit & Loss", rows=100, cols=20)

            personal_pnl_data_to_write = [personal_pnl_df.columns.values.tolist()] + personal_pnl_df.values.tolist()
            personal_pnl_worksheet.update(personal_pnl_data_to_write, "A1")

            apply_pnl_formatting(personal_pnl_worksheet, len(personal_pnl_df.index), {})
            print("✓ Personal Profit & Loss tab complete.")

        # --- 5. Write Business P&L (Tab 4) ---
        if business_pnl_df is not None and not business_pnl_df.empty:
            print("Writing Business Profit & Loss...")
            business_pnl_worksheet = gspread_sheet.add_worksheet(title="Business Profit & Loss", rows=100, cols=20)

            business_pnl_data_to_write = [business_pnl_df.columns.values.tolist()] + business_pnl_df.values.tolist()
            business_pnl_worksheet.update(business_pnl_data_to_write, "A1")

            apply_pnl_formatting(business_pnl_worksheet, len(business_pnl_df.index), {})
            print("✓ Business Profit & Loss tab complete.")

        # --- 6. Write Transactions (Last Tab) ---
        if not transactions_df.empty:
            print("Writing Transactions...")
            trans_worksheet = gspread_sheet.add_worksheet(title="Transactions", rows=1000, cols=20)

            trans_data_to_write = [transactions_df.columns.values.tolist()] + transactions_df.values.tolist()
            trans_worksheet.update(trans_data_to_write, "A1")

            apply_transactions_formatting(trans_worksheet, len(transactions_df.index))
            print("✓ Transactions tab complete.")

        # 7. Make the file public
        share_spreadsheet_publicly(drive_service, spreadsheet_id)

        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    except HttpError as e:
        print(f"\n❌ HTTP Error: {e}")
        if "accessNotConfigured" in str(e):
            print("\n💡 HINT: The Google Sheets API is not enabled for your project.")
            print("   Please enable it in the Google Cloud Console.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """
    Main function to run the Financial Report generator.
    """
    # Print configuration
    Config.print_config()

    # Validate configuration
    if not Config.validate():
        print("\n❌ Configuration validation failed. Please check your settings.")
        sys.exit(1)

    # Get user ID
    user_id = input("Enter User ID to generate reports: ").strip()
    if not user_id:
        print("❌ Error: User ID cannot be empty")
        sys.exit(1)

    print(f"\n{'='*70}")
    print(f"Generating Financial Reports for User: {user_id}")
    print(f"{'='*70}\n")

    # Initialize variables
    data = {}
    transactions_df = pd.DataFrame()
    db = None

    try:
        print("--- Connecting to Database ---")
        # Initialize database connection
        db = DatabaseConnector(**Config.get_db_config())

        # Fetch transactions
        print(f"Fetching transactions for user {user_id}...")
        start_date = Config.REPORT_START_DATE
        end_date = Config.REPORT_END_DATE

        if start_date and end_date:
            print(f"Date range: {start_date} to {end_date}")

        transactions = get_user_transactions(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            limit=Config.DEFAULT_TRANSACTION_LIMIT
        )

        print(f"✓ Retrieved {len(transactions)} transactions")

        if not transactions:
            print("⚠ WARNING: No transactions found for this user.")
            print("   Reports will be generated with zero values.")

        # Create transactions DataFrame for sheet
        transactions_df = create_transactions_dataframe(transactions)

        # Process transactions using grouped query for P&L
        print("\nProcessing transactions for P&L using grouped query...")
        grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Process the grouped data into P&L format
        data = process_grouped_data_for_pnl(grouped_data)
        print(f"✓ P&L data calculated. Net Income: ${data['Net Income']:,.2f}")

        # Fetch Balance Sheet data from database
        print("\nFetching Balance Sheet data from database...")
        balance_sheet_data = get_all_balance_sheet_data(
            db, user_id,
            start_date=start_date,
            end_date=end_date
        )

        # Merge balance sheet data with P&L data
        data.update(balance_sheet_data)
        print("✓ Balance Sheet data loaded from database")

        # 2. Generate P&L report (General)
        print("\n--- Generating Reports ---")
        pnl_df, net_income, pnl_formatting_rows = generate_pnl_report(data, user_id)
        if pnl_df is None:
            sys.exit(1)  # Exit if data was missing

        # 2a. Generate Personal P&L report
        print("\n--- Generating Personal P&L Report ---")
        personal_grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            account_category="personal"
        )
        personal_data = process_grouped_data_for_pnl(personal_grouped_data)
        personal_pnl_df, personal_net_income, _ = generate_pnl_report_by_account(personal_data, user_id, "Personal")
        print(f"✓ Personal P&L data calculated. Net Income: ${personal_net_income:,.2f}")

        # 2b. Generate Business P&L report
        print("\n--- Generating Business P&L Report ---")
        business_grouped_data = get_transactions_grouped_by_category(
            db, user_id,
            start_date=start_date,
            end_date=end_date,
            account_category="business"
        )
        business_data = process_grouped_data_for_pnl(business_grouped_data)
        business_pnl_df, business_net_income, _ = generate_pnl_report_by_account(business_data, user_id, "Business")
        print(f"✓ Business P&L data calculated. Net Income: ${business_net_income:,.2f}")

        # 3. Generate Balance Sheet (passing in the calculated net_income from general P&L)
        balance_sheet_df = generate_balance_sheet(data, user_id, net_income)

        # 4. Create and write to new Google Sheets document
        sheet_link = create_reports_in_google_sheets(
            user_id, pnl_df, balance_sheet_df, transactions_df, pnl_formatting_rows,
            personal_pnl_df, business_pnl_df
        )

        print("\n" + "="*70)
        print("✅ Financial Reports successfully generated!")
        print(f"🔗 Link: {sheet_link}")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n❌ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up database connection
        if db:
            db.close_all_connections()
            print("\n✓ Database connections closed")


if __name__ == "__main__":
    main()
