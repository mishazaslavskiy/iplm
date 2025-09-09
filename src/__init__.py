"""
IPLM - IP Management System

A comprehensive IP management system with MySQL database integration,
supporting Process, IP, and Type management with tree-structured classification.
"""

from .models import Process
from .ip_model import IP
from .type_model import Type
from .core_methods import IPManager, ip_manager
from .database import db_manager

__version__ = "1.0.0"
__author__ = "IPLM Team"

# Export main classes and functions
__all__ = [
    'Process',
    'IP', 
    'Type',
    'IPManager',
    'ip_manager',
    'db_manager'
]
