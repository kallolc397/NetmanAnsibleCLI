#!/usr/bin/env python3
"""
Network Device Management CLI Tool

A CLI tool that uses Ansible for configuration, monitoring, and automation
of network devices.
"""
import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import our library modules
from lib.inventory import InventoryManager
from lib.config_manager import ConfigManager
from lib.monitoring import Monitor
from lib.git_manager import GitManager
from lib.ansible_runner import AnsibleRunner
from lib.template_manager import TemplateManager

# Initialize console for rich output
console = Console()

# Create instances of our managers
inventory_manager = InventoryManager()
config_manager = ConfigManager()
monitor = Monitor()
git_manager = GitManager()
ansible_runner = AnsibleRunner()
template_manager = TemplateManager()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """NetMan - Network Device Management CLI Tool.
    
    A Python CLI tool for managing network devices using Ansible.
    """
    # Ensure our directory structure exists
    os.makedirs('data', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Initialize git repo if it doesn't exist
    if not os.path.exists(os.path.join('configs', '.git')):
        git_manager.init_repo('configs')

# --- Inventory Commands ---

@cli.group()
def inventory():
    """Manage network device inventory."""
    pass

@inventory.command("add")
@click.argument("hostname")
@click.option("--ip", required=True, help="IP address of the device")
@click.option("--device-type", required=True, help="Device type (e.g., cisco_ios)")
@click.option("--username", required=True, help="Username for authentication")
@click.option("--password", required=True, help="Password for authentication", hide_input=True)
@click.option("--ssh-port", default=22, help="SSH port (default: 22)")
@click.option("--groups", default="", help="Comma-separated list of groups")
def add_device(hostname, ip, device_type, username, password, ssh_port, groups):
    """Add a new device to inventory."""
    groups_list = [g.strip() for g in groups.split(',')] if groups else []
    
    success = inventory_manager.add_device(
        hostname=hostname,
        ip=ip,
        device_type=device_type,
        username=username,
        password=password,
        ssh_port=ssh_port,
        groups=groups_list
    )
    
    if success:
        console.print(f"[green]✓ Device {hostname} added successfully to inventory[/green]")
    else:
        console.print(f"[red]✗ Failed to add device {hostname}[/red]")

@inventory.command("list")
@click.option("--group", help="Filter devices by group")
def list_devices(group):
    """List devices in inventory."""
    devices = inventory_manager.list_devices(group)
    
    if not devices:
        console.print("[yellow]No devices found in inventory[/yellow]")
        return
    
    table = Table(title="Network Device Inventory")
    table.add_column("Hostname", style="cyan")
    table.add_column("IP Address", style="blue")
    table.add_column("Device Type", style="green")
    table.add_column("Groups", style="magenta")
    
    for device in devices:
        groups_str = ", ".join(device.get("groups", []))
        table.add_row(
            device["hostname"],
            device["ip"],
            device["device_type"],
            groups_str
        )
    
    console.print(table)

@inventory.command("remove")
@click.argument("hostname")
@click.option("--force", is_flag=True, help="Force removal without confirmation")
def remove_device(hostname, force):
    """Remove a device from inventory."""
    if not force:
        if not click.confirm(f"Are you sure you want to remove {hostname}?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
    
    success = inventory_manager.remove_device(hostname)
    if success:
        console.print(f"[green]✓ Device {hostname} removed from inventory[/green]")
    else:
        console.print(f"[red]✗ Failed to remove device {hostname}[/red]")

# --- Configuration Commands ---

@cli.group()
def config():
    """Manage device configurations."""
    pass

@config.command("push")
@click.argument("hostname")
@click.option("--template", required=True, help="Template name to use")
@click.option("--vars", help="Path to variables file")
@click.option("--dry-run", is_flag=True, help="Generate but don't apply config")
def push_config(hostname, template, vars, dry_run):
    """Push configuration to a device using a template."""
    # Generate config from template
    try:
        config_content = template_manager.render_template(template, vars)
        
        if dry_run:
            console.print(Panel(config_content, title=f"Configuration for {hostname} (Dry Run)", 
                               border_style="yellow"))
            return
        
        # Apply configuration
        success = config_manager.push_config(hostname, config_content)
        
        if success:
            console.print(f"[green]✓ Configuration applied to {hostname}[/green]")
            # Backup the new config and commit to git
            backup_path = config_manager.backup_config(hostname)
            if backup_path:
                git_manager.commit_changes(f"Updated configuration for {hostname}")
                console.print(f"[green]✓ Configuration backed up and committed to Git[/green]")
        else:
            console.print(f"[red]✗ Failed to apply configuration to {hostname}[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")

@config.command("backup")
@click.argument("hostname", required=False)
@click.option("--all", is_flag=True, help="Backup all devices")
def backup_config(hostname, all):
    """Backup device configuration to Git repository."""
    if not hostname and not all:
        console.print("[red]Error: Specify either a hostname or --all flag[/red]")
        return
    
    devices = []
    if all:
        devices = [device["hostname"] for device in inventory_manager.list_devices()]
    else:
        devices = [hostname]
    
    success_count = 0
    for device in devices:
        backup_path = config_manager.backup_config(device)
        if backup_path:
            success_count += 1
            console.print(f"[green]✓ Configuration backed up for {device}[/green]")
        else:
            console.print(f"[red]✗ Failed to backup configuration for {device}[/red]")
    
    if success_count > 0:
        git_manager.commit_changes(f"Backup configuration for {success_count} devices")
        console.print(f"[green]✓ Changes committed to Git repository[/green]")

@config.command("diff")
@click.argument("hostname")
@click.option("--revisions", default="HEAD~1..HEAD", help="Git revision range")
def diff_config(hostname, revisions):
    """Show configuration differences between revisions."""
    diff = git_manager.show_diff(hostname, revisions)
    if diff:
        console.print(Panel(diff, title=f"Configuration Diff for {hostname} ({revisions})", 
                          border_style="blue"))
    else:
        console.print("[yellow]No differences found or invalid revision range[/yellow]")

# --- Monitoring Commands ---

@cli.group()
def monitor():
    """Monitor network devices."""
    pass

@monitor.command("status")
@click.argument("hostname", required=False)
@click.option("--all", is_flag=True, help="Check all devices")
def check_status(hostname, all):
    """Check connection status of network devices."""
    if not hostname and not all:
        console.print("[red]Error: Specify either a hostname or --all flag[/red]")
        return
    
    devices = []
    if all:
        devices = [device["hostname"] for device in inventory_manager.list_devices()]
    else:
        devices = [hostname]
    
    table = Table(title="Device Status")
    table.add_column("Hostname", style="cyan")
    table.add_column("IP Address", style="blue")
    table.add_column("Status", style="bold")
    table.add_column("Response Time", style="magenta")
    
    with console.status("[bold green]Checking device status..."):
        for device_name in devices:
            device_info = inventory_manager.get_device(device_name)
            if not device_info:
                table.add_row(device_name, "Unknown", "[red]Not in inventory[/red]", "N/A")
                continue
                
            status, response_time = Monitor.check_device_status(device_info)
            status_str = "[green]Up[/green]" if status else "[red]Down[/red]"
            response_str = f"{response_time:.2f}ms" if status else "N/A"
            
            table.add_row(
                device_info["hostname"],
                device_info["ip"],
                status_str,
                response_str
            )
    
    console.print(table)

@monitor.command("facts")
@click.argument("hostname")
def get_facts(hostname):
    """Retrieve system facts from a device."""
    device_info = inventory_manager.get_device(hostname)
    if not device_info:
        console.print(f"[red]Error: Device {hostname} not found in inventory[/red]")
        return
    
    with console.status(f"[bold green]Gathering facts from {hostname}..."):
        facts = Monitor.get_device_facts(device_info)
    
    if facts:
        # Create a table to display the facts
        table = Table(title=f"Device Facts - {hostname}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in facts.items():
            # Handle nested dictionaries or lists
            if isinstance(value, (dict, list)):
                value = str(value)
            table.add_row(key, str(value))
        
        console.print(table)
    else:
        console.print(f"[red]Failed to retrieve facts from {hostname}[/red]")

# --- Template Commands ---

@cli.group()
def template():
    """Manage configuration templates."""
    pass

@template.command("list")
def list_templates():
    """List available configuration templates."""
    templates = template_manager.list_templates()
    
    if not templates:
        console.print("[yellow]No templates available[/yellow]")
        return
    
    table = Table(title="Available Templates")
    table.add_column("Template Name", style="cyan")
    table.add_column("Description", style="green")
    
    for template in templates:
        name = template["name"]
        description = template.get("description", "No description available")
        table.add_row(name, description)
    
    console.print(table)

@template.command("show")
@click.argument("template_name")
def show_template(template_name):
    """Show content of a specific template."""
    content = template_manager.get_template_content(template_name)
    
    if not content:
        console.print(f"[red]Template '{template_name}' not found[/red]")
        return
    
    console.print(Panel(content, title=f"Template: {template_name}", border_style="green"))

if __name__ == "__main__":
    cli()
