#!/usr/bin/env python3
"""
NetMan Quick Demo Script

This script demonstrates the key features of NetMan by running
a series of commands with the demo mode enabled.
"""
import os
import subprocess
import time

# Set demo mode environment variable
os.environ['NETMAN_DEMO_MODE'] = 'true'

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def run_command(command, description=None):
    """Run a NetMan command and display the output."""
    if description:
        print(f"\n>>> {description}")
    
    print(f"$ python netman.py {command}\n")
    
    # Execute the command
    process = subprocess.run(
        f"python netman.py {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Print the output
    print(process.stdout)
    
    # Add a slight delay for readability
    time.sleep(1)

def main():
    """Run the demo script."""
    print_header("NetMan CLI Tool Demo")
    print("This demo showcases the key features of NetMan in demo mode.")
    print("No real network devices are required to run this demo.")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Part 1: Help and version information
    print_header("NetMan Help and Version")
    run_command("--help", "Show help information")
    run_command("--version", "Show version information")
    
    # Part 2: Inventory Management
    print_header("Inventory Management")
    
    # Add demo devices
    run_command("inventory add demo-router1 --ip 192.168.1.1 --device-type cisco_ios --username admin --password admin123 --groups core,routing", 
               "Add a Cisco router to inventory")
    
    run_command("inventory add demo-switch1 --ip 192.168.1.2 --device-type cisco_ios --username admin --password admin123 --groups access,switching", 
               "Add a Cisco switch to inventory")
    
    # List devices
    run_command("inventory list", "List all devices in inventory")
    
    # List devices by group
    run_command("inventory list --group core", "List devices in 'core' group")
    
    # Part 3: Monitoring
    print_header("Device Monitoring")
    
    # Check device status
    run_command("monitor status demo-router1", "Check status of a specific device")
    run_command("monitor status --all", "Check status of all devices")
    
    # Get device facts
    run_command("monitor facts demo-router1", "Get detailed facts about a device")
    
    # Part 4: Configuration Management
    print_header("Configuration Management")
    
    # Show available templates
    run_command("template list", "List available configuration templates")
    run_command("template show cisco_base", "Show content of the Cisco base template")
    
    # Dry run configuration push
    run_command("config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run", 
               "Generate configuration (dry run)")
    
    # Backup configuration
    run_command("config backup demo-router1", "Backup configuration of a device")
    run_command("config backup --all", "Backup configuration of all devices")
    
    # Compare configurations
    run_command("config diff demo-router1", "Compare configuration versions")
    
    print_header("Demo Completed")
    print("The NetMan demo has completed successfully.")
    print("You can run individual commands in demo mode with:")
    print("  export NETMAN_DEMO_MODE=true")
    print("  python netman.py <command>")
    print("\nOr use the interactive demo menu with:")
    print("  python demo.py")

if __name__ == "__main__":
    main()