# Financial Reports Generator

Generate comprehensive financial reports (P&L, Balance Sheet, and Transaction Details) from transaction data and export them to Google Sheets.

## Features

- **Database Integration**: Fetch transaction data from PostgreSQL database
- **Sample Data Mode**: Test with sample data without database connection
- **Automated Report Generation**: 
  - Profit & Loss Statement
  - Balance Sheet
  - Raw Transaction Data
- **Google Sheets Export**: Automatically creates and formats reports in Google Sheets
- **Date Range Filtering**: Generate reports for specific time periods
- **Modular Architecture**: Clean separation of concerns for easy maintenance
- **PILA Planillas Parser**: Parse and match PILA payroll forms with financial logs (see [PLANILLAS_README.md](PLANILLAS_README.md))

## Project Structure

```
gsreports/
├── main.py                      # Main application entry point
├── config.py                    # Configuration management
├── db_connector.py              # Database connection handler
├── db_queries.py                # SQL queries for data retrieval
├── transaction_processor.py    # Transaction processing logic
├── pnl.py                       # P&L report generation
├── balance_sheet.py             # Balance Sheet generation
├── utils.py                     # Google API utilities
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── client_secret.json           # Google OAuth credentials (create this)
├── README.md                    # This file
├── PLANILLAS_README.md          # PILA planillas parser documentation
├── notebooks/
│   └── BuscandoEnLog.ipynb      # PILA planillas matching notebook
├── src/
│   └── parsers/
│       └── txt_parser.py        # Planilla parser functions
└── Planillas/                   # Directory for planilla files
```

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download the credentials and save as `client_secret.json` in the project directory

### 3. Configure Database Connection

Copy the example environment file:

```bash
copy .env.example .env
```

Edit `.env` and fill in your database credentials:

```env
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
USE_SAMPLE_DATA=False
```

**Note**: On Windows, you can also set environment variables directly:

```cmd
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=mydb
set DB_USER=postgres
set DB_PASSWORD=mypassword
```

## Usage

### Using Database Data

1. Ensure your database is running and environment variables are set
2. Run the application:

```bash
python main.py
```

3. Enter the user ID when prompted
4. The script will:
   - Fetch transactions from the database
   - Process data for P&L and Balance Sheet
   - Create a Google Sheet with three tabs
   - Return a shareable link

### Using Sample Data

To test without a database connection:

```bash
set USE_SAMPLE_DATA=True
python main.py
```

Or edit your `.env` file:
```env
USE_SAMPLE_DATA=True
```

### Date Range Reports

To generate reports for a specific period, set these environment variables:

```bash
set REPORT_START_DATE=2024-01-01
set REPORT_END_DATE=2024-12-31
python main.py
```

## Database Schema

The application expects a `Transaction` table with the following structure:

```sql
CREATE TABLE "Transaction" (
    id TEXT PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "accountFrom" TEXT,
    name TEXT,
    amount DECIMAL,
    description TEXT,
    "receiptUrl" TEXT,
    category TEXT,
    "categoryId" TEXT,
    subcategory TEXT,
    "subcategoryId" TEXT,
    "plaidCategory" TEXT,
    "plaidSubcategory" TEXT,
    "plaidPrimary" TEXT,
    "plaidDetailed" TEXT,
    "plaidConfidenceLevel" TEXT,
    "plaidCategoryUrl" TEXT,
    "transactionId" TEXT,
    "accountId" TEXT,
    "isoCurrencyCode" TEXT,
    "unofficialCurrencyCode" TEXT,
    date DATE,
    year INTEGER,
    month INTEGER,
    "merchantName" TEXT,
    "merchantLogo" TEXT,
    "paymentChannel" TEXT,
    "paymentMeta" JSONB,
    "referenceNumber" TEXT,
    "transactionCode" TEXT,
    "accountCategory" TEXT,
    status TEXT,
    "createdAt" TIMESTAMP,
    "updatedAt" TIMESTAMP
);
```

**Important**: The query filters for `category IS NOT NULL` to only include categorized transactions.

## Module Documentation

### db_connector.py
- `DatabaseConnector`: Manages PostgreSQL connections with connection pooling
- Provides context managers for safe connection handling
- Supports query execution and transaction management

### db_queries.py
- `get_user_transactions()`: Fetch recent transactions for a user
- `get_transactions_by_date_range()`: Get transactions within date range
- `get_income_summary_by_category()`: Aggregate income by category
- `get_expense_summary_by_category()`: Aggregate expenses by category
- `get_balance_sheet_data()`: Retrieve balance sheet data (customizable)
- `get_account_summary()`: Get account summaries with balances

### transaction_processor.py
- `process_transactions_for_pnl()`: Convert transactions to P&L line items
- `process_transactions_for_balance_sheet()`: Calculate balance sheet values
- `create_transactions_dataframe()`: Format transactions for display
- `apply_transactions_formatting()`: Apply Google Sheets formatting

### pnl.py
- `generate_pnl_report()`: Create P&L DataFrame
- `apply_pnl_formatting()`: Apply formatting to P&L sheet

### balance_sheet.py
- `generate_balance_sheet()`: Create Balance Sheet DataFrame
- `apply_balance_sheet_formatting()`: Apply formatting to Balance Sheet

### config.py
- `Config`: Centralized configuration management
- Reads from environment variables
- Provides validation and debugging utilities

## Customization

### Adding New P&L Categories

Edit `transaction_processor.py` in the `process_transactions_for_pnl()` function:

```python
pnl_data = {
    # ... existing categories ...
    "Your New Category": 0.0,
}
```

Then add the mapping logic in the transaction processing loop.

### Modifying Balance Sheet Structure

Edit `balance_sheet.py` to add or modify line items in the `generate_balance_sheet()` function.

### Custom SQL Queries

Add new queries to `db_queries.py` following the existing patterns.

## Troubleshooting

### Database Connection Issues

```
❌ Error creating connection pool
```

**Solution**: 
- Verify database credentials in environment variables
- Ensure PostgreSQL is running
- Check network connectivity to database host

### Google API Errors

```
❌ HTTP Error: accessNotConfigured
```

**Solution**:
- Enable Google Sheets API and Google Drive API in Google Cloud Console
- Verify `client_secret.json` is in the project directory

### No Transactions Found

```
⚠ WARNING: No transactions found for this user
```

**Solution**:
- Verify the user ID exists in the database
- Check that transactions have non-null `category` values
- Adjust date range if using `REPORT_START_DATE` and `REPORT_END_DATE`

### Import Errors

```
ModuleNotFoundError: No module named 'psycopg2'
```

**Solution**:
```bash
pip install -r requirements.txt
```

## Development

### Running in Development Mode

Use sample data for testing:

```bash
set USE_SAMPLE_DATA=True
python main.py
```

### Adding New Features

1. Create feature-specific modules in the project directory
2. Import and integrate in `main.py`
3. Update configuration in `config.py` if needed
4. Document changes in this README

## Security Notes

- Never commit `.env` files or `client_secret.json` to version control
- Use `.gitignore` to exclude sensitive files:
  ```
  .env
  client_secret.json
  token.json
  credentials.json
  __pycache__/
  *.pyc
  ```
- Store production credentials securely (e.g., environment variables, secret managers)

## License

[Your License Here]

## Support

For issues or questions, please contact [Your Contact Info]

