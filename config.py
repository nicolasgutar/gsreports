# config.py
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration settings for the reports application.
    Reads from environment variables with fallback defaults.
    """

    # Database Configuration (single connection string)
    DB_URL: str = os.getenv('DB_URL', '')

    # Application Settings
    DEFAULT_TRANSACTION_LIMIT: int = int(os.getenv('DEFAULT_TRANSACTION_LIMIT', '1000'))

    # Date Range Settings (optional)
    REPORT_START_DATE: Optional[str] = os.getenv('REPORT_START_DATE', None)
    REPORT_END_DATE: Optional[str] = os.getenv('REPORT_END_DATE', None)

    @classmethod
    def get_db_config(cls) -> dict:
        """
        Get database configuration as a dictionary.

        Returns:
            Dictionary with database connection string
        """
        return {
            'connection_string': cls.DB_URL
        }

    @classmethod
    def validate(cls) -> bool:
        """
        Validate that required configuration is present.

        Returns:
            True if configuration is valid, False otherwise
        """
        if not cls.DB_URL:
            print("⚠ WARNING: DB_URL is not set!")
            print("   Set DB_URL environment variable with format:")
            print("   DB_URL=postgresql://user:password@host:port/database")
            return False

        return True

    @classmethod
    def print_config(cls):
        """
        Print current configuration (without sensitive data).
        """
        print("\n=== Configuration ===")
        if cls.DB_URL:
            # Parse and display connection info without password
            import re
            match = re.search(r'postgresql://([^:]+):[^@]+@([^/]+)/(.+)', cls.DB_URL)
            if match:
                user, host, database = match.groups()
                print(f"Database URL: postgresql://{user}:***@{host}/{database}")
            else:
                print(f"Database URL: [configured]")
        else:
            print("Database URL: (not set)")

        print(f"Transaction Limit: {cls.DEFAULT_TRANSACTION_LIMIT}")
        if cls.REPORT_START_DATE:
            print(f"Report Start Date: {cls.REPORT_START_DATE}")
        if cls.REPORT_END_DATE:
            print(f"Report End Date: {cls.REPORT_END_DATE}")
        print("====================\n")

