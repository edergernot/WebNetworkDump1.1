import ipaddress
from netmiko import ConnectHandler, SSHDetect 
from multiprocessing.dummy import Pool as ThreadPool
import logging

username = ''
password = ''
devices = []

def delete_device():
    global devices 
    devices = []
    return

def ssh_worker(IP):
    '''Logs in to Devices and try to get Device-Type
    Add the device to global devices'''
    from models import network_device
    global username, password, devices
    testdevice = {'device_type':"autodetect", 'ip':IP, 'username':username, 'password':password}
    logging.debug(f'get_deviceinfos.ssh_worker. Testdevice: {testdevice}')
    try:
        sshtest = SSHDetect(**testdevice)
        device_type = sshtest.autodetect()
    except Exception as E:
        print (f"Error turing login to IP {IP}:\n{E}\n")
        return
    if device_type == None:
        device_type == 'paloalto_panos'
    buffer = sshtest.initial_buffer
    logging.debug(f'Buffer from initial login {buffer}')
    try:
        hostname = buffer.split('\n')[-1][:-1]
    except Exception as e:
        print (f'Error: Could not get Hostname from initial Device-discovery!')
    if device_type == 'paloalto_panos':  #remove HA - State from Prompt
        testdevice['device_type']='paloalto_panos'
        ssh = ConnectHandler(**testdevice)
        hostname=ssh.find_prompt()
        hostname = hostname.split('@')[1][:-1]
        if '(active)' in hostname:
            hostname = hostname.replace('(active)', '')
        elif ('passive') in hostname:
            hostname = hostname.replace('(passive)', '')
        elif ('suspend') in hostname:
            hostname = hostname.replace('(suspend)')
    if device_type == "cisco_asa":
        hostname=hostname[:-1]
        if "/" in hostname:
            hostname=hostname.replace("/", "_")
    if device_type == "hp_comware":
        hostname=hostname[1:]
    device = network_device(name=hostname, ip_addr=IP, username=username, password=password, 
                            dev_id=1, enabled=True, type=device_type, connected=True)
    logging.debug(f'get_deviceinfos.ssh_worker. hostname = {hostname}, Type = {device_type}')
    devices.append(device)
    logging.debug(f'get_deviceinfos.ssh_worker. Device: {device.name} with IP: {device.ip_addr} added')
    

def ssh_login(ip_network, user, passwd):
    ''' try to login with Netmiko and detect Device'''
    global username, password, devices
    username = user
    password = passwd
    ip_list=[]
   
    for addr in ipaddress.IPv4Network(ip_network).hosts():
        ip = str(addr)
        ip_list.append(ip)
    logging.debug(f'get_deviceinfos.ssh_login: Ip-Adresses to login: {ip_list}')
    if len(ip_list) > 50:
        number_workers = 50
    else:
        number_workers = len(ip_list)
    threads = ThreadPool(number_workers)
    threads.map (ssh_worker, ip_list )
    threads.close()
    threads.join()

    logging.debug(f'get_deviceinfos.ssh_login. Devices to add : {devices}')
    return (devices)

