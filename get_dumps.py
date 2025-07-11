COMMANDS = ["show clock",
            "show version",
            "show running",
            "show inventory",
            "show cdp neighbors detail",
            "show ip interface brief",
            "show interfaces",
            "show interface trunk",
            "show interfaces status",
            "show interface switchport",
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
            "show ip dhcp shooping",
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
                 "show neighbor interface all | match REACHABLE",
                 "show routing route",
                 "show config running",
                 "show global-protect-gateway current-user",
                 "show global-protect-gateway previous-user",
                 "show global-protect-gateway statistics",
                 "show session meter",
                 "show counter interface all",
                 "show user ip-user-mapping all | except unknown",
                 "show dos-block-table all",
                 "show counter global",
                 "show system state | match sys.s1.p*"
                 ]

PALO_XML_API =["/api/?type=op&cmd=<show><system><info></info></system></show>",
               "/api/?type=op&cmd=<show><interface>all</interface></show>",
               "/api/?type=op&cmd=<show><interface>logical</interface></show>",
               "/api/?type=op&cmd=<show><arp><entry name = 'all'/></arp></show>",
               "/api/?type=op&cmd=<show><neighbor><interface></interface></neighbor></show>",
               "/api/?type=op&cmd=<show><routing><route></route></routing></show>",
               "/api/?type=op&cmd=<show><global-protect-gateway><current-user></current-user></global-protect-gateway></show>",
               "/api/?type=op&cmd=<show><global-protect-gateway><previous-user></previous-user></global-protect-gateway></show>",
               "/api/?type=op&cmd=<show><global-protect-gateway><statistics></statistics></global-protect-gateway></show>",
               "/api/?type=op&cmd=<show><session><meter></meter></session></show>",
               "/api/?type=op&cmd=<show><high-availability><all></all></high-availability></show>"]

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

WLC_9800_COMMANDS = ["show ap summary",
    "show ap summary sort descending client-count",
    "show ap cdp neighbors",
    "show ap lldp neighbors",
    "show ap dot11 24ghz summary",
    "show ap dot11 5ghz summary",
    "show ap dot11 6ghz summary",
    "show ap auto-rf dot11 24ghz",
    "show ap auto-rf dot11 5ghz",
    "show ap auto-rf dot11 6ghz",
    "show ap name <ap_name> inventory",
    "show ap name <ap_name> tag detail",
    "show ap name <ap_name> config general",
    "show ap name <ap_name> config dot11 24ghz",
    "show ap name <ap_name> config dot11 5ghz",
    "show ap name <ap_name> config dot11 6ghz",
    "show ap name <ap_name> config dot11 dual-band",
    "show ap name <ap_name> channel",
    "show ap name <ap_name> gps location",
    "show chassis",
    "show wireless stats ap history",
    "show wireless client summary",
    "show wireless client mac-address <client_mac> detail",
    "show wlan summary",
    "show wlan id <wlan_id>",
    "show wlan id <wlan_id> client stats"]

from netmiko import ConnectHandler
import logging

OUTPUT_DIR='./dump'

def set_panos_output_xml(ssh_session):
    command_xml='set cli op-command-xml-output on'
    ssh_session.send_command_timing(command_xml)

