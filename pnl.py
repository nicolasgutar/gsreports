import pandas as pd
from itertools import zip_longest

def generate_pnl_report_by_account(user_data: dict, user_id: str, account_type: str):
    """
    Structures the P&L data into a 4-column (Expenses | Income) pandas DataFrame for a specific account type,
    styled like the user's new image.
    ALL calculations are assumed to be done by the backend.

    Args:
        user_data: Dictionary with P&L line items
        user_id: User ID for the report
        account_type: Either 'Personal' or 'Business'

    Returns the DataFrame, the Net Income (read from user_data), and an empty dict.
    """
    print(f"--- Generating {account_type} P&L Report for {user_id} ---")

    # 1. READ ALL VALUES FROM user_data (NO COMPUTATION)
    try:
        total_income = user_data["Total Income"]
        total_operating_expenses = user_data["Total Operating Expenses"]
        total_other_expenses = user_data["Total Other Expenses"]
        net_income = user_data["Net Income"] # Still needed for balance_sheet.py
    except KeyError as e:
        print(f"❌ ERROR: Missing P&L total key in user_data: {e}")
        print("   Please add all total fields (Total Income, Gross Profit, etc.) to SAMPLE_USER_DATA.")
        return None, 0, None

    print(f"✓ {account_type} P&L Data Read. Net Income: {net_income:.2f}")

    # 2. PREPARE DATA LISTS FOR COLUMNS

    # --- Income Column (Right Side) ---
    income_items = [
        ["Business Income", user_data["Business Income"]],
        ["Other Income", user_data["Other Income"]],
        ["Uncategorized", user_data["Uncategorized Income"]],
        # Add more income items here if they are in user_data
    ]

    # --- Expense Column (Left Side) ---
    # Combine OpEx and OtherEx for one long list
    op_expense_items = [
        ["Advertising", user_data["Advertising"]],
        ["Advertising - test purchases", user_data["Advertising - test purchases"]],
        ["Business Equipment", user_data["Business Equipment"]],
        ["Education", user_data["Education"]],
        ["Employee & Contractor Salaries", user_data["Employee & Contractor Salaries"]],
        ["Entertainment", user_data["Entertainment"]],
        ["Food & Drink", user_data["Food & Drink"]],
        ["Food & Drink - w/ Client", user_data["Food & Drink - w/ Client"]],
        ["Medical", user_data["Medical"]],
        ["Non-Profit / Charity", user_data["Non-Profit / Charity"]],
        ["Personal Branding", user_data["Personal Branding"]],
        ["Professional Fees", user_data["Professional Fees"]],
        ["Professional Fees - Market fees", user_data["Professional Fees - Market fees"]],
        ["Professional Fees - Patent", user_data["Professional Fees - Patent"]],
        ["Professional Fees - Sunbiz registration fees", user_data["Professional Fees - Sunbiz registration fees"]],
        ["Rent & Utilities", user_data["Rent & Utilities"]],
        ["Repairs & Maintenance", user_data["Repairs & Maintenance"]],
        ["Subscriptions", user_data["Subscriptions"]],
        ["Supplies", user_data["Supplies"]],
        ["Transportation", user_data["Transportation"]],
        ["Travel", user_data["Travel"]],
        ["Uncategorized", user_data["Uncategorized Expense"]],
    ]

    other_expense_items = [
        ["Bank Fees", user_data["Bank Fees"]],
        ["Insurance", user_data["Insurance"]],
        ["Tax", user_data["Tax"]],
    ]

    all_expense_items = op_expense_items + other_expense_items

    # 3. BUILD THE 4-COLUMN DATA STRUCTURE (New Layout)

    # --- CHANGED: Pre-calculate SUM ranges ---
    # The header is now 4 rows. Items start at row 5 (index 4).
    expense_item_start_row = 5 # Sheet row 5
    expense_item_end_row = expense_item_start_row + len(all_expense_items) - 1

    income_item_start_row = 5 # Sheet row 5
    income_item_end_row = income_item_start_row + len(income_items) - 1

    # Create the SUM formulas. Handle empty lists to avoid e.g. "B5:B4"
    expense_sum_formula = f"=SUM(B{expense_item_start_row+1}:B{expense_item_end_row+1})" if len(all_expense_items) > 0 else "0"
    income_sum_formula = f"=SUM(D{income_item_start_row+1}:D{income_item_end_row+1})" if len(income_items) > 0 else "0"

    # --- CHANGED: Updated data list with account type in title ---
    data = [
        [f"{account_type} Yearly Income And Expense Report", "", "", ""], # Row 1: Main title with account type
        ["Operating Expenses", expense_sum_formula, "Income", income_sum_formula], # Row 2: Section Headers + Totals
        ["", "Actual", "", "Actual"],                     # Row 3: Sub-Headers
        ["", "", "", ""],                                 # Row 4: Divider
    ]
    # Rows 5, 6 from the original list have been removed.

    # Use zip_longest to pair expense and income items, padding the shorter list
    for exp, inc in zip_longest(all_expense_items, income_items, fillvalue=["", ""]):
        data.append([exp[0], exp[1], inc[0], inc[1]])

    df = pd.DataFrame(data, columns=["", "Amount", "", "Amount"])

    # Return df and net_income (as before), but formatting_rows is no longer needed
    return df, net_income, {} # Pass empty dict to satisfy main.py


