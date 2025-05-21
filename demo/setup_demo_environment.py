#!/usr/bin/env python3
"""
NetMan Demo Setup Script

This script sets up a demo environment for the NetMan tool with sample devices
and templates for testing functionality without real network devices.
"""
import os
import json
import yaml
from pathlib import Path

def setup_demo_environment():
    """Set up the demo environment with sample devices and templates."""
    print("Setting up NetMan demo environment...")
    
    # Ensure directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('configs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('demo/simulations', exist_ok=True)
    os.makedirs('demo/vars', exist_ok=True)
    
    # Create demo inventory
    create_demo_inventory()
    
    # Create demo simulation responses
    create_demo_simulations()
    
    # Create demo variable files
    create_demo_vars()
    
    print("Demo environment setup complete!")

def create_demo_inventory():
    """Create a demo inventory with sample devices."""
    inventory_file = 'data/inventory.json'
    
    demo_devices = [
        {
            "hostname": "demo-router1",
            "ip": "192.168.1.1",
            "device_type": "cisco_ios",
            "username": "admin",
            "password": "admin123",
            "ssh_port": 22,
            "groups": ["demo", "routers"]
        },
        {
            "hostname": "demo-switch1",
            "ip": "192.168.1.2",
            "device_type": "cisco_ios",
            "username": "admin",
            "password": "admin123",
            "ssh_port": 22,
            "groups": ["demo", "switches"]
        },
        {
            "hostname": "demo-aci1",
            "ip": "10.0.0.100",
            "device_type": "cisco_aci",
            "username": "admin",
            "password": "cisco123",
            "ssh_port": 22,
            "groups": ["demo", "aci", "fabric_controllers"],
            "apic_url": "https://10.0.0.100"
        },
        {
            "hostname": "demo-juniper1",
            "ip": "10.0.0.2",
            "device_type": "junos",
            "username": "admin",
            "password": "juniper123",
            "ssh_port": 22,
            "groups": ["demo", "firewalls", "juniper"]
        },
        {
            "hostname": "demo-paloalto1",
            "ip": "10.0.0.3",
            "device_type": "panos",
            "username": "admin",
            "password": "paloalto123",
            "ssh_port": 22,
            "groups": ["demo", "firewalls", "paloalto"]
        }
    ]
    
    with open(inventory_file, 'w') as f:
        json.dump(demo_devices, f, indent=2)
    
    print(f"Created demo inventory with {len(demo_devices)} devices")
    
    # Create Ansible inventory
    ansible_inventory = {
        'all': {
            'children': {
                'network': {
                    'children': {
                        'routers': {
                            'hosts': {
                                'demo-router1': {
                                    'ansible_host': '192.168.1.1',
                                    'ansible_network_os': 'ios',
                                    'ansible_user': 'admin',
                                    'ansible_password': 'admin123'
                                }
                            }
                        },
                        'switches': {
                            'hosts': {
                                'demo-switch1': {
                                    'ansible_host': '192.168.1.2',
                                    'ansible_network_os': 'ios',
                                    'ansible_user': 'admin',
                                    'ansible_password': 'admin123'
                                }
                            }
                        },
                        'aci': {
                            'hosts': {
                                'demo-aci1': {
                                    'ansible_host': '10.0.0.100',
                                    'ansible_network_os': 'aci',
                                    'ansible_user': 'admin',
                                    'ansible_password': 'cisco123',
                                    'apic_host': '10.0.0.100',
                                    'apic_use_proxy': 'no',
                                    'apic_validate_certs': 'no'
                                }
                            }
                        },
                        'juniper': {
                            'hosts': {
                                'demo-juniper1': {
                                    'ansible_host': '10.0.0.2',
                                    'ansible_network_os': 'junos',
                                    'ansible_user': 'admin',
                                    'ansible_password': 'juniper123',
                                    'ansible_connection': 'netconf'
                                }
                            }
                        },
                        'paloalto': {
                            'hosts': {
                                'demo-paloalto1': {
                                    'ansible_host': '10.0.0.3',
                                    'ansible_network_os': 'panos',
                                    'ansible_user': 'admin',
                                    'ansible_password': 'paloalto123'
                                }
                            }
                        },
                        'firewalls': {
                            'children': {
                                'juniper': {},
                                'paloalto': {}
                            }
                        }
                    }
                }
            }
        }
    }
    
    with open('data/ansible_inventory.yml', 'w') as f:
        yaml.dump(ansible_inventory, f)
    
    print("Created demo Ansible inventory")

