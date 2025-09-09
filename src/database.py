"""
Database connection and management module for IPLM
"""
import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from typing import Optional, Dict, Any, List
import logging
from config.settings import DATABASE_CONFIG, get_schema_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self):
        self.config = DATABASE_CONFIG
        self.connection = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            return False
        return False
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection closed")
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor(dictionary=True)
        try:
            yield cursor
        except Error as e:
            logger.error(f"Database error: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.rowcount
    
    def create_tables(self):
        """Create database tables based on schema configuration"""
        schemas = get_schema_config()
        
        for table_name, schema in schemas.items():
            self._create_table(table_name, schema)
    
    def _create_table(self, table_name: str, schema: Dict[str, Any]):
        """Create a single table based on schema"""
        columns = []
        for col_name, col_def in schema['columns'].items():
            columns.append(f"{col_name} {col_def}")
        
        # Add foreign keys if they exist
        if 'foreign_keys' in schema:
            for fk_name, fk_def in schema['foreign_keys'].items():
                columns.append(fk_def)
        
        # Add indexes if they exist
        if 'indexes' in schema:
            for idx_name, idx_def in schema['indexes'].items():
                columns.append(idx_def)
        
        create_query = f"""
        CREATE TABLE IF NOT EXISTS {schema['table_name']} (
            {', '.join(columns)}
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        
        try:
            self.execute_update(create_query)
            logger.info(f"Table {schema['table_name']} created successfully")
        except Error as e:
            logger.error(f"Error creating table {schema['table_name']}: {e}")
            raise

# Global database manager instance
db_manager = DatabaseManager()

