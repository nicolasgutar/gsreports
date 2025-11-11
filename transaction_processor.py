# transaction_processor.py
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime


def process_grouped_data_for_pnl(grouped_data: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Process grouped transaction data from database query into P&L line items.
    The grouped_data comes from get_transactions_grouped_by_category() which already
    has totals calculated by category.

    Args:
        grouped_data: Dictionary with 'income' and 'expenses' keys containing category totals

    Returns:
        Dictionary with P&L line items and totals
    """
    # Initialize P&L structure with all expected line items
    pnl_data = {
        # Income items
        "Business Income": 0.0,
        "Other Income": 0.0,
        "Uncategorized Income": 0.0,

        # Operating Expenses
        "Advertising": 0.0,
        "Advertising - test purchases": 0.0,
        "Business Equipment": 0.0,
        "Education": 0.0,
        "Employee & Contractor Salaries": 0.0,
        "Entertainment": 0.0,
        "Food & Drink": 0.0,
        "Food & Drink - w/ Client": 0.0,
        "Medical": 0.0,
        "Non-Profit / Charity": 0.0,
        "Personal Branding": 0.0,
        "Professional Fees": 0.0,
        "Professional Fees - Market fees": 0.0,
        "Professional Fees - Patent": 0.0,
        "Professional Fees - Sunbiz registration fees": 0.0,
        "Rent & Utilities": 0.0,
        "Repairs & Maintenance": 0.0,
        "Subscriptions": 0.0,
        "Supplies": 0.0,
        "Transportation": 0.0,
        "Travel": 0.0,
        "Uncategorized Expense": 0.0,

        # Other Expenses
        "Bank Fees": 0.0,
        "Insurance": 0.0,
        "Tax": 0.0,
    }

    # Map income categories directly (already grouped by DB)
    income_categories = grouped_data.get('income', {})
    for category, amount in income_categories.items():
        # Direct match first
        if category in pnl_data:
            pnl_data[category] += amount
        # Fuzzy matching for income
        elif "Business" in category or "Income" in category:
            pnl_data["Business Income"] += amount
        elif "Uncategorized" in category:
            pnl_data["Uncategorized Income"] += amount
        else:
            pnl_data["Other Income"] += amount

    # Map expense categories (already grouped by DB)
    expense_categories = grouped_data.get('expenses', {})
    for category, amount in expense_categories.items():
        # Direct match first
        if category in pnl_data:
            pnl_data[category] += amount
        # Fuzzy matching for expenses
        else:
            pnl_data["Uncategorized Expense"] += amount

    # Calculate totals
    total_income = (
        pnl_data["Business Income"] +
        pnl_data["Other Income"] +
        pnl_data["Uncategorized Income"]
    )

    total_operating_expenses = sum([
        pnl_data["Advertising"],
        pnl_data["Advertising - test purchases"],
        pnl_data["Business Equipment"],
        pnl_data["Education"],
        pnl_data["Employee & Contractor Salaries"],
        pnl_data["Entertainment"],
        pnl_data["Food & Drink"],
        pnl_data["Food & Drink - w/ Client"],
        pnl_data["Medical"],
        pnl_data["Non-Profit / Charity"],
        pnl_data["Personal Branding"],
        pnl_data["Professional Fees"],
        pnl_data["Professional Fees - Market fees"],
        pnl_data["Professional Fees - Patent"],
        pnl_data["Professional Fees - Sunbiz registration fees"],
        pnl_data["Rent & Utilities"],
        pnl_data["Repairs & Maintenance"],
        pnl_data["Subscriptions"],
        pnl_data["Supplies"],
        pnl_data["Transportation"],
        pnl_data["Travel"],
        pnl_data["Uncategorized Expense"],
    ])

    total_other_expenses = (
        pnl_data["Bank Fees"] +
        pnl_data["Insurance"] +
        pnl_data["Tax"]
    )

    gross_profit = total_income - total_operating_expenses
    net_income = gross_profit - total_other_expenses

    # Add totals to data
    pnl_data["Total Income"] = total_income
    pnl_data["Total Operating Expenses"] = total_operating_expenses
    pnl_data["Gross Profit"] = gross_profit
    pnl_data["Total Other Expenses"] = total_other_expenses
    pnl_data["Net Income"] = net_income

    return pnl_data


def create_transactions_dataframe(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert list of transaction dictionaries to a pandas DataFrame for display.

    Args:
        transactions: List of transaction dictionaries

    Returns:
        Formatted DataFrame with transaction data
    """
    if not transactions:
        return pd.DataFrame()

    # Select key columns for display
    display_columns = [
        'date', 'name', 'category', 'subcategory', 'amount',
        'merchantName', 'description', 'accountFrom', 'status'
    ]

    # Create list of dictionaries with selected columns
    df_data = []
    for transaction in transactions:
        row = {}
        for col in display_columns:
            value = transaction.get(col, '')
            # Format date if present
            if col == 'date' and value:
                if isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d')
            # Format amount
            elif col == 'amount' and value:
                value = float(value)
            row[col] = value
        df_data.append(row)

    df = pd.DataFrame(df_data)

    # Rename columns for better display
    df.rename(columns={
        'date': 'Date',
        'name': 'Transaction Name',
        'category': 'Category',
        'subcategory': 'Subcategory',
        'amount': 'Amount',
        'merchantName': 'Merchant',
        'description': 'Description',
        'accountFrom': 'Account',
        'status': 'Status'
    }, inplace=True)

    return df


def apply_transactions_formatting(worksheet, num_rows: int):
    """
    Apply formatting to the transactions sheet.

    Args:
        worksheet: gspread worksheet object
        num_rows: Number of rows in the sheet
    """
    requests = []
    sheet_id = worksheet.id

    # 1. Format header row (bold, background color)
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 0,
                "endRowIndex": 1,
                "startColumnIndex": 0,
                "endColumnIndex": 9,
            },
            "cell": {
                "userEnteredFormat": {
                    "backgroundColor": {"red": 0.44, "green": 0.19, "blue": 0.63},
                    "textFormat": {
                        "bold": True,
                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}
                    }
                }
            },
            "fields": "userEnteredFormat(backgroundColor,textFormat)"
        }
    })

    # 2. Format Amount column as currency
    requests.append({
        "repeatCell": {
            "range": {
                "sheetId": sheet_id,
                "startRowIndex": 1,
                "endRowIndex": num_rows + 1,
                "startColumnIndex": 4,  # Amount column
                "endColumnIndex": 5,
            },
            "cell": {
                "userEnteredFormat": {
                    "numberFormat": {
                        "type": "CURRENCY",
                        "pattern": "$#,##0.00"
                    }
                }
            },
            "fields": "userEnteredFormat.numberFormat"
        }
    })

    # 3. Freeze header row
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "frozenRowCount": 1
                }
            },
            "fields": "gridProperties.frozenRowCount"
        }
    })

    # 4. Auto-resize columns
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {
                "sheetId": sheet_id,
                "dimension": "COLUMNS",
                "startIndex": 0,
                "endIndex": 9
            }
        }
    })

    # Execute all formatting requests
    worksheet.spreadsheet.batch_update({"requests": requests})

