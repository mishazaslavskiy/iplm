"""
IP model for IP management
"""
from typing import Dict, Any, Optional, List
import json
import logging
from .database import db_manager
from .models import Process
from .type_model import Type
from config.settings import IP_STATUSES, DEFAULT_REVISION, DEFAULT_STATUS

logger = logging.getLogger(__name__)

class IP:
    """IP model for IP management"""
    
    def __init__(self, name: str, type_id: int, process_id: int, revision: str = DEFAULT_REVISION,
                 status: str = DEFAULT_STATUS, provider: str = "", flavor: str = "",
                 ip_components: List[Dict[str, Any]] = None, description: str = "",
                 documentation: str = "", **kwargs):
        self.id = kwargs.get('id')
        self.name = name
        self.type_id = type_id
        self.process_id = process_id
        self.flavor = flavor
        self.revision = revision
        self.status = status
        self.provider = provider
        self.ip_components = ip_components or []
        self.description = description
        self.documentation = documentation
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at')
        
        # Validate status
        if self.status not in IP_STATUSES:
            raise ValueError(f"Invalid status '{self.status}'. Must be one of: {IP_STATUSES}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert IP instance to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type_id': self.type_id,
            'process_id': self.process_id,
            'flavor': self.flavor,
            'revision': self.revision,
            'status': self.status,
            'provider': self.provider,
            'ip_components': json.dumps(self.ip_components) if self.ip_components else None,
            'description': self.description,
            'documentation': self.documentation,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IP':
        """Create IP instance from dictionary"""
        ip_components = []
        if data.get('ip_components'):
            try:
                ip_components = json.loads(data['ip_components'])
            except (json.JSONDecodeError, TypeError):
                ip_components = []
        
        return cls(
            id=data.get('id'),
            name=data['name'],
            type_id=data['type_id'],
            process_id=data['process_id'],
            flavor=data.get('flavor', ''),
            revision=data.get('revision', DEFAULT_REVISION),
            status=data.get('status', DEFAULT_STATUS),
            provider=data.get('provider', ''),
            ip_components=ip_components,
            description=data.get('description', ''),
            documentation=data.get('documentation', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def save(self) -> bool:
        """Save IP to database"""
        try:
            if self.id:
                # Update existing IP
                query = """
                UPDATE ips 
                SET name = %s, type_id = %s, process_id = %s, flavor = %s, revision = %s,
                    status = %s, provider = %s, ip_components = %s, description = %s,
                    documentation = %s, updated_at = NOW()
                WHERE id = %s
                """
                params = (self.name, self.type_id, self.process_id, self.flavor, self.revision,
                         self.status, self.provider, json.dumps(self.ip_components) if self.ip_components else None,
                         self.description, self.documentation, self.id)
                db_manager.execute_update(query, params)
            else:
                # Insert new IP
                query = """
                INSERT INTO ips (name, type_id, process_id, flavor, revision, status, provider, 
                               ip_components, description, documentation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (self.name, self.type_id, self.process_id, self.flavor, self.revision,
                         self.status, self.provider, json.dumps(self.ip_components) if self.ip_components else None,
                         self.description, self.documentation)
                db_manager.execute_update(query, params)
                # Get the inserted ID
                result = db_manager.execute_query("SELECT LAST_INSERT_ID() as id")
                self.id = result[0]['id']
            
            logger.info(f"IP {self.name} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving IP {self.name}: {e}")
            return False
    
    def delete(self) -> bool:
        """Delete IP from database"""
        if not self.id:
            return False
        
        try:
            query = "DELETE FROM ips WHERE id = %s"
            db_manager.execute_update(query, (self.id,))
            logger.info(f"IP {self.name} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting IP {self.name}: {e}")
            return False
    
    @classmethod
    def find_by_id(cls, id: int) -> Optional['IP']:
        """Find IP by ID"""
        try:
            query = "SELECT * FROM ips WHERE id = %s"
            result = db_manager.execute_query(query, (id,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding IP by ID {id}: {e}")
            return None
    
    @classmethod
    def find_by_name(cls, name: str) -> Optional['IP']:
        """Find IP by name"""
        try:
            query = "SELECT * FROM ips WHERE name = %s"
            result = db_manager.execute_query(query, (name,))
            if result:
                return cls.from_dict(result[0])
            return None
        except Exception as e:
            logger.error(f"Error finding IP by name {name}: {e}")
            return None
    
    @classmethod
    def find_all(cls) -> List['IP']:
        """Find all IPs"""
        try:
            query = "SELECT * FROM ips ORDER BY name"
            result = db_manager.execute_query(query)
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding all IPs: {e}")
            return []
    
    @classmethod
    def find_by_type(cls, type_id: int) -> List['IP']:
        """Find IPs by type ID"""
        try:
            query = "SELECT * FROM ips WHERE type_id = %s ORDER BY name"
            result = db_manager.execute_query(query, (type_id,))
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs by type {type_id}: {e}")
            return []
    
    @classmethod
    def find_by_process(cls, process_id: int) -> List['IP']:
        """Find IPs by process ID"""
        try:
            query = "SELECT * FROM ips WHERE process_id = %s ORDER BY name"
            result = db_manager.execute_query(query, (process_id,))
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs by process {process_id}: {e}")
            return []
    
    @classmethod
    def find_by_status(cls, status: str) -> List['IP']:
        """Find IPs by status"""
        try:
            query = "SELECT * FROM ips WHERE status = %s ORDER BY name"
            result = db_manager.execute_query(query, (status,))
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs by status {status}: {e}")
            return []
    
    @classmethod
    def find_by_provider(cls, provider: str) -> List['IP']:
        """Find IPs by provider"""
        try:
            query = "SELECT * FROM ips WHERE provider = %s ORDER BY name"
            result = db_manager.execute_query(query, (provider,))
            return [cls.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs by provider {provider}: {e}")
            return []
    
    def get_type(self) -> Optional[Type]:
        """Get the type object for this IP"""
        return Type.find_by_id(self.type_id)
    
    def get_process(self) -> Optional[Process]:
        """Get the process object for this IP"""
        return Process.find_by_id(self.process_id)
    
    def add_component(self, component: Dict[str, Any]):
        """Add a component to the IP components list"""
        if not self.ip_components:
            self.ip_components = []
        self.ip_components.append(component)
    
    def remove_component(self, component_name: str) -> bool:
        """Remove a component from the IP components list"""
        if not self.ip_components:
            return False
        
        for i, component in enumerate(self.ip_components):
            if component.get('name') == component_name:
                del self.ip_components[i]
                return True
        return False
    
    def update_status(self, new_status: str) -> bool:
        """Update IP status"""
        if new_status not in IP_STATUSES:
            logger.error(f"Invalid status '{new_status}'. Must be one of: {IP_STATUSES}")
            return False
        
        self.status = new_status
        return self.save()
    
    def release(self) -> bool:
        """Release IP (change status to production)"""
        return self.update_status('production')
    
    def __str__(self):
        return f"IP(id={self.id}, name='{self.name}', type_id={self.type_id}, process_id={self.process_id}, status='{self.status}')"
    
    def __repr__(self):
        return self.__str__()