def create_demo_simulations():
    """Create simulation responses for demo devices."""
    # Load existing simulations for Cisco IOS and other devices
    simulations_file = 'demo/simulations/default_responses.yml'
    
    # Now add Cisco ACI responses
    aci_simulations_file = 'demo/simulations/cisco_aci_responses.yml'
    
    # Basic simulation responses
    simulations = {
        'cisco_ios': {
            'show version': """Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.7(3)M2, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Wed 01-Aug-18 16:45 by prod_rel_team

ROM: System Bootstrap, Version 15.0(1r)M15, RELEASE SOFTWARE (fc1)

demo-router1 uptime is 1 day, 2 hours, 5 minutes
System returned to ROM by power-on
System restarted at 12:05:33 UTC Mon Jan 1 2023
System image file is "flash:c2900-universalk9-mz.SPA.157-3.M2.bin"
Last reload type: Normal Reload
Last reload reason: power-on

Processor board ID FTX1234ABCD
1 Gigabit Ethernet interface
1 Virtual Private Network (VPN) Module
256K bytes of non-volatile configuration memory.
512MB of DRAM Memory

License Info:
License UDI:
-------------------------------------------------
Device#   PID                   SN
-------------------------------------------------
*0        CISCO2901/K9          FTX1234ABCD      

Technology Package License Information for Module:'c2900' 
----------------------------------------------------------------
Technology     Technology-package          Technology-package
               Current            Type     Next reboot
----------------------------------------------------------------
ipbase         ipbasek9            Permanent  ipbasek9
security       securityk9          Permanent  securityk9
uc             None                None       None
data           None                None       None

Configuration register is 0x2102""",
            'show clock': "12:05:33.000 UTC Mon Jan 1 2023",
            'show interfaces': """GigabitEthernet0/0 is up, line protocol is up 
  Hardware is CN Gigabit Ethernet, address is aabb.cc00.0100 (bia aabb.cc00.0100)
  Description: WAN Interface
  Internet address is 10.0.0.1/24
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec, 
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full-duplex, 1000Mb/s, media type is RJ45
  output flow-control is off, input flow-control is off
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:05, output 00:00:01, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 25000 bits/sec, 40 packets/sec
  5 minute output rate 21000 bits/sec, 35 packets/sec
     1250 packets input, 125000 bytes, 0 no buffer
     Received 650 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles 
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 650 multicast, 0 pause input
     1150 packets output, 115000 bytes, 0 underruns
     0 output errors, 0 collisions, 1 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out
     
GigabitEthernet0/1 is up, line protocol is up 
  Hardware is CN Gigabit Ethernet, address is aabb.cc00.0101 (bia aabb.cc00.0101)
  Description: LAN Interface
  Internet address is 192.168.1.1/24
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec, 
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full-duplex, 1000Mb/s, media type is RJ45
  output flow-control is off, input flow-control is off
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input 00:00:02, output 00:00:00, output hang never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0
  Queueing strategy: fifo
  Output queue: 0/40 (size/max)
  5 minute input rate 52000 bits/sec, 75 packets/sec
  5 minute output rate 48000 bits/sec, 70 packets/sec
     2500 packets input, 250000 bytes, 0 no buffer
     Received 1200 broadcasts (0 IP multicasts)
     0 runts, 0 giants, 0 throttles 
     0 input errors, 0 CRC, 0 frame, 0 overrun, 0 ignored
     0 watchdog, 1200 multicast, 0 pause input
     2300 packets output, 230000 bytes, 0 underruns
     0 output errors, 0 collisions, 0 interface resets
     0 unknown protocol drops
     0 babbles, 0 late collision, 0 deferred
     0 lost carrier, 0 no carrier, 0 pause output
     0 output buffer failures, 0 output buffers swapped out""",
            'show ip interface brief': """Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.1        YES NVRAM  up                    up      
GigabitEthernet0/1         192.168.1.1     YES NVRAM  up                    up      
GigabitEthernet0/2         unassigned      YES NVRAM  administratively down down    
Loopback0                  1.1.1.1         YES NVRAM  up                    up""",
            'show running-config': """Building configuration...

Current configuration : 1782 bytes
!
! Last configuration change at 12:05:33 UTC Mon Jan 1 2023
!
version 15.7
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname demo-router1
!
boot-start-marker
boot-end-marker
!
!
enable secret 5 $1$demo$cGBKMa8pVS.wcZ6EwBj3R1
!
no aaa new-model
!
!
!
ip domain name demo.local
ip cef
no ipv6 cef
!
!
!
username admin privilege 15 secret 5 $1$demo$F7BFhvKjm5kEcYLes3OKo1
!
!
!
interface GigabitEthernet0/0
 description WAN Interface
 ip address 10.0.0.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 description LAN Interface
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/2
 no ip address
 shutdown
 duplex auto
 speed auto
!
!
router ospf 1
 network 10.0.0.0 0.0.0.255 area 0
 network 192.168.1.0 0.0.0.255 area 0
!
ip forward-protocol nd
!
!
no ip http server
no ip http secure-server
!
!
!
!
snmp-server community demopublic RO
snmp-server contact Demo Admin
snmp-server location Demo Lab
!
!
!
line con 0
 logging synchronous
line aux 0
line vty 0 4
 transport input ssh
 login local
!
ntp server 10.0.0.10
ntp server 10.0.0.11
!
end"""
        },
        'junos': {
            'show version': """Hostname: demo-juniper1
Model: srx300
JUNOS Software Release [20.2R1.10]"""
        },
        'arista_eos': {
            'show version': """Arista DCS-7280SE-68-F
Hardware version: 01.00
Serial number: ABC12345678
System MAC address: 001c.1234.5678

Software image version: 4.22.1F
Architecture: i386
Internal build version: 4.22.1F-12345678.42211F
Internal build ID: 58fde4bc-f991-4810-b717-d670e436da94

Uptime: 1 day, 2 hours and 5 minutes
Total memory: 8051592 kB
Free memory: 5337688 kB"""
        }
    }
    
    with open(simulations_file, 'w') as f:
        yaml.dump(simulations, f, sort_keys=False)
    
    print("Created demo simulation responses")

