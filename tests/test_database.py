#!/usr/bin/env python3
"""
Tests for database.py - DatabaseManager
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.database import DatabaseManager


class TestDatabaseManager:
    """Test DatabaseManager functionality"""
    
    def test_init(self):
        """Test DatabaseManager initialization"""
        db_manager = DatabaseManager()
        
        assert db_manager.config is not None
        assert db_manager.connection is None
    
    @patch('src.database.mysql.connector.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection"""
        # Mock successful connection
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        result = db_manager.connect()
        
        assert result is True
        assert db_manager.connection == mock_connection
        mock_connect.assert_called_once_with(**db_manager.config)
    
    @patch('src.database.mysql.connector.connect')
    def test_connect_failure(self, mock_connect):
        """Test database connection failure"""
        # Mock connection failure
        mock_connect.side_effect = Exception("Connection failed")
        
        db_manager = DatabaseManager()

        with pytest.raises(Exception) as excinfo:
            result = db_manager.connect()
        assert 'Connection failed' in str(excinfo.value)
        assert db_manager.connection is None
    
    def test_disconnect_no_connection(self):
        """Test disconnect when no connection"""
        db_manager = DatabaseManager()
        db_manager.disconnect()  # Should not raise error
    
    def test_disconnect_with_connection(self):
        """Test disconnect with active connection"""
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        
        db_manager = DatabaseManager()
        db_manager.connection = mock_connection
        db_manager.disconnect()
        
        mock_connection.close.assert_called_once()
    
    def test_disconnect_connection_not_connected(self):
        """Test disconnect when connection is not connected"""
        mock_connection = Mock()
        mock_connection.is_connected.return_value = False
        
        db_manager = DatabaseManager()
        db_manager.connection = mock_connection
        db_manager.disconnect()
        
        mock_connection.close.assert_not_called()
    
    @patch('src.database.mysql.connector.connect')
    def test_get_cursor_success(self, mock_connect):
        """Test successful get_cursor context manager"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        
        with db_manager.get_cursor() as cursor:
            assert cursor == mock_cursor
        
        mock_cursor.close.assert_called_once()
    
    @patch('src.database.mysql.connector.connect')
    def test_get_cursor_not_connected(self, mock_connect):
        """Test get_cursor when not connected"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = False
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        db_manager.connection = None
        
        with db_manager.get_cursor() as cursor:
            assert cursor == mock_cursor
        
        mock_connect.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    @patch('src.database.mysql.connector.connect')
    def test_get_cursor_database_error(self, mock_connect):
        """Test get_cursor with database error"""
        from mysql.connector import Error
        
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        # Mock cursor to raise error
        mock_cursor.execute.side_effect = Error("Database error")
        
        db_manager = DatabaseManager()
        
        with pytest.raises(Error):
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT 1")
        
        mock_connection.rollback.assert_called_once()
        mock_cursor.close.assert_called_once()
    
    @patch('src.database.mysql.connector.connect')
    def test_execute_query_success(self, mock_connect):
        """Test successful execute_query"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test'}]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        result = db_manager.execute_query("SELECT * FROM test", (1,))
        
        assert result == [{'id': 1, 'name': 'test'}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", (1,))
        mock_cursor.fetchall.assert_called_once()
    
    @patch('src.database.mysql.connector.connect')
    def test_execute_query_no_params(self, mock_connect):
        """Test execute_query with no parameters"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'test'}]
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        result = db_manager.execute_query("SELECT * FROM test")
        
        assert result == [{'id': 1, 'name': 'test'}]
        mock_cursor.execute.assert_called_once_with("SELECT * FROM test", None)
    
    @patch('src.database.mysql.connector.connect')
    def test_execute_update_success(self, mock_connect):
        """Test successful execute_update"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        result = db_manager.execute_update("INSERT INTO test VALUES (%s)", (1,))
        
        assert result == 1
        mock_cursor.execute.assert_called_once_with("INSERT INTO test VALUES (%s)", (1,))
        mock_connection.commit.assert_called_once()
    
    @patch('src.database.mysql.connector.connect')
    def test_execute_update_no_params(self, mock_connect):
        """Test execute_update with no parameters"""
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        result = db_manager.execute_update("CREATE TABLE test (id INT)")
        
        assert result == 1
        mock_cursor.execute.assert_called_once_with("CREATE TABLE test (id INT)", None)
    
    @patch('src.database.get_schema_config')
    @patch('src.database.mysql.connector.connect')
    def test_create_tables_success(self, mock_connect, mock_get_schema):
        """Test successful create_tables"""
        # Mock schema configuration
        mock_schema = {
            'processes': {
                'table_name': 'processes',
                'columns': {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                    'name': 'VARCHAR(255) NOT NULL UNIQUE'
                }
            }
        }
        mock_get_schema.return_value = mock_schema
        
        # Mock connection and cursor
        mock_connection = Mock()
        mock_connection.is_connected.return_value = True
        mock_cursor = Mock()
        mock_cursor.rowcount = 1
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        db_manager = DatabaseManager()
        db_manager.create_tables()
        
        # Verify table creation was called
        mock_cursor.execute.assert_called()
        mock_connection.commit.assert_called()
    
    @patch('src.database.get_schema_config')
    def test_create_table_success(self, mock_get_schema):
        """Test successful _create_table"""
        # Mock schema configuration
        mock_schema = {
            'processes': {
                'table_name': 'processes',
                'columns': {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                    'name': 'VARCHAR(255) NOT NULL UNIQUE'
                }
            }
        }
        mock_get_schema.return_value = mock_schema
        
        db_manager = DatabaseManager()
        
        # Mock execute_update to avoid actual database call
        with patch.object(db_manager, 'execute_update') as mock_execute:
            db_manager._create_table('processes', mock_schema['processes'])
            
            # Verify the CREATE TABLE query was called
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]
            assert 'CREATE TABLE IF NOT EXISTS processes' in call_args[0]
            assert 'id INT AUTO_INCREMENT PRIMARY KEY' in call_args[0]
            assert 'name VARCHAR(255) NOT NULL UNIQUE' in call_args[0]
    
    @patch('src.database.get_schema_config')
    def test_create_table_with_foreign_keys(self, mock_get_schema):
        """Test _create_table with foreign keys"""
        # Mock schema configuration with foreign keys
        mock_schema = {
            'ips': {
                'table_name': 'ips',
                'columns': {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                    'type_id': 'INT NOT NULL'
                },
                'foreign_keys': {
                    'type_id': 'FOREIGN KEY (type_id) REFERENCES types(id)'
                }
            }
        }
        mock_get_schema.return_value = mock_schema
        
        db_manager = DatabaseManager()
        
        # Mock execute_update to avoid actual database call
        with patch.object(db_manager, 'execute_update') as mock_execute:
            db_manager._create_table('ips', mock_schema['ips'])
            
            # Verify the CREATE TABLE query includes foreign key
            call_args = mock_execute.call_args[0]
            assert 'FOREIGN KEY (type_id) REFERENCES types(id)' in call_args[0]
    
    @patch('src.database.get_schema_config')
    def test_create_table_with_indexes(self, mock_get_schema):
        """Test _create_table with indexes"""
        # Mock schema configuration with indexes
        mock_schema = {
            'types': {
                'table_name': 'types',
                'columns': {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                    'path': 'VARCHAR(500) NOT NULL'
                },
                'indexes': {
                    'path': 'INDEX idx_path (path(191))'
                }
            }
        }
        mock_get_schema.return_value = mock_schema
        
        db_manager = DatabaseManager()
        
        # Mock execute_update to avoid actual database call
        with patch.object(db_manager, 'execute_update') as mock_execute:
            db_manager._create_table('types', mock_schema['types'])
            
            # Verify the CREATE TABLE query includes index
            call_args = mock_execute.call_args[0]
            assert 'INDEX idx_path (path(191))' in call_args[0]
    
    @patch('src.database.get_schema_config')
    def test_create_table_database_error(self, mock_get_schema):
        """Test _create_table with database error"""
        from mysql.connector import Error
        
        # Mock schema configuration
        mock_schema = {
            'processes': {
                'table_name': 'processes',
                'columns': {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY'
                }
            }
        }
        mock_get_schema.return_value = mock_schema
        
        db_manager = DatabaseManager()
        
        # Mock execute_update to raise error
        with patch.object(db_manager, 'execute_update', side_effect=Error("Database error")):
            with pytest.raises(Error):
                db_manager._create_table('processes', mock_schema['processes'])

