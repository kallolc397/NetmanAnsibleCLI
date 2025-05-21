# NetMan - Network Device Management CLI Tool

NetMan is a Python CLI tool for managing network devices using Ansible for configuration, monitoring, and automation tasks. It provides a simple interface for network administrators to manage device inventory, push configurations, monitor device status, and maintain version control of network configurations.

## Features

- **Inventory Management**: Add, list, and remove network devices with support for grouping
- **Configuration Management**: Push, backup, compare, and track configurations with Git
- **Monitoring**: Check device status, connectivity, and retrieve detailed system information
- **Template Management**: Create and manage Jinja2 configuration templates for different device types
- **Multi-vendor Support**: Works with Cisco IOS, Cisco ACI, Juniper, and Palo Alto devices
- **Ansible Integration**: Leverage Ansible's powerful network automation capabilities
- **Demo Mode**: Test and demonstrate functionality without requiring real network devices

## Installation

### Requirements

- Python 3.6+
- Ansible 2.9+ (for network automation)
- Git (for configuration version control)

### Dependencies

```
click>=8.2.1
rich>=14.0.0
jinja2>=3.1.6
pyyaml>=6.0.2
gitpython>=3.1.44
ansible>=11.6.0
```

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/netman.git
cd netman
```

2. Install the dependencies:
```bash
pip install click rich jinja2 pyyaml gitpython ansible
```

3. Create required directories:
```bash
mkdir -p data configs logs
```

## Detailed Command Reference

### Global Options

```bash
# Show version
python netman.py --version

# Show help
python netman.py --help
```

### Inventory Management

```bash
# List all inventory commands
python netman.py inventory --help

# Add a device
python netman.py inventory add HOSTNAME --ip IP_ADDRESS --device-type DEVICE_TYPE --username USERNAME --password PASSWORD [--ssh-port PORT] [--groups GROUP1,GROUP2]

# List all devices
python netman.py inventory list

# List devices in a specific group
python netman.py inventory list --group GROUP_NAME

# Remove a device (with confirmation)
python netman.py inventory remove HOSTNAME

# Remove a device (without confirmation)
python netman.py inventory remove HOSTNAME --force
```

### Configuration Management

```bash
# List all configuration commands
python netman.py config --help

# Push configuration to a device
python netman.py config push HOSTNAME --template TEMPLATE_NAME --vars VARS_FILE

# Perform a dry run (generate configuration without applying)
python netman.py config push HOSTNAME --template TEMPLATE_NAME --vars VARS_FILE --dry-run

# Backup configuration from a single device
python netman.py config backup HOSTNAME

# Backup configuration from all devices
python netman.py config backup --all

# Compare configuration differences (latest changes)
python netman.py config diff HOSTNAME

# Compare configuration with specific revisions
python netman.py config diff HOSTNAME --revisions "HEAD~2..HEAD"
```

### Monitoring

```bash
# List all monitoring commands
python netman.py monitor --help

# Check status of a specific device
python netman.py monitor status HOSTNAME

# Check status of all devices
python netman.py monitor status --all

# Retrieve detailed facts about a device
python netman.py monitor facts HOSTNAME
```

### Template Management

```bash
# List all template commands
python netman.py template --help

# List available templates
python netman.py template list

# Show content of a specific template
python netman.py template show TEMPLATE_NAME
```

## Directory Structure

```
netman/
├── config/                # Configuration files
│   └── settings.yml       # Global settings for the application
├── lib/                   # Library modules
│   ├── ansible_runner.py  # Ansible integration
│   ├── config_manager.py  # Configuration management
│   ├── git_manager.py     # Git version control
│   ├── inventory.py       # Device inventory management
│   ├── monitoring.py      # Device monitoring
│   ├── simulator.py       # Demo mode simulation
│   └── template_manager.py # Template management
├── playbooks/             # Ansible playbooks
│   ├── backup_config.yml  # Playbook for backing up configs
│   ├── configure_device.yml # Playbook for applying configs
│   ├── demo_connectivity.yml # Demo connectivity testing
│   └── get_device_status.yml # Playbook for checking status
├── templates/             # Configuration templates
│   ├── cisco_base.j2      # Base Cisco IOS template
│   ├── cisco_aci.j2       # Cisco ACI template
│   ├── juniper_srx.j2     # Juniper SRX template
│   └── paloalto_fw.j2     # Palo Alto firewall template
├── data/                  # Device inventory data
│   ├── inventory.json     # JSON inventory data
│   └── ansible_inventory.yml # Generated Ansible inventory
├── configs/               # Backed up configurations (Git-tracked)
├── logs/                  # Log files
├── demo/                  # Demo and testing utilities
│   ├── simulations/       # Simulation response files
│   └── vars/              # Template variables for demos
├── demo.py                # Demo mode launcher
├── netman.py              # Main CLI tool
└── README.md              # Documentation
```

## Practical Examples

### Adding Devices to Inventory

Add a Cisco router:
```bash
python netman.py inventory add router1 --ip 192.168.1.1 --device-type cisco_ios --username admin --password Cisco123 --groups core,production
```

Add a Juniper SRX firewall:
```bash
python netman.py inventory add srx1 --ip 192.168.2.1 --device-type junos --username admin --password Juniper123 --ssh-port 22 --groups firewalls,core
```

Add a Palo Alto firewall:
```bash
python netman.py inventory add pa1 --ip 192.168.3.1 --device-type panos --username admin --password PaloAlto123 --groups firewalls,dmz
```

Add a Cisco ACI controller:
```bash
python netman.py inventory add apic1 --ip 10.0.0.1 --device-type cisco_aci --username admin --password Cisco123 --groups fabric,datacenter
```

### Working with Configuration Templates

Create a variables file (router1_vars.yml):
```yaml
hostname: router1
domain_name: example.net
interfaces:
  - name: GigabitEthernet0/0
    description: Internet Connection
    ip: 203.0.113.1
    netmask: 255.255.255.0
  - name: GigabitEthernet0/1
    description: Internal Network
    ip: 192.168.10.1
    netmask: 255.255.255.0
ntp_servers:
  - 10.0.0.1
  - 10.0.0.2
snmp_community: public_string
snmp_location: "Data Center 1"
```

Push the configuration (dry run):
```bash
python netman.py config push router1 --template cisco_base --vars router1_vars.yml --dry-run
```

Push the configuration (apply to device):
```bash
python netman.py config push router1 --template cisco_base --vars router1_vars.yml
```

### Configuration Backup and Comparison

Backup all device configurations:
```bash
python netman.py config backup --all
```

Compare changes in a device's configuration:
```bash
python netman.py config diff router1
```

### Monitoring Network Devices

Check status of all devices:
```bash
python netman.py monitor status --all
```

Get detailed information about a device:
```bash
python netman.py monitor facts router1
```

## Demo Mode

NetMan includes a demo mode that allows you to test functionality without requiring real network devices:

```bash
# Run the demo script with interactive menu
python demo.py

# Run specific commands in demo mode
export NETMAN_DEMO_MODE=true
python netman.py inventory list
python netman.py monitor status demo-router1
python netman.py config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run
```

## Troubleshooting

### Common Issues

1. **Ansible Connectivity Problems**
   - Ensure SSH keys are properly set up
   - Verify network connectivity to devices
   - Check credentials in the inventory

2. **Git Integration Issues**
   - Ensure Git is installed and properly configured
   - Check permissions on the configs directory

3. **Template Rendering Errors**
   - Verify the template variable file format
   - Ensure all required variables are defined

## License

MIT