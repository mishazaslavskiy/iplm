"""
Configuration settings for IPLM project
"""
import os
import yaml
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

def load_config():
    """Load configuration from YAML file"""
    config_file = CONFIG_DIR / "database.yaml"
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def get_database_config():
    """Get database configuration"""
    config = load_config()
    return config['database']

def get_schema_config():
    """Get schema configuration"""
    config = load_config()
    return config['schemas']

# Environment variables override
DATABASE_CONFIG = {
    'host': os.getenv('IPLM_DB_HOST', 'localhost'),
    'port': int(os.getenv('IPLM_DB_PORT', 3306)),
    'user': os.getenv('IPLM_DB_USER', 'iplm_user'),
    'password': os.getenv('IPLM_DB_PASSWORD', 'IPLM_password_123'),
    'database': os.getenv('IPLM_DB_NAME', 'iplm_db'),
    'charset': 'utf8mb4',
    'autocommit': True
}

# Status constants
IP_STATUSES = ['alpha', 'beta', 'production', 'obsolete']

# Default values
DEFAULT_REVISION = '1.0'
DEFAULT_STATUS = 'alpha'
