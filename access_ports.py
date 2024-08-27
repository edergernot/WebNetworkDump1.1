'''Used to check interfaces on Cisco Switch, if AccessPort it will do some default configuration
It will not change config, if ist a trunk or routed Interface or member of Portchannnel'''



global_config=['ipv6 nd raguard policy RAGUARD_HOST',  'device-role host']

access_switch_port=['switchport mode access',
                    'spanning-tree portfast',
                    'spanning-tree portfast edge',
                    'spanning-tree bpduguard enable',
                    'storm-control broadcast level 8 6',
                    'storm-control multicast level 8 6',
                    'storm-control action trap',
                    'ipv6 nd raguard attach-policy RAGUARD_HOST',]
access_port_portsec=[
                    'switchport port-security',
                    'switchport port-security maximum 2',
                    'switchport port-security violation restrict',]


def configure_access_ports(ssh_device):
    import time
    import logging
    logging.basicConfig(level=logging.DEBUG)
    from netmiko import ConnectHandler
    import logging
    OUTPUT_DIR='./quickcommand'
    access_interface=[]
    hostname = ssh_device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    logging.debug (f'Try to connect to {hostname}')
    dev_type=ssh_device['device_type']
    logging.debug(f'Conneced to Device {hostname}')
    if dev_type != 'cisco_ios':  # only used on Cisco IOS devices
        return
    try:
        ssh_session = ConnectHandler(**ssh_device)
    except Exception as e:
        logging.debug(f'find_access_ports Something went wrong when connecting Device')
        logging.debug(e)
    now = time.strftime("%Y%b%d_%H%M", time.localtime())
    backup = ssh_session.send_command_timing(f"copy run flash:Backup_{now}")
    logging.debug(f"Backing Up running Config:\n{backup}")
    interfaces_cmd='show interfaces status'
    int_status=ssh_session.send_command_timing(interfaces_cmd, use_textfsm=True) # get interfaces from Switch
    with open (f"{OUTPUT_DIR}/{hostname}_accessport_cfg.txt", "w") as file:
        file.write(f"copy run flash:Backup_{now}\n ")
        file.write(backup)
        # configure global ipv6 RA-Guard
        globalconfig = ssh_session.send_config_set(global_config)
        file.write(globalconfig)
        for int in int_status:
            MacSec = True
            AccessPort = True
            int_name=int['port']
            logging.debug(f"Testing Interface : {int_name}")
            print(f"Testing Interface : {int_name} on device {hostname}")
            if int['vlan']=='trunk':
                continue  ### configured and working as trunk
            if int_name[:2]=='Po':
                continue  #### dont configure Portchannels
            if int_name[:2]=='Vl':
                continue #### dont configure Vlans
            mac_count=ssh_session.send_command_timing(f"show mac address int {int_name}", use_textfsm=True)
            if "\n------------------------" in mac_count:  #'          Mac Address Table\n-------------------------------------------\n\nVlan    Mac Address       Type        Ports\n----    -----------       --------    -----'
                macs=mac_count.split("Ports\n")
                try:
                    mac_addr=macs[1]
                except IndexError:
                    mac_count=["No Entry"]
                try:
                    mac_count=mac_addr.split('\n')
                except Exception as e:
                    print (f"Error: {e}")
            if len(mac_count)>=2:
                MacSec = False  ### Dont enable MAC-sec, more than 2 Addesses found
            #### Get Interface config
            portconfig = ssh_session.send_command_timing(f"show run interface {int_name}")
            file.write(portconfig)
            ### Check Interface config for keywords
            for line in portconfig:
                if "mode trunk" in line:
                    AccessPort=False
                if "channel-group" in line:
                    AccessPort=False
                if "stackwise-virtual" in line:
                    AccessPort=False
                if "ip address" in line:
                    AccessPort=False
                if "no switchport" in line:
                    AccessPort=False
            if AccessPort:
                commands=[]
                interface=f"interface {int_name}"
                commands.append(interface)
                for commandline in access_switch_port:
                    commands.append(commandline)
                if MacSec:
                    for commandline in access_port_portsec:
                        commands.append(commandline)
                access_interface.append(int_name)
                logging.debug(f"Configuring Interface {int_name}")
                configure = ssh_session.send_config_set(commands)
                logging.debug(f"Interface {int_name} configured")
                file.write("-"*40)
                file.write('\n')
                file.write(configure)
                file.write('#'*40)
                file.write('\n')



if __name__ == "__main__":
    ### Used to run al single App on single Device
    from models import *
    from webnetworkdump import make_netmiko_device
    test_device= network_device(name='testdev', ip_addr='1.1.1.1', username='usern', password='password',type='cisco_ios',dev_id=1) 
    ssh_device=make_netmiko_device(test_device)
    configure_access_ports(ssh_device)