def generate_pnl_report(user_data: dict, user_id: str):
    """
    Structures the P&L data into a 4-column (Expenses | Income) pandas DataFrame,
    styled like the user's new image.
    ALL calculations are assumed to be done by the backend.

    Returns the DataFrame, the Net Income (read from user_data), and an empty dict.
    """
    print(f"--- Generating P&L Report for {user_id} ---")

    # 1. READ ALL VALUES FROM user_data (NO COMPUTATION)
    try:
        total_income = user_data["Total Income"]
        total_operating_expenses = user_data["Total Operating Expenses"]
        total_other_expenses = user_data["Total Other Expenses"]
        net_income = user_data["Net Income"] # Still needed for balance_sheet.py
    except KeyError as e:
        print(f"❌ ERROR: Missing P&L total key in user_data: {e}")
        print("   Please add all total fields (Total Income, Gross Profit, etc.) to SAMPLE_USER_DATA.")
        return None, 0, None

    print(f"✓ P&L Data Read. Net Income: {net_income:.2f}")

    # 2. PREPARE DATA LISTS FOR COLUMNS

    # --- Income Column (Right Side) ---
    income_items = [
        ["Business Income", user_data["Business Income"]],
        ["Other Income", user_data["Other Income"]],
        ["Uncategorized", user_data["Uncategorized Income"]],
        # Add more income items here if they are in user_data
    ]

    # --- Expense Column (Left Side) ---
    # Combine OpEx and OtherEx for one long list
    op_expense_items = [
        ["Advertising", user_data["Advertising"]],
        ["Advertising - test purchases", user_data["Advertising - test purchases"]],
        ["Business Equipment", user_data["Business Equipment"]],
        ["Education", user_data["Education"]],
        ["Employee & Contractor Salaries", user_data["Employee & Contractor Salaries"]],
        ["Entertainment", user_data["Entertainment"]],
        ["Food & Drink", user_data["Food & Drink"]],
        ["Food & Drink - w/ Client", user_data["Food & Drink - w/ Client"]],
        ["Medical", user_data["Medical"]],
        ["Non-Profit / Charity", user_data["Non-Profit / Charity"]],
        ["Personal Branding", user_data["Personal Branding"]],
        ["Professional Fees", user_data["Professional Fees"]],
        ["Professional Fees - Market fees", user_data["Professional Fees - Market fees"]],
        ["Professional Fees - Patent", user_data["Professional Fees - Patent"]],
        ["Professional Fees - Sunbiz registration fees", user_data["Professional Fees - Sunbiz registration fees"]],
        ["Rent & Utilities", user_data["Rent & Utilities"]],
        ["Repairs & Maintenance", user_data["Repairs & Maintenance"]],
        ["Subscriptions", user_data["Subscriptions"]],
        ["Supplies", user_data["Supplies"]],
        ["Transportation", user_data["Transportation"]],
        ["Travel", user_data["Travel"]],
        ["Uncategorized", user_data["Uncategorized Expense"]],
    ]

    other_expense_items = [
        ["Bank Fees", user_data["Bank Fees"]],
        ["Insurance", user_data["Insurance"]],
        ["Tax", user_data["Tax"]],
    ]

    all_expense_items = op_expense_items + other_expense_items

    # 3. BUILD THE 4-COLUMN DATA STRUCTURE (New Layout)

    # --- CHANGED: Pre-calculate SUM ranges ---
    # The header is now 4 rows. Items start at row 5 (index 4).
    expense_item_start_row = 5 # Sheet row 5
    expense_item_end_row = expense_item_start_row + len(all_expense_items) - 1

    income_item_start_row = 5 # Sheet row 5
    income_item_end_row = income_item_start_row + len(income_items) - 1

    # Create the SUM formulas. Handle empty lists to avoid e.g. "B5:B4"
    expense_sum_formula = f"=SUM(B{expense_item_start_row+1}:B{expense_item_end_row+1})" if len(all_expense_items) > 0 else "0"
    income_sum_formula = f"=SUM(D{income_item_start_row+1}:D{income_item_end_row+1})" if len(income_items) > 0 else "0"

    # --- CHANGED: Updated data list ---
    data = [
        ["Yearly Income And Expense Report", "", "", ""], # Row 1: Main title
        ["Operating Expenses", expense_sum_formula, "Income", income_sum_formula], # Row 2: Section Headers + Totals
        ["", "Actual", "", "Actual"],                     # Row 3: Sub-Headers
        ["", "", "", ""],                                 # Row 4: Divider
    ]
    # Rows 5, 6 from the original list have been removed.

    # Use zip_longest to pair expense and income items, padding the shorter list
    for exp, inc in zip_longest(all_expense_items, income_items, fillvalue=["", ""]):
        data.append([exp[0], exp[1], inc[0], inc[1]])

    df = pd.DataFrame(data, columns=["", "Amount", "", "Amount"])

    # Return df and net_income (as before), but formatting_rows is no longer needed
    return df, net_income, {} # Pass empty dict to satisfy main.py

