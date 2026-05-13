import ipaddress
import netmiko_multihop  # noqa — monkeypatches netmiko ConnectHandler with jump_to/jump_back
from netmiko import ConnectHandler, SSHDetect, exceptions
from multiprocessing.dummy import Pool as ThreadPool
import logging

username = ''
password = ''
devices = []


def _make_jh_dict(jumphost):
    return {
        'device_type': 'linux',
        'ip': jumphost.ip_addr,
        'port': jumphost.port,
        'username': jumphost.username,
        'password': jumphost.password,
    }


def delete_device():
    global devices 
    devices = []
    return

def ssh_worker(IPdict):
    '''Logs in to Devices and try to get Device-Type.
    Add the device to global devices.'''
    from models import network_device
    global username, password, devices
    telnet = IPdict["Telnet"]
    IP = IPdict["IP"]
    jumphost = IPdict.get("Jumphost")
    hostname1 = ""

    if jumphost:
        _ssh_worker_via_jumphost(IP, jumphost)
        return

    testdevice = {'device_type': "autodetect", 'ip': IP, 'username': username, 'password': password}
    logging.debug(f'get_deviceinfos.ssh_worker. Testdevice: {testdevice}')
    try:
        sshtest = SSHDetect(**testdevice)
        device_type = sshtest.autodetect()
    except exceptions.NetmikoTimeoutException:
        if telnet == True:
            testdevice["device_type"] = 'cisco_ios_telnet'
            try:
                sshtest = ConnectHandler(**testdevice)
                hostname1 = sshtest.find_prompt()
                device_type = 'cisco_ios_telnet'
            except Exception as e:
                print(f"Error while Telnet Login to IP {IP}:\n{e}\n")
                return
        else:
            return
    except Exception as E:
        print(f"Error turing login to IP {IP}:\n{E}\n")
        return
    if device_type is None:
        device_type = 'paloalto_panos'
    try:
        buffer = sshtest.initial_buffer
        logging.debug(f'Buffer from initial login {buffer}')
        hostname = buffer.split('\n')[-1][:-1]
    except AttributeError:
        hostname = hostname1
    except Exception as e:
        print(f'Error: Could not get Hostname from initial Device-discovery!')
    if hostname1 != "":
        hostname = hostname1
    if device_type == 'paloalto_panos':
        testdevice['device_type'] = 'paloalto_panos'
        ssh = ConnectHandler(**testdevice)
        hostname = ssh.find_prompt()
        hostname = hostname.split('@')[1][:-1]
        if '(active)' in hostname:
            hostname = hostname.replace('(active)', '')
        elif 'passive' in hostname:
            hostname = hostname.replace('(passive)', '')
        elif 'suspend' in hostname:
            hostname = hostname.replace('(suspend)', '')
    if device_type == "cisco_asa":
        hostname = hostname[:-1]
        if "/" in hostname:
            hostname = hostname.replace("/", "_")
    if device_type == "hp_comware":
        hostname = hostname[1:]
    if hostname[-1] == "#":
        hostname = hostname[:-1]
    device = network_device(name=hostname, ip_addr=IP, username=username, password=password,
                            dev_id=1, enabled=True, type=device_type, connected=True)
    logging.debug(f'get_deviceinfos.ssh_worker. hostname = {hostname}, Type = {device_type}')
    devices.append(device)
    logging.debug(f'get_deviceinfos.ssh_worker. Device: {device.name} with IP: {device.ip_addr} added')


_JH_TIMEOUT = 10   # seconds — applied to every blocking call in the jumphost path


def _ssh_worker_via_jumphost(IP, jumphost):
    '''Discovery via netmiko_multihop.
    Step 1: connect to jumphost (netmiko_multihop ConnectHandler).
    Step 2: reuse that session's paramiko transport to open a direct-tcpip
            channel to the target — feed it into SSHDetect for proper autodetect.
    Step 3: jump_to the target with the detected device_type to read the hostname.'''
    from models import network_device
    global username, password, devices

    # Step 1 — connect to jumphost (with timeout so unreachable host doesn't block)
    try:
        jh_session = ConnectHandler(**_make_jh_dict(jumphost),
                                    timeout=_JH_TIMEOUT, auth_timeout=_JH_TIMEOUT)
    except Exception as e:
        print(f"Error connecting to jumphost {jumphost.ip_addr}:{jumphost.port}:\n{e}\n")
        return

    # Step 2 — autodetect via the jumphost transport (no separate paramiko connection)
    try:
        transport = jh_session.remote_conn_pre.get_transport()
        # open_channel timeout prevents blocking on unreachable targets
        sock = transport.open_channel('direct-tcpip', (IP, 22), ('', 0),
                                      timeout=_JH_TIMEOUT)
        sock.settimeout(_JH_TIMEOUT)
        sshtest = SSHDetect(device_type='autodetect', ip=IP,
                            username=username, password=password, sock=sock,
                            timeout=_JH_TIMEOUT, auth_timeout=_JH_TIMEOUT)
        device_type = sshtest.autodetect()
    except Exception as e:
        print(f"No SSH on {IP} via jumphost: {e}")
        try:
            jh_session.disconnect()
        except Exception:
            pass
        return

    if device_type is None:
        device_type = 'paloalto_panos'

    # Step 3 — jump to target with the detected type to read hostname
    hostname = IP  # fallback
    try:
        jh_session.jump_to(device_type=device_type, ip=IP,
                           username=username, password=password,
                           timeout=_JH_TIMEOUT, auth_timeout=_JH_TIMEOUT)
        hostname = jh_session.find_prompt()
        if device_type == 'paloalto_panos':
            hostname = hostname.split('@')[1][:-1]
            for tag in ('(active)', '(passive)', '(suspend)'):
                hostname = hostname.replace(tag, '')
        elif device_type == 'cisco_asa':
            hostname = hostname[:-1]
            hostname = hostname.replace('/', '_')
        elif device_type == 'hp_comware':
            hostname = hostname[1:]
        else:
            if hostname.endswith('#') or hostname.endswith('>'):
                hostname = hostname[:-1]
    except Exception as e:
        print(f"Error reading hostname via jumphost from {IP}:\n{e}\n")

    device = network_device(name=hostname, ip_addr=IP, username=username, password=password,
                            dev_id=1, enabled=True, type=device_type, connected=True,
                            use_jumphost=True, jumphost=jumphost)
    logging.debug(f'get_deviceinfos._ssh_worker_via_jumphost. hostname={hostname}, type={device_type}')
    devices.append(device)
    try:
        jh_session.jump_back()
        jh_session.disconnect()
    except Exception:
        pass
    

def ssh_login(ip_network, user, passwd, telnet, jumphost=None):
    ''' try to login with Netmiko and detect Device'''
    global username, password, devices
    username = user
    password = passwd
    ip_list = []

    for addr in ipaddress.IPv4Network(ip_network).hosts():
        IP = {}
        ip = str(addr)
        IP["IP"] = ip
        IP["Telnet"] = telnet
        IP["Jumphost"] = jumphost
        ip_list.append(IP)

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

