# db_queries.py
from typing import List, Dict, Any
import json
from db_connector import DatabaseConnector

def get_user_transactions(db_connector: DatabaseConnector,
                          user_id: str,
                          start_date: str = None,
                          end_date: str = None,
                          limit: int = None) -> List[Dict[str, Any]]:
    """
    Get transactions for a specific user with optional date filtering.

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID to fetch transactions for
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        limit: Optional maximum number of transactions to return

    Returns:
        List[Dict]: List of transaction records
    """
    query = """
    SELECT id, "userId", "accountFrom", name, amount, description, "receiptUrl",
           category, "categoryId", subcategory, "subcategoryId", "plaidCategory",
           "plaidSubcategory", "plaidPrimary", "plaidDetailed", "plaidConfidenceLevel",
           "plaidCategoryUrl", "transactionId", "accountId", "isoCurrencyCode",
           "unofficialCurrencyCode", date, year, month, "merchantName", "merchantLogo",
           "paymentChannel", "paymentMeta", "referenceNumber", "transactionCode",
           "accountCategory", status, "createdAt", "updatedAt"
    FROM "Transaction"
    WHERE "userId" = %s
      AND category IS NOT NULL
    """

    params = [user_id]

    if start_date and end_date:
        query += " AND date >= %s AND date <= %s"
        params.extend([start_date, end_date])

    query += " ORDER BY date DESC, \"createdAt\" DESC"

    if limit:
        query += " LIMIT %s"
        params.append(str(limit))

    results = db_connector.execute_query(query, tuple(params))

    columns = ['id', 'userId', 'accountFrom', 'name', 'amount', 'description', 'receiptUrl',
               'category', 'categoryId', 'subcategory', 'subcategoryId', 'plaidCategory',
               'plaidSubcategory', 'plaidPrimary', 'plaidDetailed', 'plaidConfidenceLevel',
               'plaidCategoryUrl', 'transactionId', 'accountId', 'isoCurrencyCode',
               'unofficialCurrencyCode', 'date', 'year', 'month', 'merchantName', 'merchantLogo',
               'paymentChannel', 'paymentMeta', 'referenceNumber', 'transactionCode',
               'accountCategory', 'status', 'createdAt', 'updatedAt']

    transactions = []
    for row in results:
        transaction = dict(zip(columns, row))
        # Parse JSON fields
        if transaction['paymentMeta']:
            try:
                transaction['paymentMeta'] = json.loads(transaction['paymentMeta'])
            except (json.JSONDecodeError, TypeError):
                transaction['paymentMeta'] = {}
        transactions.append(transaction)

    return transactions


def get_transactions_grouped_by_category(db_connector: DatabaseConnector,
                                         user_id: str,
                                         start_date: str = None,
                                         end_date: str = None,
                                         account_category: str = None) -> Dict[str, Dict[str, float]]:
    """
    Get transactions grouped by category with computed totals for P&L report.
    Returns separate groups for income (amount > 0) and expenses (amount < 0).

    Args:
        db_connector: DatabaseConnector instance
        user_id: The user ID
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        account_category: Optional filter by accountCategory field ('personal' or 'Business')

    Returns:
        Dictionary with 'income' and 'expenses' keys, each containing category totals
    """
    # Income query (amount > 0)
    income_query = """
    SELECT 
        COALESCE(subcategory, category) as category_name,
        SUM(amount) as total
    FROM "Transaction"
    WHERE "userId" = %s
      AND category IS NOT NULL
      AND amount > 0
    """

    # Expense query (amount < 0)
    expense_query = """
    SELECT 
        COALESCE(subcategory, category) as category_name,
        SUM(ABS(amount)) as total
    FROM "Transaction"
    WHERE "userId" = %s
      AND category IS NOT NULL
      AND amount < 0
    """

    params = [user_id]

    # Add account_category filter if provided
    if account_category:
        account_filter = ' AND "accountCategory" = %s'
        income_query += account_filter
        expense_query += account_filter
        params.append(account_category)

    if start_date and end_date:
        date_filter = " AND date >= %s AND date <= %s"
        income_query += date_filter
        expense_query += date_filter
        params.extend([start_date, end_date])

    income_query += " GROUP BY COALESCE(subcategory, category)"
    expense_query += " GROUP BY COALESCE(subcategory, category)"

    # Execute income query with the constructed parameters
    income_results = db_connector.execute_query(income_query, tuple(params))
    income_summary = {}
    for row in income_results:
        category_name = row[0]
        total = float(row[1]) if row[1] else 0.0
        income_summary[category_name] = total

    # Execute expense query with the same parameters
    expense_results = db_connector.execute_query(expense_query, tuple(params))
    expense_summary = {}
    for row in expense_results:
        category_name = row[0]
        total = float(row[1]) if row[1] else 0.0
        expense_summary[category_name] = total

    return {
        'income': income_summary,
        'expenses': expense_summary
    }