def create_demo_vars():
    """Create variable files for device configurations."""
    # Router variables
    router_vars = {
        'hostname': 'demo-router1',
        'domain_name': 'demo.local',
        'enable_secret': 'demo-enable',
        'username': 'admin',
        'password': 'admin123',
        'interfaces': [
            {
                'name': 'GigabitEthernet0/0',
                'description': 'WAN Interface',
                'ip': '10.0.0.1',
                'netmask': '255.255.255.0',
                'shutdown': False
            },
            {
                'name': 'GigabitEthernet0/1',
                'description': 'LAN Interface',
                'ip': '192.168.1.1',
                'netmask': '255.255.255.0',
                'shutdown': False
            }
        ],
        'routing': True,
        'ospf': {
            'process_id': 1,
            'networks': [
                {
                    'address': '10.0.0.0',
                    'wildcard': '0.0.0.255',
                    'area': 0
                },
                {
                    'address': '192.168.1.0',
                    'wildcard': '0.0.0.255',
                    'area': 0
                }
            ]
        },
        'ntp_servers': [
            '10.0.0.10',
            '10.0.0.11'
        ],
        'syslog_servers': [
            '10.0.0.20'
        ],
        'logging_source_interface': 'GigabitEthernet0/0',
        'snmp_community': 'demopublic',
        'snmp_contact': 'Demo Admin',
        'snmp_location': 'Demo Lab',
        'banner': 'Welcome to NetMan Demo Router!\nAuthorized access only.'
    }
    
    with open('demo/vars/demo-router1.yml', 'w') as f:
        f.write('---\n# Demo variable file for demo-router1\n\n')
        yaml.dump(router_vars, f, sort_keys=False)
    
    # Switch variables
    switch_vars = {
        'hostname': 'demo-switch1',
        'domain_name': 'demo.local',
        'enable_secret': 'demo-enable',
        'username': 'admin',
        'password': 'admin123',
        'interfaces': [
            {
                'name': 'GigabitEthernet0/0',
                'description': 'Uplink Interface',
                'ip': '192.168.1.2',
                'netmask': '255.255.255.0',
                'shutdown': False
            },
            {
                'name': 'GigabitEthernet0/1',
                'description': 'Access Port',
                'switchport': True,
                'mode': 'access',
                'vlan': 10,
                'shutdown': False
            },
            {
                'name': 'GigabitEthernet0/2',
                'description': 'Trunk Port',
                'switchport': True,
                'mode': 'trunk',
                'allowed_vlans': '10,20,30',
                'native_vlan': 1,
                'shutdown': False
            }
        ],
        'vlans': [
            {
                'id': 10,
                'name': 'DATA'
            },
            {
                'id': 20,
                'name': 'VOICE'
            },
            {
                'id': 30,
                'name': 'MGMT'
            }
        ],
        'routing': False,
        'ntp_servers': [
            '10.0.0.10'
        ],
        'syslog_servers': [
            '10.0.0.20'
        ],
        'logging_source_interface': 'GigabitEthernet0/0',
        'snmp_community': 'demopublic',
        'snmp_contact': 'Demo Admin',
        'snmp_location': 'Demo Lab',
        'banner': 'Welcome to NetMan Demo Switch!\nAuthorized access only.'
    }
    
    with open('demo/vars/demo-switch1.yml', 'w') as f:
        f.write('---\n# Demo variable file for demo-switch1\n\n')
        yaml.dump(switch_vars, f, sort_keys=False)
    
    print("Created demo variable files")

if __name__ == "__main__":
    setup_demo_environment()