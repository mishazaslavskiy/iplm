"""
Base model class and core models for IPLM
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .database import db_manager

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """Base model class with common database operations"""
    
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        pass
    
    @abstractmethod
    def save(self) -> bool:
        """Save model to database"""
        pass
    
    @abstractmethod
    def delete(self) -> bool:
        """Delete model from database"""
        pass
    
    @classmethod
    @abstractmethod
    def find_by_id(cls, id: int) -> Optional['BaseModel']:
        """Find model by ID"""
        pass
    
    @classmethod
    @abstractmethod
    def find_all(cls) -> List['BaseModel']:
        """Find all models"""
        pass

class Process(BaseModel):
    """Process model for IP management"""
    
    def __init__(self, name: str, node: str, fab: str, description: str = "", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.node = node
        self.fab = fab
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Process instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'node': self.node,
            'fab': self.fab,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Process':
        """Create Process instance from dictionary"""
        return cls(
            id=data.get('id'),
            name=data['name'],
            node=data['node'],
            fab=data['fab'],
            description=data.get('description', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def save(self) -> bool:
        """Save Process to database"""
        try:
            if self.id:
                # Update existing process
                query = """
                UPDATE processes 
                SET name = %s, node = %s, fab = %s, description = %s, updated_at = NOW()
                WHERE id = %s
                """
                params = (self.name, self.node, self.fab, self.description, self.id)
                db_manager.execute_update(query, params)
            else:
                # Insert new process
                query = """
                INSERT INTO processes (name, node, fab, description)
                VALUES (%s, %s, %s, %s)
                """
                params = (self.name, self.node, self.fab, self.description)
                db_manager.execute_update(query, params)
                # Get the inserted ID
                result = db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                self.id = result[0]['id']
            
            logger.info(f"Process {self.name} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving process {self.name}: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete Process from database"""
        if not self.id:
            return False
        
        try:
            query = "DELETE FROM processes WHERE id = %s"
            db_manager.execute_update(query, (self.id,))
            logger.info(f"Process {self.name} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting process {self.name}: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, id: int) -> Optional['Process']:
        """Find Process by ID"""
        try:
            query = "SELECT * FROM processes WHERE id = %s"
            result = db_manager.execute_query(query, (id,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding process by ID {id}: {e}")
            return None
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['Process']:
        """Find Process by name"""
        try:
            query = "SELECT * FROM processes WHERE name = %s"
            result = db_manager.execute_query(query, (name,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding process by name {name}: {e}")
            return None
    
    @classmethod
    def find_all(cls) -> List['Process']:
        """Find all Processes"""
        try:
            query = "SELECT * FROM processes ORDER BY name"
            result = db_manager.execute_query(query)
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all processes: {e}")
            return []
    
    @classmethod
    def find_by_fab(cls, fab: str) -> List['Process']:
        """Find Processes by FAB"""
        try:
            query = "SELECT * FROM processes WHERE fab = %s ORDER BY name"
            result = db_manager.execute_query(query, (fab,))
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding processes by FAB {fab}: {e}")
            return []
    
    def __str__(self):
        return f"Process(id={self.id}, name='{self.name}', node='{self.node}', fab='{self.fab}')"
    
    def __repr__(self):
        return self.__str__()