def apply_pnl_formatting(worksheet, num_rows: int, formatting_rows: dict):
    """
    Applies formatting for the new 4-column P&L report.
    """
    requests = []
    sheet_id = worksheet.id

    # --- Define Colors Locally ---
    L_PURPLE_HEADER_TEXT = {"red": 0.44, "green": 0.19, "blue": 0.63}
    L_WHITE_BG = {"red": 1.0, "green": 1.0, "blue": 1.0}
    L_UNCA_BG = {"red": 0.945, "green": 0.725, "blue": 0.725} # Eyedropped red
    L_ITEM_BG = {"red": 0.91, "green": 0.898, "blue": 0.93} # Eyedropped light purple
    L_BORDER_COLOR = {"red": 0.7, "green": 0.7, "blue": 0.7} # Gray border
    L_ACTUAL_TEXT = {"red": 0.2, "green": 0.2, "blue": 0.2}

    # --- Define reusable formats ---
    currency_format = {"numberFormat": {"type": "CURRENCY", "pattern": "$#,##0.00"}}

    # 1. Apply Currency Formatting to Column B and Column D (starting from row 5 - items)
    # --- CHANGED: startRowIndex is now 4 (Row 5), which is the first item row ---
    for col_start in [1, 3]: # Col B (index 1) and Col D (index 3)
        requests.append({
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": 4, "endRowIndex": num_rows + 1, # Start from item row (row 5, index 4)
                    "startColumnIndex": col_start, "endColumnIndex": col_start + 1,
                },
                "cell": {"userEnteredFormat": currency_format},
                "fields": "userEnteredFormat.numberFormat"
            }
        })

    # 2. Format Main Title (Row 1)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4},
            "cell": {"userEnteredFormat": {
                "textFormat": {"bold": True, "fontSize": 18, "foregroundColor": L_PURPLE_HEADER_TEXT}
            }},
            "fields": "userEnteredFormat.textFormat"
        }
    })
    requests.append({"mergeCells": {
        "range": {"sheetId": sheet_id, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 4},
        "mergeType": "MERGE_ALL"
    }})

    # 3. Format Section Headers & TOTALS (Row 2) - PURPLE TEXT, WHITE BACKGROUND
    # --- CHANGED: This section now also formats the totals in B2 and D2 ---

    # Format "Operating Expenses" (A2)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 0, "endColumnIndex": 1},
            "cell": {"userEnteredFormat": {
                "backgroundColor": L_WHITE_BG,
                "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": L_PURPLE_HEADER_TEXT}
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor)"
        }
    })
    # Format Expense Total (B2)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 1, "endColumnIndex": 2},
            "cell": {"userEnteredFormat": {
                "backgroundColor": L_WHITE_BG,
                "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": L_PURPLE_HEADER_TEXT},
                "numberFormat": currency_format["numberFormat"] # Add currency format
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor,numberFormat)"
        }
    })
    # Format "Income" (C2)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 2, "endColumnIndex": 3},
            "cell": {"userEnteredFormat": {
                "backgroundColor": L_WHITE_BG,
                "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": L_PURPLE_HEADER_TEXT}
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor)"
        }
    })
    # Format Income Total (D2)
    requests.append({
        "repeatCell": {
            "range": {"sheetId": sheet_id, "startRowIndex": 1, "endRowIndex": 2, "startColumnIndex": 3, "endColumnIndex": 4},
            "cell": {"userEnteredFormat": {
                "backgroundColor": L_WHITE_BG,
                "textFormat": {"bold": True, "fontSize": 14, "foregroundColor": L_PURPLE_HEADER_TEXT},
                "numberFormat": currency_format["numberFormat"] # Add currency format
            }},
            "fields": "userEnteredFormat(textFormat,backgroundColor,numberFormat)"
        }
    })

    # 4. Format Sub-Headers (Row 3) - "Actual" (No change needed)
    actual_format = {
        "textFormat": {
            "bold": True,
            "foregroundColor": L_ACTUAL_TEXT,
            "underline": True
        },
        "horizontalAlignment": "RIGHT"
    }
    requests.append({"repeatCell": { # B3
        "range": {"sheetId": sheet_id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 1, "endColumnIndex": 2},
        "cell": {"userEnteredFormat": actual_format}, "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
    }})
    requests.append({"repeatCell": { # D3
        "range": {"sheetId": sheet_id, "startRowIndex": 2, "endRowIndex": 3, "startColumnIndex": 3, "endColumnIndex": 4},
        "cell": {"userEnteredFormat": actual_format}, "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
    }})

    # 5. --- DELETED: Old Totals Row (Row 5) formatting is no longer needed ---

    # 6. Format Divider Line (Row 4)
    # --- CHANGED: Row index updated from 5/6 to 3/4 ---
    border = {"style": "SOLID", "width": 1, "color": L_BORDER_COLOR}
    requests.append({"repeatCell": {
        "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 0, "endColumnIndex": 2},
        "cell": {"userEnteredFormat": {"borders": {"top": border}}},
        "fields": "userEnteredFormat.borders.top"
    }})
    requests.append({"mergeCells": {
        "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 0, "endColumnIndex": 2},
        "mergeType": "MERGE_ALL"
    }})
    requests.append({"repeatCell": {
        "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 2, "endColumnIndex": 4},
        "cell": {"userEnteredFormat": {"borders": {"top": border}}},
        "fields": "userEnteredFormat.borders.top"
    }})
    requests.append({"mergeCells": {
        "range": {"sheetId": sheet_id, "startRowIndex": 3, "endRowIndex": 4, "startColumnIndex": 2, "endColumnIndex": 4},
        "mergeType": "MERGE_ALL"
    }})

    # 7. Apply background and bold to NON-EMPTY label cells (Row 5+, where items start)
    # --- CHANGED: Row index updated from 6 to 4 ---

    # Rule for Expense Labels (Col A, starting from row 5)
    non_empty_rule_exp = {
        "ranges": [
            {"sheetId": sheet_id, "startRowIndex": 4, "endRowIndex": num_rows + 1, "startColumnIndex": 0, "endColumnIndex": 1}
        ],
        "booleanRule": {
            "condition": {
                "type": "NOT_BLANK"
            },
            "format": {
                "backgroundColor": L_ITEM_BG,
                "textFormat": {"bold": True}
            }
        }
    }

    # Rule for Income Labels (Col C, starting from row 5)
    non_empty_rule_inc = {
        "ranges": [
            {"sheetId": sheet_id, "startRowIndex": 4, "endRowIndex": num_rows + 1, "startColumnIndex": 2, "endColumnIndex": 3}
        ],
        "booleanRule": {
            "condition": {
                "type": "NOT_BLANK"
            },
            "format": {
                "backgroundColor": L_ITEM_BG,
                "textFormat": {"bold": True}
            }
        }
    }

    requests.append({"addConditionalFormatRule": {"rule": non_empty_rule_exp, "index": 0}})
    requests.append({"addConditionalFormatRule": {"rule": non_empty_rule_inc, "index": 1}})


    # 8. Conditional Formatting for "Uncategorized" (starting from row 5)
    # --- CHANGED: Row index updated from 6 to 4, and formula from $A7 to $A5 ---

    uncategorized_rule_exp = {
        "ranges": [
            {"sheetId": sheet_id, "startRowIndex": 4, "endRowIndex": num_rows + 1, "startColumnIndex": 0, "endColumnIndex": 2}
        ],
        "booleanRule": {
            "condition": {
                "type": "CUSTOM_FORMULA",
                "values": [{"userEnteredValue": "=REGEXMATCH($A5, \"Uncategorized\")"}]
            },
            "format": {"backgroundColor": L_UNCA_BG}
        }
    }

    uncategorized_rule_inc = {
        "ranges": [
            {"sheetId": sheet_id, "startRowIndex": 4, "endRowIndex": num_rows + 1, "startColumnIndex": 2, "endColumnIndex": 4}
        ],
        "booleanRule": {
            "condition": {
                "type": "CUSTOM_FORMULA",
                "values": [{"userEnteredValue": "=REGEXMATCH($C5, \"Uncategorized\")"}]
            },
            "format": {"backgroundColor": L_UNCA_BG}
        }
    }

    requests.append({"addConditionalFormatRule": {"rule": uncategorized_rule_exp, "index": 2}})
    requests.append({"addConditionalFormatRule": {"rule": uncategorized_rule_inc, "index": 3}})


    # 9. Autofit column widths (No change needed)
    requests.append({
        "autoResizeDimensions": {
            "dimensions": {"sheetId": sheet_id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 4}
        }
    })

    # 10. Hide grid lines for cleaner appearance (No change needed)
    requests.append({
        "updateSheetProperties": {
            "properties": {
                "sheetId": sheet_id,
                "gridProperties": {
                    "hideGridlines": True
                }
            },
            "fields": "gridProperties.hideGridlines"
        }
    })

    worksheet.spreadsheet.batch_update({"requests": requests})
