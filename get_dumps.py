COMMANDS = ["show clock",
            "show version",
            "show running",
            "show inventory",
            "show cdp neighbors detail",
            "show ip interface brief",
            "show interfaces",
            "show interface trunk",
            "show interfaces status",
            "show etherchannel summary",
            "show mac address-table",
            "show ip route",
            "show arp",
            "show access-lists",
            "show ip arp",
            "show ip protocols",
            "show ip route",
            "show ipv6 route",
            "show ipv6 neighbors",
            "show ip mroute",
            "show power inline",
            "show standby all",
            "show ip vrf",
            "show lldp",
            "show lldp neighbors detail",
            "show processes cpu history",
            "show ip pim interface",
            "show ip pim neighbor",
            "show ntp associations",
            "show ntp status",
            "show environment",
            "show environment all",
            "show environment power",
            "show environment temperature",
            "show spanning-tree",
            "show spanning-tree detail",
            "show license all",
            "show stormcontroll",
            "show vlan",
            "show vtp status",
            "show vtp password",
            "show mka summary",
            "show authentication sessions",
            ]

VRF_COMMANDS = ["show ip route vrf <VRF>",
                "show ipv6 route vrf <VRF>",
                "show ip mroute vrf <VRF>",
                "show ip arp vrf <VRF>",
                "show ip protocols vrf <VRF>",
                ]

NX_COMMANDS = ["show vpc",
               "show port-channel summary",
               "show fex",
               "show interface",
               "show interface status",
               ]

PALO_COMMANDS = ["show system info",
                 "show interface all",
                 "show interface logical",
                 "show arp all",
                 "show neighbor interface all",
                 "show routing route",
                 "show config running",
                 "show global-protect-gateway current-user",
                 "show global-protect-gateway previous-user",
                 "show global-protect-gateway statistics",
                 "show session meter",
                 ]

ASA_COMMANDS = ["show clock",
            "show version",
            "show running",
            "show inventory",
            "show interface detail",
            "show interface",
            "show route",
            "show ospf",
            "show ospf neighbor",
            "show bgp summary",
            "show arp",
            "show vpn-sessiondb",
            "show vpn-sessiondb detail l2l",
            "show vpn-sessiondb anyconnect",
            "show failover",
            "show asp drop",
            "show name",
            "show xlate",
            "show running-config object network",
            "show ipv6 route",
            "show ipv6 neighbor",
            "show ipv6 ospf",
            "show flash"
            ]

HP_COMWARE_COMMANDS = ["display clock",
                       "display version",
                       "display current-configuration",
                       "display interface",
                       "display device manuinfo",
                       "display interface",
                       "display ip interface",
                       "display display ip routing-table",
                       "display link-aggregation verbose",
                       "display lldp neighbor-information verbose",
                       "display vlan all",
                       "display mac-address",
                       "display stp",
                       "display counters inbound interface",
                       "display counters outbound interface",
                       "display environment",
                       ""
                       ]

from netmiko import ConnectHandler
import logging

OUTPUT_DIR='./dump'


def make_netmiko_device(device):
    netmiko_device={}
    netmiko_device['device_type']=device.type
    netmiko_device['host']=device.ip_addr
    netmiko_device['username']=device.username
    netmiko_device['password']=device.password
    netmiko_device['hostname']=device.name
    return (netmiko_device)

def dump_cisco_ios(device): 
    vrf_enabled = False
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_cisco_ios: Something went wrong when connecting Device')
        logging.debug(e)
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n")  
            for command in COMMANDS:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command_timing(command)
                if command == "show ip vrf":
                    if len(commandoutput.split("\n")) >= 2:
                        vrf_enabled = True
                        vrf_output = commandoutput
                        logging.debug('get_dumps:dump_cisco_ios: VRF enabled')
                outputfile.write(commandoutput) 
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
            if vrf_enabled:
                vrfs=[]
                logging.debug(f'get_dumps.dump_cisco_ios: VRF Output\n {vrf_output}')
                for line in vrf_output.split("\n"):
                    if line.split(" ")[0] == "Name":
                        continue
                    if line[4] == " ":
                        continue
                    vrf = line.split(" ")[2]
                    vrfs.append(vrf)
                for vrf in vrfs:
                    for command in VRF_COMMANDS:
                        command_vrf = command.replace("<VRF>", vrf)
                        outputfile.write(command_vrf)
                        outputfile.write("\n")
                        outputfile.write("**"+"-"*40+"**")
                        outputfile.write("\n")
                        commandoutput = ssh_session.send_command(command_vrf)
                        outputfile.write(commandoutput) 
                        outputfile.write("\n")
                        outputfile.write("*"*40)
                        outputfile.write("\n")
    except Exception as e:
        logging.debug('get_dumps.dump_cisco_ios: Somthing went wrong with sending commands')
        logging.debug(e)
    return

