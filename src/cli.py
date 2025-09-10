"""
Command Line Interface for IPLM
"""
import argparse
import sys
import json
from typing import Dict, Any
from .core_methods import ip_manager
from .database import db_manager
from .models import Process
from .ip_model import IP
from .type_model import Type

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="IPLM - IP Management System")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Database commands
    db_parser = subparsers.add_parser('db', help='Database operations')
    db_subparsers = db_parser.add_subparsers(dest='db_action')
    db_subparsers.add_parser('init', help='Initialize database')
    db_subparsers.add_parser('status', help='Check database status')
    
    # Process commands
    process_parser = subparsers.add_parser('process', help='Process operations')
    process_subparsers = process_parser.add_subparsers(dest='process_action')
    process_subparsers.add_parser('list', help='List all processes')
    process_subparsers.add_parser('create', help='Create a new process')
    process_subparsers.add_parser('show', help='Show process details')
    
    # Type commands
    type_parser = subparsers.add_parser('type', help='Type operations')
    type_subparsers = type_parser.add_subparsers(dest='type_action')
    type_subparsers.add_parser('list', help='List all types')
    type_subparsers.add_parser('create', help='Create a new type')
    type_subparsers.add_parser('tree', help='Show type tree')
    
    # IP commands
    ip_parser = subparsers.add_parser('ip', help='IP operations')
    ip_subparsers = ip_parser.add_subparsers(dest='ip_action')
    ip_subparsers.add_parser('list', help='List IPs')
    ip_subparsers.add_parser('create', help='Create a new IP')
    ip_subparsers.add_parser('show', help='Show IP details')
    ip_subparsers.add_parser('find', help='Find IPs by criteria')
    ip_subparsers.add_parser('release', help='Release an IP')
    ip_subparsers.add_parser('update', help='Update an IP')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'db':
            handle_db_command(args)
        elif args.command == 'process':
            handle_process_command(args)
        elif args.command == 'type':
            handle_type_command(args)
        elif args.command == 'ip':
            handle_ip_command(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def handle_db_command(args):
    """Handle database commands"""
    if args.db_action == 'init':
        print("Initializing database...")
        if db_manager.connect():
            db_manager.create_tables()
            print("Database initialized successfully!")
        else:
            print("Failed to connect to database", file=sys.stderr)
            sys.exit(1)
    elif args.db_action == 'status':
        if db_manager.connect():
            print("Database connection successful!")
        else:
            print("Database connection failed", file=sys.stderr)
            sys.exit(1)

def handle_process_command(args):
    """Handle process commands"""
    if args.process_action == 'list':
        processes = Process.find_all()
        for process in processes:
            print(f"{process.id}: {process.name} (Node: {process.node}, FAB: {process.fab})")
    elif args.process_action == 'create':
        name = input("Process name: ")
        node = input("Node: ")
        fab = input("FAB: ")
        description = input("Description (optional): ")
        
        process = Process(name=name, node=node, fab=fab, description=description)
        if process.save():
            print(f"Process '{name}' created successfully!")
        else:
            print("Failed to create process", file=sys.stderr)
    elif args.process_action == 'show':
        name = input("Process name: ")
        process = Process.find_by_name(name)
        if process:
            print(json.dumps(process.to_dict(), indent=2, default=str))
        else:
            print("Process not found", file=sys.stderr)

def handle_type_command(args):
    """Handle type commands"""
    if args.type_action == 'list':
        types = Type.find_all()
        for type_obj in types:
            indent = "  " * type_obj.level
            print(f"{indent}{type_obj.name} (ID: {type_obj.id}, Path: {type_obj.path})")
    elif args.type_action == 'create':
        name = input("Type name: ")
        parent_name = input("Parent type name (optional): ")
        description = input("Description (optional): ")
        
        parent_id = None
        if parent_name:
            parent = Type.find_by_name(parent_name)
            if parent:
                parent_id = parent.id
            else:
                print("Parent type not found", file=sys.stderr)
                return
        
        type_obj = Type(name=name, parent_id=parent_id, description=description)
        if type_obj.save():
            print(f"Type '{name}' created successfully!")
        else:
            print("Failed to create type", file=sys.stderr)
    elif args.type_action == 'tree':
        print_type_tree()

def print_type_tree(types=None, level=0):
    """Print type tree structure"""
    if types is None:
        types = Type.find_roots()
    
    for type_obj in types:
        indent = "  " * level
        print(f"{indent}├─ {type_obj.name}")
        children = type_obj.find_children()
        if children:
            print_type_tree(children, level + 1)

def handle_ip_command(args):
    """Handle IP commands"""
    if args.ip_action == 'list':
        ips = IP.find_all()
        for ip in ips:
            process = Process.find_by_id(ip.process_id)
            type = Type.find_by_id(ip.type_id)
            print(f"{ip.id}: {ip.name} (Status: {ip.status}, IP Type Path: {type.path}, Process: {process.name})")

    elif args.ip_action == 'create':
        name = input("IP name: ")
        type_name = input("Type name: ")
        process_name = input("Process name: ")
        revision = input("Revision (default: 1.0): ") or "1.0"
        status = input("Status (alpha/beta/production/obsolete, default: alpha): ") or "alpha"
        provider = input("Provider: ")
        description = input("Description (optional): ")
        
        # Find type and process
        type_obj = Type.find_by_name(type_name)
        process = Process.find_by_name(process_name)
        
        if not type_obj:
            print("Type not found", file=sys.stderr)
            return
        if not process:
            print("Process not found", file=sys.stderr)
            return
        
        ip = IP(
            name=name,
            type_id=type_obj.id,
            process_id=process.id,
            revision=revision,
            status=status,
            provider=provider,
            description=description
        )
        
        if ip.save():
            print(f"IP '{name}' created successfully!")
        else:
            print("Failed to create IP", file=sys.stderr)
    elif args.ip_action == 'show':
        name = input("IP name: ")
        ip = IP.find_by_name(name)
        if ip:
            ip_data = ip.to_dict()
            ip_data['type'] = ip.get_type().to_dict() if ip.get_type() else None
            ip_data['process'] = ip.get_process().to_dict() if ip.get_process() else None
            print(json.dumps(ip_data, indent=2, default=str))
        else:
            print("IP not found", file=sys.stderr)
    elif args.ip_action == 'find':
        print("Enter search criteria (leave empty to skip):")
        criteria = {}
        
        name = input("Name: ").strip()
        if name:
            criteria['name'] = name
        
        type_name = input("Type name: ").strip()
        if type_name:
            criteria['type_name'] = type_name
        
        status = input("Status: ").strip()
        if status:
            criteria['status'] = status
        
        provider = input("Provider: ").strip()
        if provider:
            criteria['provider'] = provider
        
        ips = ip_manager.find(**criteria)
        for ip in ips:
            print(f"{ip.id}: {ip.name} (Status: {ip.status}, Type: {ip.type_id})")
    elif args.ip_action == 'release':
        name = input("IP name to release: ")
        if ip_manager.release(name):
            print(f"IP '{name}' released successfully!")
        else:
            print("Failed to release IP", file=sys.stderr)
    elif args.ip_action == 'update':
        name = input("IP name to update: ")
        print("Enter new values (leave empty to keep current):")
        
        updates = {}
        new_name = input("New name: ").strip()
        if new_name:
            updates['name'] = new_name
        
        new_status = input("New status: ").strip()
        if new_status:
            updates['status'] = new_status
        
        new_description = input("New description: ").strip()
        if new_description:
            updates['description'] = new_description
        
        if ip_manager.update(name, **updates):
            print(f"IP '{name}' updated successfully!")
        else:
            print("Failed to update IP", file=sys.stderr)

if __name__ == "__main__":
    main()
