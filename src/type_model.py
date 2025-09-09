"""
Type model for IP classification tree structure
"""
from typing import Dict, Any, Optional, List
import logging
from .database import db_manager

logger = logging.getLogger(__name__)

class Type:
    """Type model for IP classification tree"""
    
    def __init__(self, name: str, parent_id: Optional[int] = None, description: str = "", **kwargs):
        self.id = kwargs.get('id')
        self.name = name
        self.parent_id = parent_id
        self.path = kwargs.get('path', '')
        self.level = kwargs.get('level', 0)
        self.description = description
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Type instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'parent_id': self.parent_id,
            'path': self.path,
            'level': self.level,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Type':
        """Create Type instance from dictionary"""
        return cls(
            id=data.get('id'),
            name=data['name'],
            parent_id=data.get('parent_id'),
            path=data.get('path', ''),
            level=data.get('level', 0),
            description=data.get('description', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def save(self) -> bool:
        """Save Type to database"""
        try:
            # Update path and level based on parent
            self._update_path_and_level()
            
            if self.id:
                # Update existing type
                query = """
                UPDATE types 
                SET name = %s, parent_id = %s, path = %s, level = %s, description = %s, updated_at = NOW()
                WHERE id = %s
                """
                params = (self.name, self.parent_id, self.path, self.level, self.description, self.id)
                db_manager.execute_update(query, params)
            else:
                # Insert new type
                query = """
                INSERT INTO types (name, parent_id, path, level, description)
                VALUES (%s, %s, %s, %s, %s)
                """
                params = (self.name, self.parent_id, self.path, self.level, self.description)
                db_manager.execute_update(query, params)
                # Get the inserted ID
                result = db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                self.id = result[0]['id']
            
            # Update path for all descendants if this is a new node or parent changed
            if not self.id or self._parent_changed():
                self._update_descendants_paths()
            
            logger.info(f"Type {self.name} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving type {self.name}: {e}")
            return False
    
    def _update_path_and_level(self):
        """Update path and level based on parent"""
        if self.parent_id:
            parent = self.find_by_id(self.parent_id)
            if parent:
                self.path = f"{parent.path}/{self.name}" if parent.path else self.name
                self.level = parent.level + 1
            else:
                self.path = self.name
                self.level = 0
        else:
            self.path = self.name
            self.level = 0
    
    def _parent_changed(self) -> bool:
        """Check if parent has changed (for existing records)"""
        if not self.id:
            return False
        
        current = self.find_by_id(self.id)
        return current and current.parent_id != self.parent_id
    
    def _update_descendants_paths(self):
        """Update paths for all descendants"""
        descendants = self.find_descendants()
        for descendant in descendants:
            descendant._update_path_and_level()
            descendant.save()
    
    def delete(self) -> bool:
        """Delete Type from database (moves children to parent)"""
        if not self.id:
            return False
        
        try:
            # Move children to parent
            children = self.find_children()
            for child in children:
                child.parent_id = self.parent_id
                child.save()
            
            # Delete the type
            query = "DELETE FROM types WHERE id = %s"
            db_manager.execute_update(query, (self.id,))
            logger.info(f"Type {self.name} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting type {self.name}: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, id: int) -> Optional['Type']:
        """Find Type by ID"""
        try:
            query = "SELECT * FROM types WHERE id = %s"
            result = db_manager.execute_query(query, (id,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding type by ID {id}: {e}")
            return None
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Type']:
        """Find Type by name"""
        try:
            query = "SELECT * FROM types WHERE name = %s"
            result = db_manager.execute_query(query, (name,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding type by name {name}: {e}")
            return None
    
    @classmethod
    def find_all(cls) -> List['Type']:
        """Find all Types"""
        try:
            query = "SELECT * FROM types ORDER BY path"
            result = db_manager.execute_query(query)
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all types: {e}")
            return []
    
    @classmethod
    def find_roots(cls) -> List['Type']:
        """Find root types (no parent)"""
        try:
            query = "SELECT * FROM types WHERE parent_id IS NULL ORDER BY name"
            result = db_manager.execute_query(query)
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding root types: {e}")
            return []
    
    def find_children(self) -> List['Type']:
        """Find direct children of this type"""
        if not self.id:
            return []
        
        try:
            query = "SELECT * FROM types WHERE parent_id = %s ORDER BY name"
            result = db_manager.execute_query(query, (self.id,))
            return [Type.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding children of type {self.name}: {e}")
            return []
    
    def find_descendants(self) -> List['Type']:
        """Find all descendants of this type"""
        if not self.id:
            return []
        
        try:
            query = "SELECT * FROM types WHERE path LIKE %s ORDER BY path"
            result = db_manager.execute_query(query, (f"{self.path}/%",))
            return [Type.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding descendants of type {self.name}: {e}")
            return []
    
    def find_ancestors(self) -> List['Type']:
        """Find all ancestors of this type"""
        if not self.path:
            return []
        
        try:
            path_parts = self.path.split('/')
            ancestors = []
            current_path = ""
            
            for part in path_parts[:-1]:  # Exclude self
                current_path = f"{current_path}/{part}" if current_path else part
                query = "SELECT * FROM types WHERE path = %s"
                result = db_manager.execute_query(query, (current_path,))
                if result:
                    ancestors.append(Type.from_dict(result[0]))
            
            return ancestors
        except Exception as e:
            logger.error(f"Error finding ancestors of type {self.name}: {e}")
            return []
    
    def is_ancestor_of(self, other: 'Type') -> bool:
        """Check if this type is an ancestor of another type"""
        if not other.path:
            return False
        return other.path.startswith(f"{self.path}/")
    
    def is_descendant_of(self, other: 'Type') -> bool:
        """Check if this type is a descendant of another type"""
        if not self.path:
            return False
        return self.path.startswith(f"{other.path}/")
    
    def __str__(self):
        return f"Type(id={self.id}, name='{self.name}', path='{self.path}', level={self.level})"
    
    def __repr__(self):
        return self.__str__()