def dump_cisco_nxos(device):
    vrf_enabled = False
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    logging.debug(f'get_dumps.dump_cisco_nxos: ')
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_cisco_nxos: Something went wrong when connecting Device')
        logging.debug(e)
        return
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n") 
            for command in COMMANDS:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command_timing(command)
                if command == "show ip vrf":
                    if len(commandoutput.split("\n")) >= 2:
                        vrf_enabled = True
                        vrf_output = commandoutput
                        logging.debug('get_dumps:dump_cisco_nxos: VRF enabled')
                outputfile.write(commandoutput) 
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
            if vrf_enabled:
                vrfs=[]
                logging.debug(f'get_dumps.dump_cisco_nxos: VRF Output\n {vrf_output}')
                for line in vrf_output.split("\n"):
                    if "Invalid command at" in vrf_output:
                        continue
                    if line.split(" ")[0] == "Name":
                        continue
                    if line[4] == " ":
                        continue
                    vrf = line.split(" ")[2]
                    vrfs.append(vrf)
                if len(vrfs) != 0:
                    for vrf in vrfs:
                        for command in VRF_COMMANDS:
                            command_vrf = command.replace("<VRF>", vrf)
                            outputfile.write(command_vrf)
                            outputfile.write("\n")
                            outputfile.write("**"+"-"*40+"**")
                            outputfile.write("\n")
                            commandoutput = ssh_session.send_command(command_vrf)
                            outputfile.write(commandoutput) 
                            outputfile.write("\n")
                            outputfile.write("*"*40)
                            outputfile.write("\n")
            for command in NX_COMMANDS:
                logging.debug(f'get_dumps.dump_cisco_nxos: NX_Command: {command}\n')
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command(command)
                outputfile.write(commandoutput) 
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
    except Exception as e:
        logging.debug('get_dumps.dump_cisco_nxos: Somthing went wrong with sending commands')
        print (e)
    return

def dump_cisco_asa(device):
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_cisco_asa: Something went wrong when connecting Device')
        logging.debug(e)
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n") 
            for command in ASA_COMMANDS:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command_timing(command)
                outputfile.write(commandoutput)
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
    except Exception as e:
        logging.debug('get_dumps.dump_cisco_asa: Somthing went wrong with sending commands')
        print (e)
    return

def dump_paloalto_panos(device):
    import time
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    try:
        ssh_session = ConnectHandler(**device,)
    except Exception as e:
        logging.debug(f'get_dumps.dump_palo_asa: Something went wrong when connecting Device')
        logging.debug(e)
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n") 
            for command in PALO_COMMANDS:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command_timing(command)
                logging.debug(f'get_dumps.dump_palo Command: {command}')
                logging.debug(f'get_dumps.dump_palo:\n{commandoutput}')
                outputfile.write(commandoutput) 
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
    except Exception as e:
        logging.debug('get_dumps.dump_cisco_asa: Somthing went wrong with sending commands')
        print (e)
    return

def dump_hp_comware(device):
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_hp_comware Something went wrong when connecting Device')
        logging.debug(e)
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n") 
            for command in HP_COMWARE_COMMANDS:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**"+"-"*40+"**")
                outputfile.write("\n")
                commandoutput = ssh_session.send_command_timing(command)
                outputfile.write(commandoutput)
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
    except Exception as e:
        logging.debug('get_dumps.dump_hp_comware: Somthing went wrong with sending commands')
        print (e)
    return

def dump_worker(device): # Main Thread get device infos
    dump_device=make_netmiko_device(device)
    dev_type=dump_device['device_type']
    if dev_type=='cisco_ios':
        dump_cisco_ios(dump_device)
    elif dev_type=='cisco_nxos':
        dump_cisco_nxos(dump_device)
    elif dev_type=='cisco_asa':
        dump_cisco_asa(dump_device)
    elif dev_type=='paloalto_panos':
        dump_paloalto_panos(dump_device)
    elif dev_type=="hp_comware":
        dump_hp_comware(dump_device)
    return

