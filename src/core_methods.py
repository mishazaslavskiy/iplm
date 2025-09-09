"""
Core methods for IPLM: Release, Find, Update, Change schema
"""
from typing import Dict, Any, Optional, List, Union
import logging
from datetime import datetime
from .models import Process
from .ip_model import IP
from .type_model import Type
from .database import db_manager

logger = logging.getLogger(__name__)

class IPManager:
    """Main IP management class with core methods"""
    
    def __init__(self):
        self.db_manager = db_manager
    
    def release(self, ip_name: str) -> bool:
        """
        Release an IP (change status to production)
        
        Args:
            ip_name: Name of the IP to release
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            ip = IP.find_by_name(ip_name)
            if not ip:
                logger.error(f"IP '{ip_name}' not found")
                return False
            
            success = ip.release()
            if success:
                logger.info(f"IP '{ip_name}' released successfully")
            else:
                logger.error(f"Failed to release IP '{ip_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error releasing IP '{ip_name}': {e}")
            return False
    
    def find(self, **criteria) -> List[IP]:
        """
        Find IPs based on various criteria
        
        Args:
            **criteria: Search criteria including:
                - name: IP name (exact match)
                - type_name: Type name (exact match)
                - type_id: Type ID
                - process_name: Process name (exact match)
                - process_id: Process ID
                - status: IP status
                - provider: Provider name
                - fab: FAB name
                - node: Node name
                - flavor: Flavor name
                
        Returns:
            List[IP]: List of matching IPs
        """
        try:
            query_parts = ["SELECT i.* FROM ips i"]
            joins = []
            where_conditions = []
            params = []
            
            # Add joins and conditions based on criteria
            if 'type_name' in criteria or 'type_id' in criteria:
                joins.append("JOIN types t ON i.type_id = t.id")
                if 'type_name' in criteria:
                    where_conditions.append("t.name = %s")
                    params.append(criteria['type_name'])
                if 'type_id' in criteria:
                    where_conditions.append("i.type_id = %s")
                    params.append(criteria['type_id'])
            
            if 'process_name' in criteria or 'process_id' in criteria or 'fab' in criteria or 'node' in criteria:
                joins.append("JOIN processes p ON i.process_id = p.id")
                if 'process_name' in criteria:
                    where_conditions.append("p.name = %s")
                    params.append(criteria['process_name'])
                if 'process_id' in criteria:
                    where_conditions.append("i.process_id = %s")
                    params.append(criteria['process_id'])
                if 'fab' in criteria:
                    where_conditions.append("p.fab = %s")
                    params.append(criteria['fab'])
                if 'node' in criteria:
                    where_conditions.append("p.node = %s")
                    params.append(criteria['node'])
            
            # Direct IP criteria
            if 'name' in criteria:
                where_conditions.append("i.name = %s")
                params.append(criteria['name'])
            if 'status' in criteria:
                where_conditions.append("i.status = %s")
                params.append(criteria['status'])
            if 'provider' in criteria:
                where_conditions.append("i.provider = %s")
                params.append(criteria['provider'])
            if 'flavor' in criteria:
                where_conditions.append("i.flavor = %s")
                params.append(criteria['flavor'])
            
            # Build final query
            if joins:
                query_parts.extend(joins)
            
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            query_parts.append("ORDER BY i.name")
            
            query = " ".join(query_parts)
            result = self.db_manager.execute_query(query, tuple(params))
            
            return [IP.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs with criteria {criteria}: {e}")
            return []
    
    def find_by_type_tree(self, type_name: str, include_descendants: bool = True) -> List[IP]:
        """
        Find IPs by type, optionally including descendants
        
        Args:
            type_name: Name of the type to search for
            include_descendants: Whether to include IPs from descendant types
            
        Returns:
            List[IP]: List of matching IPs
        """
        try:
            type_obj = Type.find_by_name(type_name)
            if not type_obj:
                logger.error(f"Type '{type_name}' not found")
                return []
            
            if include_descendants:
                # Find all descendant types
                descendants = type_obj.find_descendants()
                type_ids = [type_obj.id] + [d.id for d in descendants]
                
                # Build query with IN clause
                placeholders = ','.join(['%s'] * len(type_ids))
                query = f"SELECT * FROM ips WHERE type_id IN ({placeholders}) ORDER BY name"
                result = self.db_manager.execute_query(query, tuple(type_ids))
            else:
                # Find only direct type
                query = "SELECT * FROM ips WHERE type_id = %s ORDER BY name"
                result = self.db_manager.execute_query(query, (type_obj.id,))
            
            return [IP.from_dict(row) for row in result]
        except Exception as e:
            logger.error(f"Error finding IPs by type tree '{type_name}': {e}")
            return []
    
    def update(self, ip_name: str, **updates) -> bool:
        """
        Update an IP with new values
        
        Args:
            ip_name: Name of the IP to update
            **updates: Fields to update (name, type_id, process_id, flavor, 
                      revision, status, provider, description, documentation)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            ip = IP.find_by_name(ip_name)
            if not ip:
                logger.error(f"IP '{ip_name}' not found")
                return False
            
            # Update allowed fields
            allowed_fields = ['name', 'type_id', 'process_id', 'flavor', 'revision', 
                            'status', 'provider', 'description', 'documentation']
            
            for field, value in updates.items():
                if field in allowed_fields and hasattr(ip, field):
                    setattr(ip, field, value)
                else:
                    logger.warning(f"Field '{field}' is not allowed or doesn't exist")
            
            success = ip.save()
            if success:
                logger.info(f"IP '{ip_name}' updated successfully")
            else:
                logger.error(f"Failed to update IP '{ip_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error updating IP '{ip_name}': {e}")
            return False
    
    def update_ip_components(self, ip_name: str, components: List[Dict[str, Any]]) -> bool:
        """
        Update IP components
        
        Args:
            ip_name: Name of the IP to update
            components: List of component dictionaries
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            ip = IP.find_by_name(ip_name)
            if not ip:
                logger.error(f"IP '{ip_name}' not found")
                return False
            
            ip.ip_components = components
            success = ip.save()
            
            if success:
                logger.info(f"IP components for '{ip_name}' updated successfully")
            else:
                logger.error(f"Failed to update IP components for '{ip_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error updating IP components for '{ip_name}': {e}")
            return False
    
    def change_schema(self, schema_name: str, new_schema: Dict[str, Any]) -> bool:
        """
        Change database schema (add/modify tables or columns)
        
        Args:
            schema_name: Name of the schema to change
            new_schema: New schema definition
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # This is a simplified implementation
            # In a real scenario, you'd want more sophisticated schema migration
            logger.info(f"Schema change requested for '{schema_name}'")
            logger.warning("Schema change functionality is simplified - implement proper migration logic")
            
            # For now, just recreate tables with new schema
            if schema_name in ['processes', 'ips', 'types']:
                # Drop and recreate table (data loss warning!)
                logger.warning("This will recreate the table and may cause data loss!")
                return self._recreate_table(schema_name, new_schema)
            else:
                logger.error(f"Unknown schema '{schema_name}'")
                return False
        except Exception as e:
            logger.error(f"Error changing schema '{schema_name}': {e}")
            return False
    
    def _recreate_table(self, table_name: str, schema: Dict[str, Any]) -> bool:
        """Recreate a table with new schema (simplified implementation)"""
        try:
            # Drop table
            drop_query = f"DROP TABLE IF EXISTS {table_name}"
            self.db_manager.execute_update(drop_query)
            
            # Create table with new schema
            self.db_manager._create_table(table_name, schema)
            
            logger.info(f"Table '{table_name}' recreated successfully")
            return True
        except Exception as e:
            logger.error(f"Error recreating table '{table_name}': {e}")
            return False
    
    def pack(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pack IPs into a structured format for export/transfer
        
        Args:
            criteria: Search criteria for IPs to pack
            
        Returns:
            Dict containing packed IP data
        """
        try:
            ips = self.find(**criteria)
            
            packed_data = {
                'metadata': {
                    'total_ips': len(ips),
                    'criteria': criteria,
                    'packed_at': str(datetime.now())
                },
                'ips': []
            }
            
            for ip in ips:
                ip_data = ip.to_dict()
                # Add related data
                ip_data['type'] = ip.get_type().to_dict() if ip.get_type() else None
                ip_data['process'] = ip.get_process().to_dict() if ip.get_process() else None
                packed_data['ips'].append(ip_data)
            
            logger.info(f"Packed {len(ips)} IPs successfully")
            return packed_data
        except Exception as e:
            logger.error(f"Error packing IPs: {e}")
            return {'error': str(e)}
    
    def fetch(self, ip_name: str) -> Optional[IP]:
        """
        Fetch a specific IP by name (alias for find_by_name)
        
        Args:
            ip_name: Name of the IP to fetch
            
        Returns:
            IP object or None if not found
        """
        return IP.find_by_name(ip_name)

# Global IP manager instance
ip_manager = IPManager()
