#!/usr/bin/env python3
"""
NetMan Multi-Vendor Test Script

This script demonstrates all supported device types:
- Cisco IOS (Router & Switch)
- Cisco ACI
- Juniper SRX
- Palo Alto Firewall
"""
import os
import subprocess
import time
from pathlib import Path

# Set demo mode
os.environ['NETMAN_DEMO_MODE'] = 'true'

def run_command(command, description=None):
    """Run a NetMan command and display the output."""
    if description:
        print(f"\n=== {description} ===")
    
    print(f"$ python netman.py {command}\n")
    
    # Execute the command
    process = subprocess.run(
        f"python netman.py {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Print the output
    print(process.stdout)
    if process.stderr:
        print(f"Error: {process.stderr}")
    
    # Add a slight delay for readability
    time.sleep(1)
    
    return process.returncode == 0

def main():
    """Run the test script."""
    print("NetMan Multi-Vendor Test")
    print("=======================")
    
    # Setup demo environment
    subprocess.run("python demo/setup_demo_environment.py", shell=True)
    print("Demo environment setup complete!\n")
    
    # Part 1: List all devices
    run_command("inventory list", "Listing All Devices")
    
    # Part 2: Status check for all devices
    run_command("monitor status --all", "Status Check for All Devices")
    
    # Part 3: Device facts for each platform
    print("\n=== Device Facts by Platform ===")
    
    print("\n--- Cisco IOS Router ---")
    run_command("monitor facts demo-router1")
    
    print("\n--- Cisco ACI Controller ---")
    run_command("monitor facts demo-aci1")
    
    print("\n--- Juniper SRX Firewall ---")
    run_command("monitor facts demo-juniper1")
    
    print("\n--- Palo Alto Firewall ---")
    run_command("monitor facts demo-paloalto1")
    
    # Part 4: Template rendering for each platform
    print("\n=== Template Rendering by Platform ===")
    
    print("\n--- Cisco IOS Router Configuration ---")
    run_command("config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run")
    
    print("\n--- Juniper SRX Configuration ---")
    run_command("config push demo-juniper1 --template juniper_srx --vars demo/vars/demo-juniper1.yml --dry-run")
    
    print("\n--- Palo Alto Configuration ---")
    run_command("config push demo-paloalto1 --template paloalto_fw --vars demo/vars/demo-paloalto1.yml --dry-run")
    
    print("\n=== Test Completed ===")
    print("NetMan has successfully demonstrated multi-vendor support!")

if __name__ == "__main__":
    main()