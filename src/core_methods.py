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
            **updates: Fields to update (name, type_id, process_id, 
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
            allowed_fields = ['name', 'type_id', 'process_id', 'revision', 
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
    
    def add_child_ip(self, parent_ip_name: str, child_ip: IP) -> bool:
        """
        Add a child IP to a parent IP
        
        Args:
            parent_ip_name: Name of the parent IP
            child_ip: Child IP object to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            parent_ip = IP.find_by_name(parent_ip_name)
            if not parent_ip:
                logger.error(f"Parent IP '{parent_ip_name}' not found")
                return False
            
            success = parent_ip.add_child(child_ip)
            if success:
                logger.info(f"Child IP '{child_ip.name}' added to '{parent_ip_name}' successfully")
            else:
                logger.error(f"Failed to add child IP '{child_ip.name}' to '{parent_ip_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error adding child IP to '{parent_ip_name}': {e}")
            return False
    
    def remove_child_ip(self, parent_ip_name: str, child_ip_name: str) -> bool:
        """
        Remove a child IP from a parent IP
        
        Args:
            parent_ip_name: Name of the parent IP
            child_ip_name: Name of the child IP to remove
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            parent_ip = IP.find_by_name(parent_ip_name)
            child_ip = IP.find_by_name(child_ip_name)
            
            if not parent_ip:
                logger.error(f"Parent IP '{parent_ip_name}' not found")
                return False
            if not child_ip:
                logger.error(f"Child IP '{child_ip_name}' not found")
                return False
            
            success = parent_ip.remove_child(child_ip)
            if success:
                logger.info(f"Child IP '{child_ip_name}' removed from '{parent_ip_name}' successfully")
            else:
                logger.error(f"Failed to remove child IP '{child_ip_name}' from '{parent_ip_name}'")
            
            return success
        except Exception as e:
            logger.error(f"Error removing child IP from '{parent_ip_name}': {e}")
            return False
    
    def get_ip_hierarchy(self, ip_name: str) -> Dict[str, Any]:
        """
        Get the complete hierarchy for an IP
        
        Args:
            ip_name: Name of the IP to get hierarchy for
            
        Returns:
            Dict containing the IP hierarchy
        """
        try:
            ip = IP.find_by_name(ip_name)
            if not ip:
                logger.error(f"IP '{ip_name}' not found")
                return {}
            
            def build_hierarchy(ip_obj):
                hierarchy = {
                    'id': ip_obj.id,
                    'name': ip_obj.name,
                    'type': ip_obj.get_type().name if ip_obj.get_type() else 'Unknown',
                    'status': ip_obj.status,
                    'children': []
                }
                
                children = ip_obj.get_children()
                for child in children:
                    hierarchy['children'].append(build_hierarchy(child))
                
                return hierarchy
            
            return build_hierarchy(ip)
        except Exception as e:
            logger.error(f"Error getting IP hierarchy for '{ip_name}': {e}")
            return {}
    
    def show_ip_tree(self, ip_name: str = None, show_details: bool = False) -> None:
        """
        Display IP tree structure in a formatted way
        
        Args:
            ip_name: Name of the IP to show tree for. If None, shows all root IPs
            show_details: Whether to show additional details (provider, revision, etc.)
        """
        try:
            if ip_name:
                ip = IP.find_by_name(ip_name)
                if not ip:
                    print(f"IP '{ip_name}' not found")
                    return
                print(f"IP Tree for '{ip_name}':")
                print("=" * 50)
                self._print_ip_tree(ip, 0, show_details)
            else:
                root_ips = IP.find_roots()
                if not root_ips:
                    print("No root IPs found")
                    return
                print("All IP Trees:")
                print("=" * 50)
                for ip in root_ips:
                    self._print_ip_tree(ip, 0, show_details)
                    print()  # Add blank line between trees
        except Exception as e:
            logger.error(f"Error showing IP tree: {e}")
            print(f"Error showing IP tree: {e}")
    
    def _print_ip_tree(self, ip: IP, level: int = 0, show_details: bool = False) -> None:
        """
        Internal method to print IP tree structure
        
        Args:
            ip: IP object to print
            level: Current indentation level
            show_details: Whether to show additional details
        """
        indent = "  " * level
        type_obj = ip.get_type()
        type_name = type_obj.name if type_obj else 'Unknown'
        
        if show_details:
            process = ip.get_process()
            process_name = process.name if process else 'Unknown'
            print(f"{indent}├─ {ip.name}")
            print(f"{indent}   Type: {type_name}")
            print(f"{indent}   Status: {ip.status}")
            print(f"{indent}   Provider: {ip.provider}")
            print(f"{indent}   Revision: {ip.revision}")
            print(f"{indent}   Process: {process_name}")
            if ip.description:
                print(f"{indent}   Description: {ip.description}")
        else:
            print(f"{indent}├─ {ip.name} ({type_name}) - {ip.status}")
        
        children = ip.get_children()
        for child in children:
            self._print_ip_tree(child, level + 1, show_details)
    
    def show_ip_tree_by_process(self, process_name: str, show_details: bool = False) -> None:
        """
        Display IP trees for all IPs in a specific process
        
        Args:
            process_name: Name of the process
            show_details: Whether to show additional details
        """
        try:
            process = Process.find_by_name(process_name)
            if not process:
                print(f"Process '{process_name}' not found")
                return
            
            # Get all IPs for this process
            ips = IP.find_by_process(process.id)
            if not ips:
                print(f"No IPs found for process '{process_name}'")
                return
            
            # Find root IPs (IPs without parents) in this process
            root_ips = [ip for ip in ips if ip.parent_ip_id is None]
            
            if not root_ips:
                print(f"No root IPs found for process '{process_name}'")
                return
            
            print(f"IP Trees for Process '{process_name}':")
            print("=" * 50)
            for ip in root_ips:
                self._print_ip_tree(ip, 0, show_details)
                print()  # Add blank line between trees
        except Exception as e:
            logger.error(f"Error showing IP tree by process: {e}")
            print(f"Error showing IP tree by process: {e}")
    
    def show_ip_tree_by_type(self, type_name: str, show_details: bool = False) -> None:
        """
        Display IP trees for all IPs of a specific type
        
        Args:
            type_name: Name of the type
            show_details: Whether to show additional details
        """
        try:
            type_obj = Type.find_by_name(type_name)
            if not type_obj:
                print(f"Type '{type_name}' not found")
                return
            
            # Get all IPs of this type
            ips = IP.find_by_type(type_obj.id)
            if not ips:
                print(f"No IPs found for type '{type_name}'")
                return
            
            # Find root IPs (IPs without parents) of this type
            root_ips = [ip for ip in ips if ip.parent_ip_id is None]
            
            if not root_ips:
                print(f"No root IPs found for type '{type_name}'")
                return
            
            print(f"IP Trees for Type '{type_name}':")
            print("=" * 50)
            for ip in root_ips:
                self._print_ip_tree(ip, 0, show_details)
                print()  # Add blank line between trees
        except Exception as e:
            logger.error(f"Error showing IP tree by type: {e}")
            print(f"Error showing IP tree by type: {e}")
    
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
                ip_data['parent'] = ip.get_parent().to_dict() if ip.get_parent() else None
                ip_data['children'] = [child.to_dict() for child in ip.get_children()]
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
