# NetMan - Network Device Management CLI Tool

NetMan is a Python CLI tool for managing network devices using Ansible for configuration, monitoring, and automation tasks.

## Features

- **Inventory Management**: Add, list, and remove network devices
- **Configuration Management**: Push, backup, and compare device configurations
- **Monitoring**: Check device status and retrieve system information
- **Template Management**: Manage Jinja2 configuration templates
- **Version Control**: Track configuration changes with Git integration

## Installation

### Requirements

- Python 3.6+
- Ansible (for network automation)
- Git (for configuration version control)

### Dependencies

```
click==8.2.1
rich==14.0.0
jinja2==3.1.6
pyyaml==6.0.2
gitpython==3.1.44
ansible==11.6.0
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/netman.git
cd netman
```

2. Install the dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Show help
python netman.py --help

# Manage inventory
python netman.py inventory add HOSTNAME --ip IP --device-type TYPE --username USER --password PASS
python netman.py inventory list
python netman.py inventory remove HOSTNAME

# Manage configurations
python netman.py config push HOSTNAME --template TEMPLATE [--vars VARS_FILE]
python netman.py config backup HOSTNAME
python netman.py config diff HOSTNAME

# Monitor devices
python netman.py monitor status HOSTNAME
python netman.py monitor facts HOSTNAME

# Manage templates
python netman.py template list
python netman.py template show TEMPLATE_NAME
```

## Directory Structure

```
netman/
├── config/           # Configuration files
├── lib/              # Library modules
├── playbooks/        # Ansible playbooks
├── templates/        # Configuration templates
├── data/             # Device inventory data
├── configs/          # Backed up configurations
├── logs/             # Log files
└── netman.py         # Main CLI tool
```

## Examples

### Adding a Device

```bash
python netman.py inventory add router1 --ip 192.168.1.1 --device-type cisco_ios --username admin --password mypassword --groups core,production
```

### Pushing a Configuration

```bash
python netman.py config push router1 --template cisco_base --vars router1_vars.yml
```

### Monitoring Device Status

```bash
python netman.py monitor status --all
```

## License

MIT