"""
Device simulator module for the Network Device Management tool.

This module provides simulation capabilities for testing without real devices.
"""
import os
import json
import yaml
import re
import time
from pathlib import Path

class DeviceSimulator:
    """Simulates network device responses for testing."""
    
    def __init__(self, simulation_dir="demo/simulations"):
        """Initialize with the simulation directory."""
        self.simulation_dir = simulation_dir
        self._ensure_dir_exists()
        self.responses = self._load_simulations()
    
    def _ensure_dir_exists(self):
        """Ensure simulation directory exists."""
        os.makedirs(self.simulation_dir, exist_ok=True)
        
        # Create default responses if none exist
        default_file = os.path.join(self.simulation_dir, "default_responses.yml")
        if not os.path.exists(default_file):
            with open(default_file, 'w') as f:
                yaml.dump(self._get_default_responses(), f, default_flow_style=False)
    
    def _load_simulations(self):
        """Load all simulation response files."""
        responses = {}
        for file_path in Path(self.simulation_dir).glob('*.yml'):
            with open(file_path, 'r') as f:
                try:
                    data = yaml.safe_load(f)
                    responses.update(data)
                except Exception as e:
                    print(f"Error loading simulation file {file_path}: {str(e)}")
        
        return responses
    
    def _get_default_responses(self):
        """Get default simulation responses."""
        return {
            "cisco_ios": {
                "show version": """Cisco IOS Software, C2900 Software (C2900-UNIVERSALK9-M), Version 15.7(3)M2, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2018 by Cisco Systems, Inc.
Compiled Wed 01-Aug-18 16:45 by prod_rel_team

ROM: System Bootstrap, Version 15.0(1r)M15, RELEASE SOFTWARE (fc1)

demo-router1 uptime is 1 day, 2 hours, 5 minutes
System returned to ROM by power-on
System restarted at 12:05:33 UTC Mon Jan 1 2023
System image file is "flash:c2900-universalk9-mz.SPA.157-3.M2.bin"
Last reload type: Normal Reload
Last reload reason: power-on""",
                "show clock": "12:05:33.000 UTC Mon Jan 1 2023",
                "show interfaces": """GigabitEthernet0/0 is up, line protocol is up 
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
                "show ip interface brief": """Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0         10.0.0.1        YES NVRAM  up                    up      
GigabitEthernet0/1         192.168.1.1     YES NVRAM  up                    up      
GigabitEthernet0/2         unassigned      YES NVRAM  administratively down down    
Loopback0                  1.1.1.1         YES NVRAM  up                    up""",
                "show running-config": """Building configuration...

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
            "junos": {
                "show version": """Hostname: demo-juniper1
Model: srx300
JUNOS Software Release [20.2R1.10]"""
            },
            "arista_eos": {
                "show version": """Arista DCS-7280SE-68-F
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
    
    def get_response(self, device_type, command):
        """
        Get a simulated response for a command on a specific device type.
        
        Args:
            device_type (str): Type of device (e.g., 'cisco_ios', 'junos')
            command (str): Command to execute
            
        Returns:
            str: Simulated command output
        """
        # Check if we have responses for this device type
        if device_type not in self.responses:
            return f"Simulation error: No responses available for device type '{device_type}'"
        
        # Check for exact command match
        if command in self.responses[device_type]:
            return self.responses[device_type][command]
        
        # Try to find partial matches (commands that start with the given string)
        for cmd, response in self.responses[device_type].items():
            if cmd.startswith(command) or command.startswith(cmd):
                return response
        
        # No match found
        return f"% Invalid command"
    
    def simulate_connection(self, device_info):
        """
        Simulate a connection to a device and check if it's reachable.
        
        Args:
            device_info (dict): Device information
            
        Returns:
            tuple: (status_bool, response_time_ms)
        """
        # Simulate a random response time between 10-50ms
        import random
        response_time = random.uniform(10.0, 50.0)
        
        # 90% chance of success for demo purposes
        success = random.random() < 0.9
        
        return success, response_time