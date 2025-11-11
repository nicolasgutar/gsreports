# balance_sheet.py
import pandas as pd
from utils import COLOR_MAJOR_HEADER_BG, COLOR_HEADER_FONT

def generate_balance_sheet(user_data: dict, user_id: str, net_income: float) -> pd.DataFrame:
    """
    Calculates and structures the balance sheet data into a pandas DataFrame.
    Uses the net_income calculated from the P&L.
    """
    print(f"--- Generating Balance Sheet for {user_id} ---")

    # 1. ASSETS CALCULATION
    assets = [
        user_data["Cash"], user_data["Accounts Receivable"], user_data["Other Receivables"],
        user_data["Business Savings/Reserves"], user_data["Business Equipment (Asset)"],
        user_data["Inventory"], user_data["Prepaid Expenses"],
    ]
    total_assets = sum(assets)

    # 2. LIABILITIES CALCULATION
    liabilities = [
        user_data["Loan Payments / Credit Cards"], user_data["Business Loans 1"],
        user_data["Business Loans 2"], user_data["Taxes Payable"],
    ]
    total_liabilities = sum(liabilities)

    # 3. EQUITY CALCULATION
    # ** ACCOUNTING FIX **
    # We now use the net_income passed from the P&L report
    retained_earnings = net_income - user_data["Owner's Withdrawal"]
    total_equity = user_data["Owner's Contribution"] + retained_earnings

    # Sanity Check
    total_liabilities_and_equity = total_liabilities + total_equity
    if not (abs(total_assets - total_liabilities_and_equity) < 0.01):
        print(
            f"⚠ WARNING: Balance sheet does not balance!"
            f" Assets: {total_assets:.2f} | L + E: {total_liabilities_and_equity:.2f}"
        )
        print(f"   Difference: {total_assets - total_liabilities_and_equity:.2f}")
    else:
        print(f"✓ Balance sheet balances: {total_assets:.2f}")


    # 4. STRUCTURE DATA FRAME
    data = [
        ["BALANCE SHEET", ""],
        ["ASSETS", ""],
        ["Cash", user_data["Cash"]],
        ["Accounts Receivable", user_data["Accounts Receivable"]],
        ["Other Receivables", user_data["Other Receivables"]],
        ["Business savings/reserves", user_data["Business Savings/Reserves"]],
        ["Business Equipment", user_data["Business Equipment (Asset)"]],
        ["Inventory", user_data["Inventory"]],
        ["Prepaid Expenses", user_data["Prepaid Expenses"]],
        ["", ""],
        ["Total Assets", total_assets],
        ["", ""],
        ["LIABILITIES & EQUITY", ""],
        ["LIABILITIES", ""],
        ["CURRENT LIABILITIES", ""],
        ["Loan Payments / Credit Cards", user_data["Loan Payments / Credit Cards"]],
        ["Business Loans", user_data["Business Loans 1"]],
        ["Business Loans", user_data["Business Loans 2"]],
        ["Taxes Payable", user_data["Taxes Payable"]],
        ["", ""],
        ["Total Liabilities", total_liabilities],
        ["", ""],
        ["OWNER'S EQUITY", ""],
        ["Owner's Contribution", user_data["Owner's Contribution"]],
        ["Owner's Withdrawal", user_data["Owner's Withdrawal"]],
        ["Retained Earnings", retained_earnings],
        ["", ""],
        ["Total Owner's Equity", total_equity],
        ["", ""],
        ["Total Liabilities and Owner's Equity", total_liabilities_and_equity],
    ]

    df = pd.DataFrame(data, columns=["Account", "Amount"])
    return df


def apply_balance_sheet_formatting(worksheet, num_rows: int):
    """
    Applies complex formatting for the Balance Sheet.
    """
    requests = []
    sheet_id = worksheet.id

    # 1. Apply Currency Formatting to Column B
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1, "endRowIndex": num_rows + 1,
                "startColumnIndex": 1, "endColumnIndex": 2,
            },
            "cell": {"userEnteredFormat": {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}},
            "fields": "userEnteredFormat.numberFormat"
        }
    })

    # Define row structures (1-based indexing for clarity, converted to 0-based)
    major_header_rows = [3, 15, 24] # ASSETS, CURRENT LIABILITIES, OWNER'S EQUITY
    total_and_subheader_rows = [2, 11, 13, 14, 21, 23, 28, 30] # BS, Total Assets, L&E, LIAB, Total Liab, EQUITY, Total Equity, Total L&E

    # 2. Apply Formatting to Major Headers
    for row in major_header_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1, "endRowIndex": row,
                    "startColumnIndex": 0, "endColumnIndex": 2,
                },
                "cell": {"userEnteredFormat": {
                    "backgroundColor": COLOR_MAJOR_HEADER_BG,
                    "textFormat": {"bold": True, "foregroundColor": COLOR_HEADER_FONT}
                }},
                "fields": "userEnteredFormat(backgroundColor,textFormat)"
            }
        })

    # 3. Apply Bold Formatting to Totals and Sub-Headers
    for row in total_and_subheader_rows:
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1, "endRowIndex": row,
                    "startColumnIndex": 0, "endColumnIndex": 2,
                },
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold"
            }
        })

    # 4. Autofit column widths
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 2}
        }
    })

    worksheet.spreadsheet.batch_update({"requests": requests})