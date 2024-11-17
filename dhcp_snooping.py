'''Used to enable dhcp-snooping and add Trunkinterfaces to trust on Cisco Switch'''

def configure_dhcpsnooping(ssh_device):
    import time
    import logging
    logging.basicConfig(level=logging.DEBUG) # Needet for debugging
    from netmiko import ConnectHandler
    import logging
    OUTPUT_DIR='./quickcommand'
    trunk_interface=[]
    trunk_config=[]
    global_config=["ip dhcp snooping vlan 1-4090",
                   "ip dhcp snooping information option allow-untrusted",
                   "ip dhcp snooping information option format remote-id hostname",
                   "ip dhcp snooping"]
    hostname = ssh_device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    logging.debug (f'Try to connect to {hostname}')
    dev_type=ssh_device['device_type']
    logging.debug(f'Conneced to Device {hostname}')
    if dev_type != 'cisco_ios':  # only run on Cisco IOS devices
        return
    try:
        ssh_session = ConnectHandler(**ssh_device)
        print (f"Connected to {ssh_session.find_prompt()}, executing DHCP-Snooping")
    except Exception as e:
        logging.debug(f'find_trunk_ports Something went wrong when connecting Device')
        logging.debug(e)
    ### Backup Running Config
    now = time.strftime("%Y%b%d_%H%M", time.localtime())
    backup = ssh_session.send_command_timing(f"copy running flash:Backup_{now}\n")
    ssh_session.send_command_timing(f"\n")
    logging.debug(f"Backing Up running Config:\n{backup}\n")
    ### Get Interfaces
    interfaces_cmd='show interface trunk'
    int_trunk=ssh_session.send_command_timing(interfaces_cmd, use_textfsm=True)
    with open (f"{OUTPUT_DIR}/{hostname}_accessport_cfg.txt", "w") as file:  # Write Logfile
        file.write(f"copy run flash:Backup_{now}\n ")
        file.write(f"{backup}\n")
        lines = int_trunk.split('\n')
        for line in lines:
            if "trunking" in line:
                interface = line.split(' ')[0]
                trunk_interface.append(interface)
        for trunk in trunk_interface:
            trunk_config.append(f"interface {trunk}")
            trunk_config.append("ip dhcp snooping trust") 
        logging.debug(f"Configuring Trunk Interfaces:")
        configure = ssh_session.send_config_set(trunk_config)
        logging.debug(configure)
        file.write(configure)
        logging.debug(f"Configuring dhcp-snooping:")
        configure = ssh_session.send_config_set(global_config)
        logging.debug(configure)
        file.write(configure)

        


if __name__ == "__main__":
    ### Used to run as single App on single Device
    from models import *
    from webnetworkdump import make_netmiko_device
    test_device= network_device(name='testdev', ip_addr='1.1.1.1', username='user', password='pwd',type='cisco_ios',dev_id=1) 
    ssh_device=make_netmiko_device(test_device)
    configure_dhcpsnooping(ssh_device)
