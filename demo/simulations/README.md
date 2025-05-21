# NetMan Simulation Data

This directory contains simulation responses for testing NetMan without real network devices.

The files in this directory are used by the simulator module to provide mock responses for commands when running in demo mode.

## File Format

The simulation files are YAML files with the following structure:

```yaml
device_type:
  "command": |
    Command output
    line 1
    line 2
  "another command": |
    Another command output
    line 1
    line 2
```

Where:
- `device_type` is the type of device (e.g., cisco_ios, junos, arista_eos)
- `command` is the command to simulate
- The multiline string is the command output

## Adding Custom Simulations

You can add your own custom simulation responses by:

1. Creating a new YAML file in this directory
2. Adding device types and command responses

The simulator will automatically load all YAML files in this directory.

## Running in Demo Mode

To enable demo mode:

```bash
# In Linux/macOS
export NETMAN_DEMO_MODE=true
python netman.py <command>

# Or use the demo.py script
python demo.py
```