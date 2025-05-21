#!/usr/bin/env python3
"""
NetMan Demo Setup Script

This script sets up a demo environment for the NetMan tool with sample devices
and templates for testing functionality without real network devices.
"""
import os
import sys
import json
import yaml
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import NetMan modules
from lib.inventory import InventoryManager
from lib.template_manager import TemplateManager

# Sample device data
DEMO_DEVICES = [
    {
        "hostname": "demo-router1",
        "ip": "192.168.1.1",
        "device_type": "cisco_ios",
        "username": "demo",
        "password": "demo123",
        "ssh_port": 22,
        "groups": ["demo", "routers"]
    },
    {
        "hostname": "demo-switch1",
        "ip": "192.168.1.2",
        "device_type": "cisco_ios",
        "username": "demo",
        "password": "demo123",
        "ssh_port": 22,
        "groups": ["demo", "switches"]
    },
    {
        "hostname": "demo-firewall1",
        "ip": "192.168.1.3",
        "device_type": "cisco_ios",
        "username": "demo",
        "password": "demo123",
        "ssh_port": 22,
        "groups": ["demo", "firewalls"]
    }
]

# Sample template variables
DEMO_VARS = {
    "demo-router1": {
        "hostname": "demo-router1",
        "domain_name": "demo.local",
        "enable_secret": "demo-enable",
        "username": "admin",
        "password": "admin123",
        "interfaces": [
            {
                "name": "GigabitEthernet0/0",
                "description": "WAN Interface",
                "ip": "10.0.0.1",
                "netmask": "255.255.255.0",
                "shutdown": False
            },
            {
                "name": "GigabitEthernet0/1",
                "description": "LAN Interface",
                "ip": "192.168.1.1",
                "netmask": "255.255.255.0",
                "shutdown": False
            }
        ],
        "routing": True,
        "ospf": {
            "process_id": 1,
            "networks": [
                {
                    "address": "10.0.0.0",
                    "wildcard": "0.0.0.255",
                    "area": 0
                },
                {
                    "address": "192.168.1.0",
                    "wildcard": "0.0.0.255",
                    "area": 0
                }
            ]
        },
        "ntp_servers": ["10.0.0.10", "10.0.0.11"],
        "syslog_servers": ["10.0.0.20"],
        "logging_source_interface": "GigabitEthernet0/0",
        "snmp_community": "demopublic",
        "snmp_contact": "Demo Admin",
        "snmp_location": "Demo Lab",
        "banner": "Welcome to NetMan Demo Router!\nAuthorized access only."
    }
}

def setup_demo_environment():
    """Set up the demo environment with sample devices and templates."""
    print("Setting up NetMan demo environment...")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    os.makedirs('demo/vars', exist_ok=True)
    
    # Initialize managers
    inventory_manager = InventoryManager()
    
    # Add demo devices
    for device in DEMO_DEVICES:
        print(f"Adding demo device: {device['hostname']}")
        inventory_manager.add_device(
            hostname=device['hostname'],
            ip=device['ip'],
            device_type=device['device_type'],
            username=device['username'],
            password=device['password'],
            ssh_port=device['ssh_port'],
            groups=device['groups']
        )
    
    # Create demo variable files
    for hostname, vars_data in DEMO_VARS.items():
        vars_file = f"demo/vars/{hostname}.yml"
        print(f"Creating variables file: {vars_file}")
        with open(vars_file, 'w') as f:
            yaml.dump(vars_data, f, default_flow_style=False)
    
    print("\nDemo environment setup complete!")
    print("\nYou can now try these commands:")
    print("  - python netman.py inventory list")
    print("  - python netman.py template list")
    print("  - python netman.py config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run")
    print("  - python netman.py monitor status demo-router1")

if __name__ == "__main__":
    setup_demo_environment()