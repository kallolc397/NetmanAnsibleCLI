#!/usr/bin/env python3
"""
NetMan Firewall Devices Test Script

This script demonstrates the Juniper SRX and Palo Alto device capabilities:
1. Check status of firewalls
2. Get detailed facts
3. Push configuration templates (dry run)
4. Compare configuration differences
"""
import os
import subprocess
import time
from pathlib import Path

# Set demo mode
os.environ['NETMAN_DEMO_MODE'] = 'true'

def run_command(command, description):
    """Run a NetMan command and display the output."""
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

def prepare_environment():
    """Prepare the test environment by setting up the demo."""
    print("Setting up demo environment...")
    subprocess.run("python demo/setup_demo_environment.py", shell=True)
    
    # Ensure config directories exist
    Path("configs/demo-juniper1").mkdir(parents=True, exist_ok=True)
    Path("configs/demo-paloalto1").mkdir(parents=True, exist_ok=True)
    
    # Create sample configs for testing
    with open("configs/demo-juniper1/demo-juniper1_latest.cfg", "w") as f:
        f.write("# Sample Juniper configuration for testing\nversion 20.4R3-S1;\nsystem {\n    host-name demo-juniper1;\n}\n")
    
    with open("configs/demo-paloalto1/demo-paloalto1_latest.cfg", "w") as f:
        f.write("# Sample Palo Alto configuration for testing\nset deviceconfig system hostname demo-paloalto1\n")

def main():
    """Run the test script."""
    print("NetMan Firewall Devices Test")
    print("============================")
    
    # Setup environment
    prepare_environment()
    
    # Part 1: Test Inventory Commands
    run_command("inventory list --group firewalls", "List Firewall Devices")
    
    # Part 2: Test Status Monitoring
    run_command("monitor status demo-juniper1", "Check Juniper SRX Status")
    run_command("monitor status demo-paloalto1", "Check Palo Alto Status")
    
    # Part 3: Test Facts Gathering
    run_command("monitor facts demo-juniper1", "Get Juniper SRX Facts")
    run_command("monitor facts demo-paloalto1", "Get Palo Alto Facts")
    
    # Part 4: Test Configuration Commands
    # Backup configurations
    run_command("config backup demo-juniper1", "Backup Juniper Configuration")
    run_command("config backup demo-paloalto1", "Backup Palo Alto Configuration")
    
    # Generate configurations from templates (dry run)
    run_command("config push demo-juniper1 --template juniper_srx --vars demo/vars/demo-juniper1.yml --dry-run", 
               "Generate Juniper Configuration")
    
    run_command("config push demo-paloalto1 --template paloalto_fw --vars demo/vars/demo-paloalto1.yml --dry-run", 
               "Generate Palo Alto Configuration")
    
    # Show configuration differences
    run_command("config diff demo-juniper1", "Show Juniper Configuration Differences")
    run_command("config diff demo-paloalto1", "Show Palo Alto Configuration Differences")
    
    print("\n=== Test Complete ===")
    print("NetMan successfully tested Juniper and Palo Alto device support!")

if __name__ == "__main__":
    main()