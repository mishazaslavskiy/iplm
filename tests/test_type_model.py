#!/usr/bin/env python3
"""
Tests for type_model.py - Type model
"""
import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from src.type_model import Type
from src.database import db_manager


@pytest.fixture
def reset_mocks(monkeypatch):
    """Reset database mocks for each test"""
    monkeypatch.setattr(db_manager, "execute_query", lambda q, p=None: [], raising=True)
    monkeypatch.setattr(db_manager, "execute_update", lambda q, p=None: 1, raising=True)
    return monkeypatch


class TestType:
    """Test Type model functionality"""
    
    def test_type_creation(self):
        """Test Type object creation"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description"
        )
        
        assert type_obj.name == "Test_Type"
        assert type_obj.parent_id is None
        assert type_obj.description == "Test type description"
        assert type_obj.id is None
        assert type_obj.path == ""
        assert type_obj.level == 0
        assert type_obj.created_at is None
        assert type_obj.updated_at is None
    
    def test_type_creation_with_parent(self):
        """Test Type creation with parent"""
        type_obj = Type(
            name="Child_Type",
            parent_id=1,
            description="Child type description"
        )
        
        assert type_obj.name == "Child_Type"
        assert type_obj.parent_id == 1
        assert type_obj.description == "Child type description"
    
    def test_type_creation_with_kwargs(self):
        """Test Type creation with additional kwargs"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description",
            id=1,
            path="Test_Type",
            level=0,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        assert type_obj.id == 1
        assert type_obj.path == "Test_Type"
        assert type_obj.level == 0
        assert type_obj.created_at == "2023-01-01 00:00:00"
        assert type_obj.updated_at == "2023-01-01 00:00:00"
    
    def test_to_dict(self):
        """Test Type to_dict method"""
        type_obj = Type(
            name="Test_Type",
            parent_id=1,
            description="Test type description",
            id=1,
            path="Parent/Test_Type",
            level=1,
            created_at="2023-01-01 00:00:00",
            updated_at="2023-01-01 00:00:00"
        )
        
        result = type_obj.to_dict()
        expected = {
            'id': 1,
            'name': 'Test_Type',
            'parent_id': 1,
            'path': 'Parent/Test_Type',
            'level': 1,
            'description': 'Test type description',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        assert result == expected
    
    def test_from_dict(self):
        """Test Type from_dict method"""
        data = {
            'id': 1,
            'name': 'Test_Type',
            'parent_id': 1,
            'path': 'Parent/Test_Type',
            'level': 1,
            'description': 'Test type description',
            'created_at': '2023-01-01 00:00:00',
            'updated_at': '2023-01-01 00:00:00'
        }
        
        type_obj = Type.from_dict(data)
        
        assert type_obj.id == 1
        assert type_obj.name == 'Test_Type'
        assert type_obj.parent_id == 1
        assert type_obj.path == 'Parent/Test_Type'
        assert type_obj.level == 1
        assert type_obj.description == 'Test type description'
        assert type_obj.created_at == '2023-01-01 00:00:00'
        assert type_obj.updated_at == '2023-01-01 00:00:00'
    
    def test_from_dict_with_missing_fields(self):
        """Test Type from_dict with missing optional fields"""
        data = {
            'id': 1,
            'name': 'Test_Type',
            'parent_id': 1
        }
        
        type_obj = Type.from_dict(data)
        
        assert type_obj.id == 1
        assert type_obj.name == 'Test_Type'
        assert type_obj.parent_id == 1
        assert type_obj.path == ''  # Default value
        assert type_obj.level == 0  # Default value
        assert type_obj.description == ''  # Default value
        assert type_obj.created_at is None
        assert type_obj.updated_at is None
    
    def test_update_path_and_level_no_parent(self):
        """Test _update_path_and_level with no parent"""
        type_obj = Type(name="Root_Type")
        type_obj._update_path_and_level()
        
        assert type_obj.path == "Root_Type"
        assert type_obj.level == 0
    
    def test_update_path_and_level_with_parent(self, reset_mocks, monkeypatch):
        """Test _update_path_and_level with parent"""
        def mock_find_by_id(id):
            if id == 1:
                parent = Type(name="Parent_Type")
                parent.path = "Parent_Type"
                parent.level = 0
                return parent
            return None
        
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        type_obj = Type(name="Child_Type", parent_id=1)
        type_obj._update_path_and_level()
        
        assert type_obj.path == "Parent_Type/Child_Type"
        assert type_obj.level == 1
    
    def test_update_path_and_level_parent_not_found(self, reset_mocks, monkeypatch):
        """Test _update_path_and_level when parent not found"""
        def mock_find_by_id(id):
            return None
        
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        type_obj = Type(name="Child_Type", parent_id=999)
        type_obj._update_path_and_level()
        
        assert type_obj.path == "Child_Type"
        assert type_obj.level == 0
    
    def test_parent_changed_no_id(self):
        """Test _parent_changed with no ID"""
        type_obj = Type(name="Test_Type")
        result = type_obj._parent_changed()
        
        assert result is False
    
    def test_parent_changed_with_id(self, reset_mocks, monkeypatch):
        """Test _parent_changed with ID"""
        def mock_find_by_id(id):
            if id == 1:
                current = Type(name="Test_Type", parent_id=2)
                return current
            return None
        
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        type_obj = Type(name="Test_Type", parent_id=1, id=1)
        result = type_obj._parent_changed()
        
        assert result is True
    
    def test_save_new_type(self, reset_mocks, monkeypatch):
        """Test saving a new type"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description"
        )
        
        def mock_execute_update(query, params):
            return 1
        
        def mock_execute_query(query, params=None):
            if "LAST_INSERT_ID" in query:
                return [{'id': 123}]
            return []
        
        def mock_find_by_id(id):
            return None
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        result = type_obj.save()
        
        assert result is True
        assert type_obj.id == 123
    
    def test_save_existing_type(self, reset_mocks, monkeypatch):
        """Test saving an existing type"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description",
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        def mock_find_by_id(id):
            if id == 123:
                current = Type(name="Test_Type", parent_id=None, id=123)
                return current
            return None
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        result = type_obj.save()
        
        assert result is True
    
    def test_save_database_error(self, reset_mocks, monkeypatch):
        """Test save method with database error"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description"
        )
        
        def mock_execute_update(query, params):
            raise Exception("Database error")
        
        def mock_find_by_id(id):
            return None
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(Type, "find_by_id", staticmethod(mock_find_by_id), raising=True)
        
        result = type_obj.save()
        
        assert result is False
    
    def test_delete_success(self, reset_mocks, monkeypatch):
        """Test successful deletion"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description",
            id=123
        )
        
        def mock_execute_update(query, params):
            return 1
        
        def mock_find_children(self):
            return []
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(Type, "find_children", mock_find_children, raising=True)
        
        result = type_obj.delete()
        
        assert result is True
    
    def test_delete_no_id(self):
        """Test deletion without ID"""
        type_obj = Type(
            name="Test_Type",
            parent_id=None,
            description="Test type description"
        )
        
        result = type_obj.delete()
        
        assert result is False
    
    def test_delete_with_children(self, reset_mocks, monkeypatch):
        """Test deletion with children"""
        type_obj = Type(
            name="Parent_Type",
            parent_id=None,
            description="Parent type description",
            id=123
        )
        
        child = Type(name="Child_Type", parent_id=123, id=456)
        
        def mock_execute_update(query, params):
            return 1
        
        def mock_find_children(self):
            return [child]
        
        def mock_save(self):
            return True
        
        monkeypatch.setattr(db_manager, "execute_update", mock_execute_update, raising=True)
        monkeypatch.setattr(Type, "find_children", mock_find_children, raising=True)
        monkeypatch.setattr(Type, "save", mock_save, raising=True)
        
        result = type_obj.delete()
        
        assert result is True
        assert child.parent_id is None  # Should be moved to parent's parent
    
    def test_find_by_id_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_id"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_Type',
                'parent_id': None,
                'path': 'Test_Type',
                'level': 0,
                'description': 'Test type description',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Type.find_by_id(123)
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_Type'
    
    def test_find_by_id_not_found(self, reset_mocks, monkeypatch):
        """Test find_by_id when not found"""
        def mock_execute_query(query, params):
            return []
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Type.find_by_id(123)
        
        assert result is None
    
    def test_find_by_name_success(self, reset_mocks, monkeypatch):
        """Test successful find_by_name"""
        def mock_execute_query(query, params):
            return [{
                'id': 123,
                'name': 'Test_Type',
                'parent_id': None,
                'path': 'Test_Type',
                'level': 0,
                'description': 'Test type description',
                'created_at': '2023-01-01 00:00:00',
                'updated_at': '2023-01-01 00:00:00'
            }]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Type.find_by_name("Test_Type")
        
        assert result is not None
        assert result.id == 123
        assert result.name == 'Test_Type'
    
    def test_find_all_success(self, reset_mocks, monkeypatch):
        """Test successful find_all"""
        def mock_execute_query(query):
            return [
                {
                    'id': 1,
                    'name': 'Type1',
                    'parent_id': None,
                    'path': 'Type1',
                    'level': 0,
                    'description': 'Type 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                },
                {
                    'id': 2,
                    'name': 'Type2',
                    'parent_id': 1,
                    'path': 'Type1/Type2',
                    'level': 1,
                    'description': 'Type 2',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Type.find_all()
        
        assert len(result) == 2
        assert result[0].name == 'Type1'
        assert result[1].name == 'Type2'
    
    def test_find_roots_success(self, reset_mocks, monkeypatch):
        """Test successful find_roots"""
        def mock_execute_query(query):
            return [
                {
                    'id': 1,
                    'name': 'Root1',
                    'parent_id': None,
                    'path': 'Root1',
                    'level': 0,
                    'description': 'Root 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        result = Type.find_roots()
        assert len(result) == 1
        assert result[0].name == 'Root1'
        assert result[0].parent_id is None
    
    def test_find_children_success(self, reset_mocks, monkeypatch):
        """Test successful find_children"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 2,
                    'name': 'Child1',
                    'parent_id': 1,
                    'path': 'Parent/Child1',
                    'level': 1,
                    'description': 'Child 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        type_obj = Type(name="Parent", id=1)
        result = type_obj.find_children()
        
        assert len(result) == 1
        assert result[0].name == 'Child1'
        assert result[0].parent_id == 1
    
    def test_find_children_no_id(self):
        """Test find_children with no ID"""
        type_obj = Type(name="Parent")
        result = type_obj.find_children()
        
        assert result == []
    
    def test_find_descendants_success(self, reset_mocks, monkeypatch):
        """Test successful find_descendants"""
        def mock_execute_query(query, params):
            return [
                {
                    'id': 2,
                    'name': 'Child1',
                    'parent_id': 1,
                    'path': 'Parent/Child1',
                    'level': 1,
                    'description': 'Child 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                },
                {
                    'id': 3,
                    'name': 'Grandchild1',
                    'parent_id': 2,
                    'path': 'Parent/Child1/Grandchild1',
                    'level': 2,
                    'description': 'Grandchild 1',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }
            ]
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        type_obj = Type(name="Parent", path="Parent", id=1)
        result = type_obj.find_descendants()
        
        assert len(result) == 2
        assert result[0].name == 'Child1'
        assert result[1].name == 'Grandchild1'
    
    def test_find_descendants_no_id(self):
        """Test find_descendants with no ID"""
        type_obj = Type(name="Parent")
        result = type_obj.find_descendants()
        
        assert result == []
    
    def test_find_ancestors_success(self, reset_mocks, monkeypatch):
        """Test successful find_ancestors"""
        def mock_execute_query(query, params):
            if params and params[0] == "Parent":
                return [{
                    'id': 1,
                    'name': 'Parent',
                    'parent_id': None,
                    'path': 'Parent',
                    'level': 0,
                    'description': 'Parent',
                    'created_at': '2023-01-01 00:00:00',
                    'updated_at': '2023-01-01 00:00:00'
                }]
            return []
        
        monkeypatch.setattr(db_manager, "execute_query", mock_execute_query, raising=True)
        
        type_obj = Type(name="Child", path="Parent/Child", id=2)
        result = type_obj.find_ancestors()
        
        assert len(result) == 1
        assert result[0].name == 'Parent'
    
    def test_find_ancestors_no_path(self):
        """Test find_ancestors with no path"""
        type_obj = Type(name="Root")
        result = type_obj.find_ancestors()
        
        assert result == []
    
    def test_is_ancestor_of_true(self):
        """Test is_ancestor_of returns True"""
        parent = Type(name="Parent", path="Parent")
        child = Type(name="Child", path="Parent/Child")
        
        result = parent.is_ancestor_of(child)
        
        assert result is True
    
    def test_is_ancestor_of_false(self):
        """Test is_ancestor_of returns False"""
        parent = Type(name="Parent", path="Parent")
        child = Type(name="Child", path="Other/Child")
        
        result = parent.is_ancestor_of(child)
        
        assert result is False
    
    def test_is_descendant_of_true(self):
        """Test is_descendant_of returns True"""
        parent = Type(name="Parent", path="Parent")
        child = Type(name="Child", path="Parent/Child")
        
        result = child.is_descendant_of(parent)
        
        assert result is True
    
    def test_is_descendant_of_false(self):
        """Test is_descendant_of returns False"""
        parent = Type(name="Parent", path="Parent")
        child = Type(name="Child", path="Other/Child")
        
        result = child.is_descendant_of(parent)
        
        assert result is False
    
    def test_str_representation(self):
        """Test string representation"""
        type_obj = Type(
            name="Test_Type",
            parent_id=1,
            path="Parent/Test_Type",
            level=1,
            id=123
        )
        
        expected = "Type(id=123, name='Test_Type', path='Parent/Test_Type', level=1)"
        assert str(type_obj) == expected
        assert repr(type_obj) == expected

