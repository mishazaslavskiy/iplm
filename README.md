# IPLM - IP Management System

A draft of IP (Intellectual Property) management system built with Python and MySQL, designed for managing IP cores, processes, and hierarchical type classification in semiconductor design workflows.

## Features

- **Process Management**: Track semiconductor processes with node, FAB, and description information
- **IP Management**: IP tracking with status, revision, provider, and component details
- **Type Classification**: Tree-structured IP type classification system
- **Database Integration**: MySQL database with configurable schemas
- **Core Operations**: Release, Find, Update, and Schema change capabilities
- **CLI Interface**: Command-line interface for all operations
- **Object-Oriented Design**: Extensible Python classes

## Project Structure

```
iplm/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── models.py          # Base model and Process class
│   ├── ip_model.py        # IP model class
│   ├── type_model.py      # Type model (tree structure)
│   ├── core_methods.py    # Core operations (Release, Find, Update, etc.)
│   ├── database.py        # Database connection and management
│   └── cli.py             # Command-line interface
├── config/                 # Configuration files
│   ├── database.yaml      # Database schema configuration
│   └── settings.py        # Application settings
├── examples/              # Usage examples
│   └── basic_usage.py     # Basic usage demonstration
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## Installation

1. **Clone or download the project**:
   ```bash
   cd /path/to/iplm
   ```

2. **Set up MySQL database**:
   - Install MySQL server
   - Run the database setup script:
     ```bash
     mysql -u root -p < setup_database.sql
     ```
   - Or manually create database and user (see `setup_database.sql`)

3. **Install dependencies**:
   
   **Option A: Using virtual environment (recommended)**:
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   
   **Option B: Using install script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

4. **Test installation**:
   ```bash
   python test_setup.py
   ```

5. **Initialize the database**:
   ```bash
   python -m src.cli db init
   ```

## Configuration

### Database Configuration

Edit `config/database.yaml` or set environment variables:

```yaml
database:
  host: localhost
  port: 3306
  user: iplm_user
  password: iplm_password
  database: iplm_db
```

Environment variables (override YAML config):
- `IPLM_DB_HOST`
- `IPLM_DB_PORT`
- `IPLM_DB_USER`
- `IPLM_DB_PASSWORD`
- `IPLM_DB_NAME`

## Usage

### Command Line Interface

```bash
# Database operations
python -m src.cli db init          # Initialize database
python -m src.cli db status        # Check database status

# Process management
python -m src.cli process list     # List all processes
python -m src.cli process create   # Create new process
python -m src.cli process show     # Show process details

# Type management
python -m src.cli type list        # List all types
python -m src.cli type create      # Create new type
python -m src.cli type tree        # Show type tree

# IP management
python -m src.cli ip list          # List all IPs
python -m src.cli ip create        # Create new IP
python -m src.cli ip show          # Show IP details
python -m src.cli ip find          # Find IPs by criteria
python -m src.cli ip release       # Release an IP
python -m src.cli ip update        # Update an IP
```

### Python API

```python
from src import Process, IP, Type, ip_manager, db_manager

# Initialize database
db_manager.connect()
db_manager.create_tables()

# Create a process
process = Process(
    name="SoC_Design_v1",
    node="28nm",
    fab="TSMC",
    description="Main SoC design process"
)
process.save()

# Create type hierarchy
digital_type = Type(name="Digital", description="Digital IP types")
digital_type.save()

cpu_type = Type(name="CPU", parent_id=digital_type.id, description="CPU cores")
cpu_type.save()

# Create an IP
ip = IP(
    name="ARM_Cortex_A78",
    type_id=cpu_type.id,
    process_id=process.id,
    revision="2.1",
    status="production",
    provider="ARM Ltd.",
    description="High-performance ARM core"
)
ip.save()

# Find IPs
production_ips = ip_manager.find(status="production")
digital_ips = ip_manager.find_by_type_tree("Digital")

# Update IP
ip_manager.update("ARM_Cortex_A78", status="production")

# Release IP
ip_manager.release("ARM_Cortex_A78")
```

## Data Models

### Process Class
- **name**: Process name (unique)
- **node**: Technology node (e.g., "28nm", "7nm")
- **fab**: Foundry (e.g., "TSMC", "Samsung")
- **description**: Process description

### IP Class
- **name**: IP name (unique)
- **type_id**: Reference to Type
- **process_id**: Reference to Process
- **revision**: Version number
- **status**: alpha/beta/production/obsolete
- **provider**: IP provider company
- **parent_ip_id**: Reference to parent IP (for hierarchical structure)
- **description**: IP description
- **documentation**: Documentation URL

### Type Class (Tree Structure)
- **name**: Type name
- **parent_id**: Parent type ID (for tree structure)
- **path**: Full path in tree (e.g., "Digital/CPU/ARM")
- **level**: Depth in tree
- **description**: Type description

## Core Methods

### Release
Change IP status to production:
```python
ip_manager.release("IP_name")
```

### Find
Search IPs by various criteria:
```python
# Find by status
ips = ip_manager.find(status="production")

# Find by type
ips = ip_manager.find(type_name="CPU")

# Find by process
ips = ip_manager.find(process_name="SoC_Design_v1")

# Find by type tree (including descendants)
ips = ip_manager.find_by_type_tree("Digital", include_descendants=True)
```

### Tree Visualization
Display IP hierarchies in tree format:
```python
# Show all IP trees
ip_manager.show_ip_tree()

# Show tree for specific IP
ip_manager.show_ip_tree(ip_name="TSMC_7nm_SoC_v1.0")

# Show detailed tree with additional information
ip_manager.show_ip_tree(ip_name="TSMC_7nm_SoC_v1.0", show_details=True)

# Show trees by process
ip_manager.show_ip_tree_by_process("TSMC_7nm_SoC_Design")

# Show trees by type
ip_manager.show_ip_tree_by_type("Processor")
```

### Update
Update IP properties:
```python
ip_manager.update("IP_name", status="production", description="New description")
```

### Change Schema
Modify database schema (advanced):
```python
ip_manager.change_schema("ips", new_schema_definition)
```

## Examples

Run the basic usage example:
```bash
python examples/basic_usage.py
```

This will demonstrate:
- Creating type hierarchies
- Managing processes
- Creating and managing IPs
- Finding and updating IPs
- Packing IPs for export

## Command Line Interface

The system includes a comprehensive CLI for all operations:

### IP Tree Commands
```bash
# Show all IP trees
python -m src.cli ip tree

# Show tree for specific IP
python -m src.cli ip tree --ip "TSMC_7nm_SoC_v1.0"

# Show detailed tree
python -m src.cli ip tree --ip "TSMC_7nm_SoC_v1.0" --details

# Show trees by process
python -m src.cli ip tree --process "TSMC_7nm_SoC_Design"

# Show trees by type
python -m src.cli ip tree --type "Processor"
```

### Other Commands
```bash
# Database operations
python -m src.cli db init
python -m src.cli db status

# Process operations
python -m src.cli process list
python -m src.cli process create

# Type operations
python -m src.cli type list
python -m src.cli type tree

# IP operations
python -m src.cli ip list
python -m src.cli ip create
python -m src.cli ip find
python -m src.cli ip release
```

## Database Schema

The system uses three main tables:
- `processes`: Process information
- `types`: Hierarchical type classification
- `ips`: IP information with foreign keys to processes and types

See `config/database.yaml` for detailed schema definitions.

## Development

### Running Tests
```bash
pip install -r requirements.txt[dev]
pytest
```

### Code Formatting
```bash
black src/
flake8 src/
mypy src/
```

## License

GNU GPLv3 License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions, please create an issue in the project repository.
