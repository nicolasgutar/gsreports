# db_connector.py
import psycopg2
from psycopg2 import pool
from typing import List, Tuple, Any, Optional
import os
from contextlib import contextmanager

class DatabaseConnector:
    """
    Simple database connector using psycopg2 with connection pooling.
    Uses a single connection string from DB_URL environment variable.
    """

    def __init__(self,
                 connection_string: str = None,
                 min_conn: int = 1,
                 max_conn: int = 10):
        """
        Initialize database connector with connection pooling.

        Args:
            connection_string: PostgreSQL connection string
                             (e.g., 'postgresql://user:password@localhost:5433/investrio')
                             Defaults to env var DB_URL
            min_conn: Minimum number of connections in pool
            max_conn: Maximum number of connections in pool
        """
        self.connection_string = connection_string or os.getenv('DB_URL', '')

        if not self.connection_string:
            raise ValueError(
                "No database connection string provided. "
                "Set DB_URL environment variable or pass connection_string parameter."
            )

        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                min_conn,
                max_conn,
                self.connection_string
            )

            if self.connection_pool:
                # Parse connection string to show info (without password)
                import re
                match = re.search(r'postgresql://([^:]+):[^@]+@([^/]+)/(.+)', self.connection_string)
                if match:
                    user, host, database = match.groups()
                    print(f"✓ Database connection pool created successfully")
                    print(f"  Host: {host}")
                    print(f"  Database: {database}")
                    print(f"  User: {user}")
                else:
                    print(f"✓ Database connection pool created successfully")
        except (Exception, psycopg2.Error) as error:
            print(f"❌ Error creating connection pool: {error}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Context manager for getting a connection from the pool.
        Automatically returns the connection to the pool when done.
        """
        conn = None
        try:
            conn = self.connection_pool.getconn()
            yield conn
        finally:
            if conn:
                self.connection_pool.putconn(conn)

    def execute_query(self, query: str, params: Tuple = None) -> List[Tuple[Any, ...]]:
        """
        Execute a SELECT query and return results.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            List of tuples with query results
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                return results
            except (Exception, psycopg2.Error) as error:
                print(f"❌ Error executing query: {error}")
                raise

    def execute_single(self, query: str, params: Tuple = None) -> Optional[Tuple[Any, ...]]:
        """
        Execute a query and return a single row.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Single tuple or None if no results
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchone()
                cursor.close()
                return result
            except (Exception, psycopg2.Error) as error:
                print(f"❌ Error executing query: {error}")
                raise

    def execute_update(self, query: str, params: Tuple = None) -> int:
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Args:
            query: SQL query string
            params: Query parameters tuple

        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
            except (Exception, psycopg2.Error) as error:
                conn.rollback()
                print(f"❌ Error executing update: {error}")
                raise

    def close_all_connections(self):
        """
        Close all connections in the pool.
        """
        if self.connection_pool:
            self.connection_pool.closeall()
            print("✓ All database connections closed")

