# balance_sheet_queries.py
from db_connector import DatabaseConnector


def get_cash_balance(db_connector: DatabaseConnector,
                     user_id: str) -> float:
    """
    Get total cash from checking accounts.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total balance from checking accounts
    """
    query = """
    SELECT COALESCE(SUM(balance), 0) as total_cash
    FROM "Account"
    WHERE user_id = %s
      AND type = 'checking'
    """

    result = db_connector.execute_single(query, (user_id,))
    return float(result[0]) if result and result[0] is not None else 0.0


def get_accounts_receivable(db_connector: DatabaseConnector,
                            user_id: str) -> float:
    """
    Get total accounts receivable from unpaid invoices with future due dates.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total unpaid invoices amount
    """
    query = """
    SELECT COALESCE(SUM(amount), 0) as total_receivable
    FROM "Invoice"
    WHERE "userId" = %s
      AND "dueDate" > NOW()
      AND status != 'Paid'
    """

    result = db_connector.execute_single(query, (user_id,))
    return float(result[0]) if result and result[0] is not None else 0.0


def get_other_receivables(db_connector: DatabaseConnector,
                          user_id: str) -> float:
    """
    Get other receivables (placeholder for future implementation).

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total other receivables (currently 0)
    """
    # TODO: Implement when requirements are defined
    return 0.0


def get_business_savings(db_connector: DatabaseConnector,
                         user_id: str) -> float:
    """
    Get total business savings from savings accounts.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total balance from savings accounts
    """
    query = """
    SELECT COALESCE(SUM(balance), 0) as total_savings
    FROM "Account"
    WHERE user_id = %s
      AND type = 'savings'
    """

    result = db_connector.execute_single(query, (user_id,))
    return float(result[0]) if result and result[0] is not None else 0.0


def get_business_equipment(db_connector: DatabaseConnector,
                           user_id: str,
                           start_date: str = None,
                           end_date: str = None) -> float:
    """
    Get total spent on Business Equipment category.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        Total amount spent on Business Equipment
    """
    if start_date and end_date:
        query = """
        SELECT COALESCE(SUM(ABS(amount)), 0) as total_equipment
        FROM "Transaction"
        WHERE "userId" = %s
          AND category = 'Business Equipment'
          AND amount < 0
          AND date >= %s 
          AND date <= %s
        """
        params = (user_id, start_date, end_date)
    else:
        query = """
        SELECT COALESCE(SUM(ABS(amount)), 0) as total_equipment
        FROM "Transaction"
        WHERE "userId" = %s
          AND category = 'Business Equipment'
          AND amount < 0
        """
        params = (user_id,)

    result = db_connector.execute_single(query, params)
    return float(result[0]) if result and result[0] is not None else 0.0


def get_inventory(db_connector: DatabaseConnector,
                  user_id: str,
                  start_date: str = None,
                  end_date: str = None) -> float:
    """
    Get total inventory value from relevant categories.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        Total inventory value
    """
    if start_date and end_date:
        query = """
                SELECT COALESCE(SUM(ABS(amount)), 0) as total_inventory
                FROM "Transaction"
                WHERE "userId" = %s
                  AND (category LIKE '%%Inventory%%' OR category LIKE '%%marketplace%%')
                  AND amount < 0
                  AND date >= %s
                  AND date <= %s \
                """
        params = (user_id, start_date, end_date)
    else:
        query = """
                SELECT COALESCE(SUM(ABS(amount)), 0) as total_inventory
                FROM "Transaction"
                WHERE "userId" = %s
                  AND (category LIKE '%%Inventory%%' OR category LIKE '%%marketplace%%')
                  AND amount < 0 \
                """
        params = (user_id,)

    result = db_connector.execute_single(query, params)
    return float(result[0]) if result and result[0] is not None else 0.0


def get_prepaid_expenses(db_connector: DatabaseConnector,
                        user_id: str) -> float:
    """
    Get prepaid expenses (placeholder for future implementation).

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total prepaid expenses (currently 0)
    """
    # TODO: Implement when requirements are defined
    return 0.0


