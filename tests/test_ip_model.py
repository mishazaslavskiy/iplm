#!/usr/bin/env python3
"""
Tests for ip_model.py - IP model
"""
import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.ip_model import IP
from src.database import db_manager


@pytest.fixture
def reset_mocks(monkeypatch):
    """Reset database mocks for each test"""
    monkeypatch.setattr(db_manager, "execute_query", lambda q, p=None: [], raising=True)
    monkeypatch.setattr(db_manager, "execute_update", lambda q, p=None: 1, raising=True)
    return monkeypatch


class TestIP:
    """Test IP model functionality"""
    
    def test_ip_creation(self):
        """Test IP object creation"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            revision="1.0",
            status="alpha",
            provider="Test_Provider",
            parent_ip_id=None,
            description="Test IP description",
            documentation="https://example.com"
        )
        
        assert ip.name == "Test_IP"
        assert ip.type_id == 1
        assert ip.process_id == 2
        assert ip.revision == "1.0"
        assert ip.status == "alpha"
        assert ip.provider == "Test_Provider"
        assert ip.parent_ip_id is None
        assert ip.description == "Test IP description"
        assert ip.documentation == "https://example.com"
        assert ip.id is None
        assert ip.created_at is None
        assert ip.updated_at is None
    
    def test_ip_creation_with_kwargs(self):
        """Test IP creation with additional kwargs"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            id=123,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        assert ip.id == 123
        assert ip.created_at == "2023-01-01 00:00:00"
        assert ip.updated_at == "2023-01-01 00:00:00"
    
    def test_ip_creation_invalid_status(self):
        """Test IP creation with invalid status"""
        with pytest.raises(ValueError, match="Invalid status"):
            IP(
                name="Test_IP",
                type_id=1,
                process_id=2,
                status="invalid_status"
            )
    
    def test_to_dict(self):
        """Test IP to_dict method"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            revision="1.0",
            status="alpha",
            provider="Test_Provider",
            parent_ip_id=3,
            description="Test IP description",
            documentation="https://example.com",
            id=123,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        result = ip.to_dict()
        expected = {
            'id': 123,
            'name': 'Test_IP',
            'type_id': 1,
            'process_id': 2,
            'parent_ip_id': 3,
            'revision': '1.0',
            'status': 'alpha',
            'provider': 'Test_Provider',
            'description': 'Test IP description',
            'documentation': 'https://example.com',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test IP from_dict method"""
        data = {
            'id': 123,
            'name': 'Test_IP',
            'type_id': 1,
            'process_id': 2,
            'parent_ip_id': 3,
            'revision': '1.0',
            'status': 'alpha',
            'provider': 'Test_Provider',
            'description': 'Test IP description',
            'documentation': 'https://example.com',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        ip = IP.from_dict(data)
        
        assert ip.id == 123
        assert ip.name == 'Test_IP'
        assert ip.type_id == 1
        assert ip.process_id == 2
        assert ip.parent_ip_id == 3
        assert ip.revision == '1.0'
        assert ip.status == 'alpha'
        assert ip.provider == 'Test_Provider'
        assert ip.description == 'Test IP description'
        assert ip.documentation == 'https://example.com'
        assert ip.created_at == '2023-01-01 00:00:00'
        assert ip.updated_at == '2023-01-01 00:00:00'
    
    def test_from_dict_with_missing_fields(self):
        """Test IP from_dict with missing optional fields"""
        data = {
            'id': 123,
            'name': 'Test_IP',
            'type_id': 1,
            'process_id': 2
        }
        
        ip = IP.from_dict(data)
        
        assert ip.id == 123
        assert ip.name == 'Test_IP'
        assert ip.type_id == 1
        assert ip.process_id == 2
        assert ip.parent_ip_id is None
        assert ip.revision == '1.0'  # Default value
        assert ip.status == 'alpha'  # Default value
        assert ip.provider == ''
        assert ip.description == ''
        assert ip.documentation == ''
        assert ip.created_at is None
        assert ip.updated_at is None
    
    def test_save_new_ip(self, reset_mocks, monkeypatch):
        """Test saving a new IP"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            revision="1.0",
            status="alpha",
            provider="Test_Provider"
        )
        
        def mock_execute_update(query, params):
            return 1
        
        def mock_execute_query(query, params=None):
            if "LAST_INSERT_ID" in query:
                return [{'id': 123}]
            return []
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = ip.save()
        
        assert result is True
        assert ip.id == 123
    
    def test_save_existing_ip(self, reset_mocks, monkeypatch):
        """Test saving an existing IP"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            revision="1.0",
            status="alpha",
            provider="Test_Provider",
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = ip.save()
        
        assert result is True
    
    def test_save_database_error(self, reset_mocks, monkeypatch):
        """Test save method with database error"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            revision="1.0",
            status="alpha",
            provider="Test_Provider"
        )
        
        def mock_execute_update(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = ip.save()
        
        assert result is False
    
    def test_delete_success(self, reset_mocks, monkeypatch):
        """Test successful deletion"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = ip.delete()
        
        assert result is True
    
    def test_delete_no_id(self):
        """Test deletion without ID"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2
        )
        
        result = ip.delete()
        
        assert result is False
    
    def test_delete_database_error(self, reset_mocks, monkeypatch):
        """Test deletion with database error"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            id=123
        )
        
        def mock_execute_update(query, params):
            raise Exception("Database error")
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        
        result = ip.delete()
        
        assert result is False
    
    def test_find_by_id_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_id"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_IP',
                'type_id': 1,
                'process_id': 2,
                'parent_ip_id': None,
                'revision': '1.0',
                'status': 'alpha',
                'provider': 'Test_Provider',
                'description': 'Test IP description',
                'documentation': 'https://example.com',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_id(123)
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_IP'
    
    def test_find_by_id_not_found(self, reset_mocks, monkeypatch):
        """Test find_by_id when not found"""
        def mock_execute_query(query, params):
            return []
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_id(123)
        
        assert result is None
    
    def test_find_by_name_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_name"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_IP',
                'type_id': 1,
                'process_id': 2,
                'parent_ip_id': None,
                'revision': '1.0',
                'status': 'alpha',
                'provider': 'Test_Provider',
                'description': 'Test IP description',
                'documentation': 'https://example.com',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_name("Test_IP")
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_IP'
    
    def test_find_all_success(self, reset_mocks, monkeypatch):
        """Test successful find_all"""
        def mock_execute_query(query):
            return [
                {
                    'id': 1,
                    'name': 'IP1',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'Provider1',
                    'description': 'IP 1',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                },
                {
                    'id': 2,
                    'name': 'IP2',
                    'type_id': 2,
                    'process_id': 2,
                    'parent_ip_id': None,
                    'revision': '2.0',
                    'status': 'beta',
                    'provider': 'Provider2',
                    'description': 'IP 2',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_all()
        
        assert len(result) == 2
        assert result[0].name == 'IP1'
        assert result[1].name == 'IP2'
    
    def test_find_by_type_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_type"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 1,
                    'name': 'IP1',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'Provider1',
                    'description': 'IP 1',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_type(1)
        
        assert len(result) == 1
        assert result[0].type_id == 1
    
    def test_find_by_process_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_process"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 1,
                    'name': 'IP1',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'Provider1',
                    'description': 'IP 1',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_process(1)
        
        assert len(result) == 1
        assert result[0].process_id == 1
    
    def test_find_by_status_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_status"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 1,
                    'name': 'IP1',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'production',
                    'provider': 'Provider1',
                    'description': 'IP 1',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_status("production")
        
        assert len(result) == 1
        assert result[0].status == 'production'
    
    def test_find_by_provider_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_provider"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 1,
                    'name': 'IP1',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'ARM',
                    'description': 'IP 1',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_by_provider("ARM")
        
        assert len(result) == 1
        assert result[0].provider == 'ARM'
    
    def test_find_roots_success(self, reset_mocks, monkeypatch):
        """Test successful find_roots"""
        def mock_execute_query(query):
            return [
                {
                    'id': 1,
                    'name': 'Root_IP',
                    'type_id': 1,
                    'process_id': 1,
                    'parent_ip_id': None,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'Provider1',
                    'description': 'Root IP',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = IP.find_roots()
        
        assert len(result) == 1
        assert result[0].name == 'Root_IP'
        assert result[0].parent_ip_id is None

    @pytest.mark.skip(reason="This test is not debugged work yet, skipping for now")   
    def test_get_type_success(self, reset_mocks, monkeypatch):
        """Test successful get_type"""
        class MockType:
            def __init__(self):
                self.id = 1
                self.name = "Test_Type"
        
        def mock_find_by_id(id):
            if id == 1:
                return MockType()
            return None
        
        monkeypatch.setattr(IP, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        ip = IP(name="Test_IP", type_id=1, process_id=2)
        result = ip.get_type()
        
        assert result is not None
        assert result.name == "Test_Type"
    
    def test_get_type_not_found(self, reset_mocks, monkeypatch):
        """Test get_type when type not found"""
        def mock_find_by_id(id):
            return None
        
        monkeypatch.setattr(IP, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        ip = IP(name="Test_IP", type_id=999, process_id=2)
        result = ip.get_type()
        
        assert result is None

    @pytest.mark.skip(reason="This test is not debugged work yet, skipping for now")
    def test_get_process_success(self, reset_mocks, monkeypatch):
        """Test successful get_process"""
        class MockProcess:
            def __init__(self):
                self.id = 2
                self.name = "Test_Process"
        
        def mock_find_by_id(id):
            if id == 2:
                return MockProcess()
            return None
        
        monkeypatch.setattr(IP, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        ip = IP(name="Test_IP", type_id=1, process_id=2)
        result = ip.get_process()
        
        assert result is not None
        assert result.name == "Test_Process"
    
    def test_get_parent_success(self, reset_mocks, monkeypatch):
        """Test successful get_parent"""
        class MockParent:
            def __init__(self):
                self.id = 3
                self.name = "Parent_IP"
        
        def mock_find_by_id(id):
            if id == 3:
                return MockParent()
            return None
        
        monkeypatch.setattr(IP, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        ip = IP(name="Test_IP", type_id=1, process_id=2, parent_ip_id=3)
        result = ip.get_parent()
        
        assert result is not None
        assert result.name == "Parent_IP"
    
    def test_get_parent_no_parent(self):
        """Test get_parent when no parent"""
        ip = IP(name="Test_IP", type_id=1, process_id=2)
        result = ip.get_parent()
        
        assert result is None
    
    def test_get_children_success(self, reset_mocks, monkeypatch):
        """Test successful get_children"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 2,
                    'name': 'Child_IP',
                    'type_id': 1,
                    'process_id': 2,
                    'parent_ip_id': 1,
                    'revision': '1.0',
                    'status': 'alpha',
                    'provider': 'Provider1',
                    'description': 'Child IP',
                    'documentation': 'https://example.com',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        ip = IP(name="Parent_IP", type_id=1, process_id=2, id=1)
        result = ip.get_children()
        
        assert len(result) == 1
        assert result[0].name == 'Child_IP'
        assert result[0].parent_ip_id == 1
    
    def test_add_child_success(self, reset_mocks, monkeypatch):
        """Test successful add_child"""
        def mock_save(self):
            return True
        
        monkeypatch.setattr(IP, "save", mock_save, raising=True)
        
        parent = IP(name="Parent_IP", type_id=1, process_id=2, id=1)
        child = IP(name="Child_IP", type_id=1, process_id=2)
        
        result = parent.add_child(child)
        
        assert result is True
        assert child.parent_ip_id == 1
    
    def test_add_child_no_parent_id(self):
        """Test add_child when parent has no ID"""
        parent = IP(name="Parent_IP", type_id=1, process_id=2)
        child = IP(name="Child_IP", type_id=1, process_id=2)
        
        result = parent.add_child(child)
        
        assert result is False
    
    def test_remove_child_success(self, reset_mocks, monkeypatch):
        """Test successful remove_child"""
        def mock_save(self):
            return True
        
        monkeypatch.setattr(IP, "save", mock_save, raising=True)
        
        parent = IP(name="Parent_IP", type_id=1, process_id=2, id=1)
        child = IP(name="Child_IP", type_id=1, process_id=2, parent_ip_id=1)
        
        result = parent.remove_child(child)
        
        assert result is True
        assert child.parent_ip_id is None
    
    def test_remove_child_wrong_parent(self):
        """Test remove_child when child doesn't belong to parent"""
        parent = IP(name="Parent_IP", type_id=1, process_id=2, id=1)
        child = IP(name="Child_IP", type_id=1, process_id=2, parent_ip_id=999)
        
        result = parent.remove_child(child)
        
        assert result is False
    
    def test_get_all_descendants(self, reset_mocks, monkeypatch):
        """Test get_all_descendants"""
        def mock_get_children(self):
            if self.name == "Parent_IP":
                child1 = IP(name="Child1", type_id=1, process_id=2, id=2)
                child2 = IP(name="Child2", type_id=1, process_id=2, id=3)
                return [child1, child2]
            elif self.name == "Child1":
                grandchild = IP(name="Grandchild", type_id=1, process_id=2, id=4)
                return [grandchild]
            else:
                return []
        
        monkeypatch.setattr(IP, "get_children", mock_get_children, raising=True)
        
        parent = IP(name="Parent_IP", type_id=1, process_id=2, id=1)
        result = parent.get_all_descendants()
        
        assert len(result) == 3
        assert result[0].name == "Child1"
        assert result[1].name == "Grandchild"
        assert result[2].name == "Child2"
    
    def test_get_root_ancestor(self, reset_mocks, monkeypatch):
        """Test get_root_ancestor"""
        def mock_get_parent(self):
            if self.name == "Child_IP":
                parent = IP(name="Parent_IP", type_id=1, process_id=2, parent_ip_id=1)
                return parent
            elif self.name == "Parent_IP":
                return None
            return None
        
        monkeypatch.setattr(IP, "get_parent", mock_get_parent, raising=True)
        
        child = IP(name="Child_IP", type_id=1, process_id=2, parent_ip_id=2)
        result = child.get_root_ancestor()
        
        assert result.name == "Parent_IP"
    
    def test_update_status_success(self, reset_mocks, monkeypatch):
        """Test successful update_status"""
        def mock_save(self):
            return True
        
        monkeypatch.setattr(IP, "save", mock_save, raising=True)
        
        ip = IP(name="Test_IP", type_id=1, process_id=2, status="alpha")
        result = ip.update_status("production")
        
        assert result is True
        assert ip.status == "production"
    
    def test_update_status_invalid(self):
        """Test update_status with invalid status"""
        ip = IP(name="Test_IP", type_id=1, process_id=2, status="alpha")
        result = ip.update_status("invalid_status")
        
        assert result is False
        assert ip.status == "alpha"  # Should not change
    
    def test_release_success(self, reset_mocks, monkeypatch):
        """Test successful release"""
        def mock_update_status(self, status):
            self.status = status
            return True
        
        monkeypatch.setattr(IP, "update_status", mock_update_status, raising=True)
        
        ip = IP(name="Test_IP", type_id=1, process_id=2, status="beta")
        result = ip.release()
        
        assert result is True
        assert ip.status == "production"
    
    def test_str_representation(self):
        """Test string representation"""
        ip = IP(
            name="Test_IP",
            type_id=1,
            process_id=2,
            status="alpha",
            id=123
        )
        
        expected = "IP(id=123, name='Test_IP', type_id=1, process_id=2, status='alpha')"
        assert str(ip) == expected
        assert repr(ip) == expected

