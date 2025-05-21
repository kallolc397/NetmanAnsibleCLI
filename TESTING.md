# Testing NetMan

This document provides instructions for testing the NetMan network management tool.

## Demo Mode

NetMan includes a demo mode that allows you to test the functionality without requiring real network devices. The demo mode uses simulated device responses for testing.

### Running the Demo

To run NetMan in demo mode, use the included demo script:

```bash
python demo.py
```

This will:
1. Set up a demo environment with sample devices
2. Present a menu of commands to test
3. Execute NetMan commands with simulated device responses

### Demo Devices

The demo environment includes several pre-configured devices:

- `demo-router1` - A Cisco IOS router
- `demo-switch1` - A Cisco IOS switch
- `demo-firewall1` - A Cisco IOS firewall

### Testing Specific Commands

You can also run NetMan commands directly in demo mode:

```bash
# Set demo mode environment variable
export NETMAN_DEMO_MODE=true

# Run NetMan commands
python netman.py inventory list
python netman.py monitor status demo-router1
python netman.py config push demo-router1 --template cisco_base --vars demo/vars/demo-router1.yml --dry-run
```

## Testing with Real Devices

To test with real network devices:

1. Add your devices to the inventory:

```bash
python netman.py inventory add router1 --ip 192.168.1.1 --device-type cisco_ios --username admin --password mypassword
```

2. Test connectivity to the devices:

```bash
python netman.py monitor status router1
```

3. Push configurations:

```bash
python netman.py config push router1 --template cisco_base --vars router1_vars.yml
```

## Ansible Playbooks

The `playbooks/` directory contains Ansible playbooks that NetMan uses for device interactions:

- `configure_device.yml` - Applies configurations to devices
- `backup_config.yml` - Backs up device configurations
- `get_device_status.yml` - Retrieves device status and facts
- `demo_connectivity.yml` - Tests basic connectivity to devices

You can run these playbooks directly using Ansible for testing:

```bash
ansible-playbook -i data/ansible_inventory.yml playbooks/demo_connectivity.yml -e "target_host=demo-router1"
```

## Extending Simulations

To add more simulated command responses, edit or add YAML files in the `demo/simulations/` directory. The files should follow this format:

```yaml
device_type:
  "command": |
    Command output
    line 1
    line 2
```

## Testing Tips

- Use `--dry-run` option with configuration commands to preview changes without applying them
- Test demo mode first to understand the tool's functionality before connecting to real devices
- Add debugging by setting the log level in `config/settings.yml`