def get_credit_card_debt(db_connector: DatabaseConnector,
                        user_id: str) -> float:
    """
    Get total credit card and debt account balances.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total credit card and debt balances
    """
    query = """
    SELECT COALESCE(SUM(ABS(balance)), 0) as total_debt
    FROM "Account"
    WHERE user_id = %s
      AND (type = 'credit' OR type = 'debt')
    """

    result = db_connector.execute_single(query, (user_id,))
    return float(result[0]) if result and result[0] is not None else 0.0


def get_business_loans(db_connector: DatabaseConnector,
                      user_id: str) -> float:
    """
    Get business loans (placeholder for future implementation).
    Could be split into multiple loan accounts.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total business loans (currently 0)
    """
    # TODO: Implement when loan tracking is defined
    # This might come from a separate Loans table or specific account types
    return 0.0


def get_taxes_payable(db_connector: DatabaseConnector,
                     user_id: str,
                     start_date: str = None,
                     end_date: str = None) -> float:
    """
    Calculate taxes payable as 1/3 of total income.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        Estimated taxes payable (33% of income)
    """
    if start_date and end_date:
        query = """
        SELECT COALESCE(SUM(amount), 0) as total_income
        FROM "Transaction"
        WHERE "userId" = %s
          AND amount > 0
          AND date >= %s 
          AND date <= %s
        """
        params = (user_id, start_date, end_date)
    else:
        query = """
        SELECT COALESCE(SUM(amount), 0) as total_income
        FROM "Transaction"
        WHERE "userId" = %s
          AND amount > 0
        """
        params = (user_id,)

    result = db_connector.execute_single(query, params)
    total_income = float(result[0]) if result and result[0] is not None else 0.0

    return total_income * 0.33


def get_owner_contribution(db_connector: DatabaseConnector,
                          user_id: str) -> float:
    """
    Get owner's contribution to the business (placeholder).

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID

    Returns:
        Total owner's contribution (currently 0)
    """
    # TODO: Implement when equity tracking is defined
    # This might come from a specific account or transaction category
    return 0.0


def get_owner_withdrawal(db_connector: DatabaseConnector,
                        user_id: str,
                        start_date: str = None,
                        end_date: str = None) -> float:
    """
    Get owner's withdrawals from the business (placeholder).

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)

    Returns:
        Total owner's withdrawals (currently 0)
    """
    # TODO: Implement when withdrawal tracking is defined
    # This might come from a specific transaction category
    return 0.0


def get_all_balance_sheet_data(db_connector: DatabaseConnector,
                               user_id: str,
                               start_date: str = None,
                               end_date: str = None) -> dict:
    """
    Get all balance sheet data in one call.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date for transaction-based calculations
        end_date: Optional end date for transaction-based calculations

    Returns:
        Dictionary with all balance sheet line items
    """
    print(f"\n--- Fetching Balance Sheet Data for User: {user_id} ---")

    data = {
        # Assets
        "Cash": get_cash_balance(db_connector, user_id),
        "Accounts Receivable": get_accounts_receivable(db_connector, user_id),
        "Other Receivables": get_other_receivables(db_connector, user_id),
        "Business Savings/Reserves": get_business_savings(db_connector, user_id),
        "Business Equipment (Asset)": get_business_equipment(db_connector, user_id, start_date, end_date),
        "Inventory": get_inventory(db_connector, user_id, start_date, end_date),
        "Prepaid Expenses": get_prepaid_expenses(db_connector, user_id),

        # Liabilities
        "Loan Payments / Credit Cards": get_credit_card_debt(db_connector, user_id),
        "Business Loans 1": get_business_loans(db_connector, user_id),
        "Business Loans 2": 0.0,  # Placeholder for second loan
        "Taxes Payable": get_taxes_payable(db_connector, user_id, start_date, end_date),

        # Equity
        "Owner's Contribution": get_owner_contribution(db_connector, user_id),
        "Owner's Withdrawal": get_owner_withdrawal(db_connector, user_id, start_date, end_date),
    }

    print("✓ Balance Sheet data fetched successfully")
    return data

