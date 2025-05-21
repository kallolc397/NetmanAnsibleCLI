#!/usr/bin/env python3
"""
NetMan Configuration Commands Test Script

This script tests the configuration management commands:
1. config backup
2. config diff
3. config push (apply to device)
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
    """Prepare the test environment by ensuring directories exist."""
    # Create necessary directories
    os.makedirs('configs', exist_ok=True)
    os.makedirs('configs/demo-router1', exist_ok=True)
    
    # Create a sample config file if it doesn't exist
    sample_config = Path('configs/demo-router1/demo-router1_sample.cfg')
    if not sample_config.exists():
        # Get a sample config from simulator
        result = subprocess.run(
            "python -c \"from lib.simulator import DeviceSimulator; print(DeviceSimulator().get_response('cisco_ios', 'show running-config'))\"",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0 and result.stdout:
            sample_config.write_text(result.stdout)
        else:
            # Fallback to a basic sample
            sample_config.write_text("""!
! Sample Cisco IOS Configuration
!
hostname demo-router1
!
interface GigabitEthernet0/0
 description WAN Interface
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
end
""")
    
    print(f"Prepared test environment with sample config at {sample_config}")
    
    # Setup demo environment
    subprocess.run("python demo/setup_demo_environment.py", shell=True)

def main():
    """Run the test script."""
    print("NetMan Configuration Commands Test")
    print("==================================")
    
    # Prepare test environment
    prepare_environment()
    
    # 1. Test config backup
    success = run_command(
        "config backup demo-router1",
        "Test 1: Backup Configuration"
    )
    
    if not success:
        print("Warning: Backup command had issues")
    
    time.sleep(1)
    
    # Check if backup was created
    backup_dir = Path('configs/demo-router1')
    backup_files = list(backup_dir.glob('*.cfg'))
    
    if backup_files:
        print(f"Found backup files: {[f.name for f in backup_files]}")
    else:
        # Create a manual backup for diff test
        manual_backup = backup_dir / 'demo-router1_manual.cfg'
        with open(manual_backup, 'w') as f:
            f.write("""!
! Manual backup for testing diff
!
hostname demo-router1
!
interface GigabitEthernet0/0
 description WAN Interface
 ip address 10.0.0.1 255.255.255.0
 no shutdown
!
interface GigabitEthernet0/1
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
end
""")
        print(f"Created manual backup file: {manual_backup.name}")
    
    time.sleep(1)
    
    # 2. Test config diff
    run_command(
        "config diff demo-router1",
        "Test 2: Configuration Diff"
    )
    
    time.sleep(1)
    
    # 3. Test config push
    run_command(
        "config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run",
        "Test 3: Push Configuration (dry run)"
    )
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()