def _get_template_dir():
    import os, sys
    import subprocess
    try:
        template_dir = os.environ.get("NTC_TEMPLATES_DIR")
    except Exception: UnboundLocalError
    if template_dir is None:
        pip_installed=subprocess.run([sys.executable, '-m', 'pip', 'show', 'ntc-templates'], capture_output=True, text=True)
        for line in pip_installed.stdout.splitlines():
            if line.split(" ")[0] == "Location:":
                site_path= line.split(" ")[1]   
        template_dir = os.path.join(site_path, "ntc_templates", "templates")
    return template_dir

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
                if command == "show version":
                    if "C9800_IOSXE-K9" in commandoutput:
                        wlc_enabled = True
                        logging.debug('get_dumps:dump_cisco_ios: WLC enabled')  
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
            if wlc_enabled:
                ap_name=[]
                client_mac=[]
                wlan_id=[]
                for command in WLC_9800_COMMANDS:
                    wlccommmand = command
                    if "<ap_name>" in command:
                        for ap in ap_name:
                            wlccommmand = command.replace("<ap_name>", ap)
                            outputfile.write(wlccommmand)
                            outputfile.write("\n")
                            outputfile.write("**"+"-"*40+"**")
                            outputfile.write("\n")
                            commandoutput = ssh_session.send_command(wlccommmand)
                            outputfile.write(commandoutput) 
                            outputfile.write("\n")
                            outputfile.write("*"*40)
                            outputfile.write("\n")
                        continue
                    if "<client_mac>" in command:
                        for mac in client_mac:
                            wlccommmand = command.replace("<client_mac>", mac)
                            outputfile.write(wlccommmand)
                            outputfile.write("\n")
                            outputfile.write("**"+"-"*40+"**")
                            outputfile.write("\n")
                            commandoutput = ssh_session.send_command(wlccommmand)
                            outputfile.write(commandoutput) 
                            outputfile.write("\n")
                            outputfile.write("*"*40)
                            outputfile.write("\n") 
                        continue
                    if "<wlan_id>" in command:
                        for id in wlan_id:
                            wlccommmand = command.replace("<wlan_id>", id)
                            outputfile.write(wlccommmand)
                            outputfile.write("\n")
                            outputfile.write("**"+"-"*40+"**")
                            outputfile.write("\n")
                            commandoutput = ssh_session.send_command(wlccommmand)
                            outputfile.write(commandoutput) 
                            outputfile.write("\n")
                            outputfile.write("*"*40)
                            outputfile.write("\n")  
                        continue
                    if command == "show ap summary":
                        ap_output = ssh_session.send_command(command)
                        for line in ap_output.split("\n"):
                            if "Name" in line:
                                continue
                            ap_name.append(line.split(" ")[0]) 
                    if command == "show wireless client summary":
                        client_output = ssh_session.send_command(command)
                        for line in client_output.split("\n"):
                            if "MAC" in line:
                                continue
                            client_mac.append(line.split(" ")[0])
                    if command == "show wlan summary":
                        wlan_output = ssh_session.send_command(command)
                        for line in wlan_output.split("\n"):
                            if "ID" in line:
                                continue
                            wlan_id.append(line.split(" ")[0])  
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
        set_panos_output_xml(ssh_session) # Set the output format to XML for better parsing 
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
    ###############
    # To DO 
    # Make API-Calls 
    # Create API Key and generte Json Output from XML Return
    ##########################
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

def dump_with_textfsm(device): # get commands from NTC-Templates and dump these.
    from textfsm import clitable
    template_dir = _get_template_dir()
    with open(f"{template_dir}\index") as f:
        ntc_index=f.read()
    TEXTFSM_commands=[]
    try:
        dev_vendor = device["device_type"].split("_")[0]
        dev_os = device["device_type"].split("_")[1]
    except Exception as e:
        logging.debug(f'get_dumps.dump_with_textfsm: Something went wrong with Device, {device}')
        logging.debug(e)
        return
    for line in ntc_index.splitlines():
        ntc_vendor = line.split("_")[0]
        if ntc_vendor == dev_vendor:
            ntc_os = line.split("_")[1]
            if ntc_os == dev_os:
                vendor_command=line.split(".")[0]
                parts = vendor_command.split("_")
                command = " ".join(parts[2:])
                TEXTFSM_commands.append(command)
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_with_textfsm: Something went wrong when connecting Device')
        logging.debug(e)
    hostfilename = hostname +"_command.txt"
    try:
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n")  
            for command in TEXTFSM_commands:
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
        logging.debug('get_dumps.dump_with_textfsm: Somthing went wrong with sending commands')
        logging.debug(e)
    return

def dump_worker(device): # Main Thread get device infos
    if not device.enabled:
        return
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
    else:
        dump_with_textfsm(dump_device)
    return

