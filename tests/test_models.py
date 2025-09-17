#!/usr/bin/env python3
"""
Tests for models.py - Process model and BaseModel
"""
import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.models import Process
from src.database import db_manager


@pytest.fixture
def reset_mocks(monkeypatch):
    """Reset database mocks for each test"""
    monkeypatch.setattr(db_manager, "execute_query", lambda q, p=None: [], raising=True)
    monkeypatch.setattr(db_manager, "execute_update", lambda q, p=None: 1, raising=True)
    return monkeypatch


class TestProcess:
    """Test Process model functionality"""
    
    def test_process_creation(self):
        """Test Process object creation"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description"
        )
        
        assert process.name == "Test_Process"
        assert process.node == "28nm"
        assert process.fab == "TSMC"
        assert process.description == "Test process description"
        assert process.id is None
        assert process.created_at is None
        assert process.updated_at is None
    
    def test_process_creation_with_kwargs(self):
        """Test Process creation with additional kwargs"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=1,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        assert process.id == 1
        assert process.created_at == "2023-01-01 00:00:00"
        assert process.updated_at == "2023-01-01 00:00:00"
    
    def test_to_dict(self):
        """Test Process to_dict method"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=1,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        result = process.to_dict()
        expected = {
            'id': 1,
            'name': 'Test_Process',
            'node': '28nm',
            'fab': 'TSMC',
            'description': 'Test process description',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test Process from_dict method"""
        data = {
            'id': 1,
            'name': 'Test_Process',
            'node': '28nm',
            'fab': 'TSMC',
            'description': 'Test process description',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        process = Process.from_dict(data)
        
        assert process.id == 1
        assert process.name == 'Test_Process'
        assert process.node == '28nm'
        assert process.fab == 'TSMC'
        assert process.description == 'Test process description'
        assert process.created_at == '2023-01-01 00:00:00'
        assert process.updated_at == '2023-01-01 00:00:00'
    
    def test_from_dict_with_missing_fields(self):
        """Test Process from_dict with missing optional fields"""
        data = {
            'id': 1,
            'name': 'Test_Process',
            'node': '28nm',
            'fab': 'TSMC'
        }
        
        process = Process.from_dict(data)
        
        assert process.id == 1
        assert process.name == 'Test_Process'
        assert process.node == '28nm'
        assert process.fab == 'TSMC'
        assert process.description == ''  # Default value
        assert process.created_at is None
        assert process.updated_at is None
    
    def test_save_new_process(self, reset_mocks, monkeypatch):
        """Test saving a new process"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description"
        )
        
        # Mock the database responses
        def mock_execute_update(query, params):
            return 1
        
        def mock_execute_query(query, params=None):
            if "LAST_INSERT_ID" in query:
                return [{'id': 123}]
            return []
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = process.save()
        
        assert result is True
        assert process.id == 123
    
    def test_save_existing_process(self, reset_mocks, monkeypatch):
        """Test saving an existing process"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = process.save()
        
        assert result is True
    
    def test_save_database_error(self, reset_mocks, monkeypatch):
        """Test save method with database error"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description"
        )
        
        def mock_execute_update(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = process.save()
        
        assert result is False
    
    def test_delete_success(self, reset_mocks, monkeypatch):
        """Test successful deletion"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = process.delete()
        
        assert result is True
    
    def test_delete_no_id(self):
        """Test deletion without ID"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description"
        )
        
        result = process.delete()
        
        assert result is False
    
    def test_delete_database_error(self, reset_mocks, monkeypatch):
        """Test deletion with database error"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=123
        )
        
        def mock_execute_update(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = process.delete()
        
        assert result is False
    
    def test_find_by_id_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_id"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_Process',
                'node': '28nm',
                'fab': 'TSMC',
                'description': 'Test process description',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_id(123)
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_Process'
    
    def test_find_by_id_not_found(self, reset_mocks, monkeypatch):
        """Test find_by_id when not found"""
        def mock_execute_query(query, params):
            return []
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_id(123)
        
        assert result is None
    
    def test_find_by_id_database_error(self, reset_mocks, monkeypatch):
        """Test find_by_id with database error"""
        def mock_execute_query(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_id(123)
        
        assert result is None
    
    def test_find_by_name_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_name"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_Process',
                'node': '28nm',
                'fab': 'TSMC',
                'description': 'Test process description',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_name("Test_Process")
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_Process'
    
    def test_find_by_name_not_found(self, reset_mocks, monkeypatch):
        """Test find_by_name when not found"""
        def mock_execute_query(query, params):
            return []
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_name("NonExistent")
        
        assert result is None
    
    def test_find_all_success(self, reset_mocks, monkeypatch):
        """Test successful find_all"""
        def mock_execute_query(query):
            return [
                {
                    'id': 1,
                    'name': 'Process1',
                    'node': '28nm',
                    'fab': 'TSMC',
                    'description': 'Process 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                },
                {
                    'id': 2,
                    'name': 'Process2',
                    'node': '7nm',
                    'fab': 'Samsung',
                    'description': 'Process 2',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_all()
        
        assert len(result) == 2
        assert result[0].name == 'Process1'
        assert result[1].name == 'Process2'
    
    def test_find_all_database_error(self, reset_mocks, monkeypatch):
        """Test find_all with database error"""
        def mock_execute_query(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_all()
        
        assert result == []
    
    def test_find_by_fab_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_fab"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 1,
                    'name': 'Process1',
                    'node': '28nm',
                    'fab': 'TSMC',
                    'description': 'Process 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_fab("TSMC")
        
        assert len(result) == 1
        assert result[0].fab == 'TSMC'
    
    def test_find_by_fab_database_error(self, reset_mocks, monkeypatch):
        """Test find_by_fab with database error"""
        def mock_execute_query(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Process.find_by_fab("TSMC")
        
        assert result == []
    
    def test_str_representation(self):
        """Test string representation"""
        process = Process(
            name="Test_Process",
            node="28nm",
            fab="TSMC",
            description="Test process description",
            id=123
        )
        
        expected = "Process(id=123, name='Test_Process', node='28nm', fab='TSMC')"
        assert str(process) == expected
        assert repr(process) == expected

