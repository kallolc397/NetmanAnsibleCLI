#!/usr/bin/env python3
"""
NetMan Cisco ACI Commands Test Script

This script tests the Cisco ACI device management capabilities:
1. Check status of demo-aci1
2. Get facts from demo-aci1
3. Push ACI template to demo-aci1 (dry run)
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
    
    result = subprocess.run(
        f"python netman.py {command}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    
    return result.returncode == 0

def prepare_environment():
    """Prepare the test environment by setting up the demo."""
    # Setup demo environment
    print("Setting up NetMan demo environment with Cisco ACI support...")
    subprocess.run("python demo/setup_demo_environment.py", shell=True)
    print("Demo environment setup complete!")

def main():
    """Run the test script."""
    print("NetMan Cisco ACI Commands Test")
    print("==============================")
    
    # Prepare test environment
    prepare_environment()
    
    # 1. Test ACI device status
    run_command(
        "monitor status demo-aci1",
        "Test 1: Check Cisco ACI Controller Status"
    )
    
    time.sleep(1)
    
    # 2. Test ACI device facts
    run_command(
        "monitor facts demo-aci1",
        "Test 2: Get Cisco ACI Controller Facts"
    )
    
    time.sleep(1)
    
    # 3. Test ACI template push
    run_command(
        "config push demo-aci1 --template cisco_aci --vars demo/vars/demo-aci1.yml --dry-run",
        "Test 3: Push ACI Configuration Template (dry run)"
    )
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()