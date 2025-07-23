from models import network_device
from netmiko import ConnectHandler, SSHDetect
import os
from flask import Flask, render_template, flash, url_for, redirect, send_file, request
from werkzeug.utils import secure_filename
from wtforms.form import FormMeta
from wtforms.validators import HostnameValidation
from forms import DeviceDiscoveryForm, QuickCommand, PasswordForm
import ipaddress
import get_deviceinfos
import get_status
import parse_files
from global_init import *
import logging
import shutil
from get_dumps import *
from get_quickcommands import *
from access_ports import *
from dhcp_snooping import *
from multiprocessing.dummy import Pool as ThreadPool
from subprocess import Popen, PIPE
import json
import threading
import base64
from csv import DictWriter
from drawiohelper import *
from pyntc import ntc_device as NTC

############## Logging Level #################
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.ERROR)
##############################################

app = Flask(__name__)
app.config['SECRET_KEY'] = '50421D352F92E548C6AC0147380F58BC'  # used to avoid TCP-Highjacking in Flask
app.config['UPLOAD_FOLDER'] = "./upload"
global_quickcommands = {}

STATUS_FILE = "./upload/status.json"  #used during SW-Upgrade

def start_webssh_server():
    """Start the WebSSH server in a background thread."""
    try:
        command=["wssh", "--fbidhttp=False"]
        Popen(command, stdout=PIPE, stderr=PIPE)
        print(f"WebSSH server started!")
    except FileNotFoundError:
        print("Error: 'wssh' command not found. Ensure WebSSH is installed and in PATH.")
    except Exception as e:
        print(f"Failed to start WebSSH server: {e}")

    # Start the WebSSH server when Flask starts
    # threading.Thread(target=start_webssh_server, daemon=True).start()

def add_to_data(key, parsed, hostname, vrf='NONE'):
    global data
    if key not in data.keys():
        data[key]=[]
    for line in parsed:
        item={}
        item['Devicename']=hostname
        if vrf != 'NONE':
            item['vrf']=vrf
        for k in line.keys():
            item[k]=line[k]
        data[key].append(item)

def check_ip_network(ip_network):
    '''tests if IP-Network is an valid'''
    try:
        ipaddress.IPv4Network(ip_network)
        return (True)
    except:
        return (False)

def write_device_file(devices):
    with open(f'{DUMP_DIR}/device_file.csv', 'w') as dev_file:
        dev_file.write('Name,Type,IP-Address, Username\n')
        for device in devices:
            dev_file.write(f'{device.name},{device.type},{device.ip_addr},{device.username}\n')

def find_type_from_hostname(devices,hostname):
    for device in devices:
        if device.name == hostname:
            return(device.type)

def enabled_devices(devices):
    ena_devices=[]
    for device in devices:
        if device.enabled :
            ena_devices.append(device)
    return(ena_devices)

def test_connectivity():
    global devices
    if len(devices) <= 30 :
        num_threads=len(devices)
    else:
        num_threads=30
    threads = ThreadPool( num_threads )
    results = threads.map( test_logon, devices )
    threads.close()
    threads.join()
    
def test_logon(device):
    global devices
    testdevice =  {'device_type': device.type, 'ip':device.ip_addr, 'username':device.username, 'password':device.password}
    try: 
        ssh_session = ConnectHandler(**testdevice)
        hostname = ssh_session.find_prompt()
        print (f'connected to {hostname}')
    except Exception as E:
        print (f"Error turing login to device: {device.name} {device.ip_addr}:\n{E}\n")
        for dev in devices:
            if dev.ip_addr==device.ip_addr:
                dev.connected = False
                dev.enabled = False
                return
    for dev in devices:
            if dev.ip_addr==device.ip_addr:
                dev.connected = True
    return
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_csv_files(data):
    for key in data.keys():
        filename = f"{DUMP_DIR}/{key}.csv"
        with open(filename,"w",newline='') as output:
            rows = list(data[key])
            if len(rows) == 0:
                continue
            writer = DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            try:
                writer.writerows(rows)
            except Exception as e:
                print(f"Error writing CSV file {key}.csv: {e}")   
                continue
            
def generate_drawio(data):
    from drawio import NetPlot
    import json

    cdpdata = data['cisco_ios--show_cdp_neighbors_detail']
    nodes = []
    links = []

    for line in cdpdata:
        host_exist = False
        node = {}
        link = {}
        local_node = shrink_name(line['Devicename'])
        remote_node = shrink_name(line['destination_host'])
        node['id']=remote_node
        node['type']=line['capabilities'].split(" ")[0] # get the first capability
        link["from"]=local_node
        link["to"]=remote_node
        link["local_port"]=short_portname(line["local_port"])
        link["remote_port"]=short_portname( line["remote_port"])
        links.append(link) 
        for existing_node in nodes:  # check if node allready exist
            if node["id"] == existing_node["id"]:
                host_exist = True
        if not host_exist:
            nodes.append(node)
            host_exist = False

    for line in cdpdata: # Append source Device if not as neigbor in CDP-Data
        node_allready_exist=False
        for node in nodes:
            if line['Devicename'] == node["id"]:
                node_allready_exist = True
                continue
        if not node_allready_exist:
            node["id"]=line["Devicename"]
            node["type"]="Host"
            nodes.append(node)

    links = remove_duplicate_links(links)

    drawio = NetPlot()
    drawio.addNodeList(nodes)
    drawio.addLinkList(links)
    drawio.exportXML('./dump/drawio.xml')
    #print(x.display_xml())

def remove_inactve(device):
    ssh_device=make_netmiko_device(device)
    del ssh_device["hostname"]  #remove the key hostname not needet fopr netmiko connection
    commandlist=[["install remove inactive", r"[y/n]]"],
                 ["y" , ""]] 
    try:        
        ssh_session = ConnectHandler(**ssh_device)
        hostname = ssh_session.find_prompt()[:-1]
        #print (f'connected to {hostname}')
    except Exception as E:
        print (f"Error turing login to device: {device.name} {device.ip_addr}:\n{E}\n")
        return
    with open(f"{OUTPUT_DIR}/{hostname}_remove_inactice.txt", "w") as f:
        try:
            remove = ssh_session.send_multiline(commandlist)  
        except Exception as e: 
            print(f"Error on deleting old images\n ")
            print(e)
        try:
            f.write(remove)
        except Exception as e:
            pass      
    return

def sw_upgrade_devices(device):
    print("sw_upgrade_devices lounched")
    if device.enabled == False:
        return
    file = os.listdir("./upload")
    upgrade_device=make_netmiko_device(device)
    if upgrade_device["device_type"] == "cisco_ios":
        upgrade_device["device_type"] = "cisco_ios_ssh"
    if upgrade_device["device_type"] == "cisco_asa":
        upgrade_device["device_type"] = "cisco_asa_ssh"
    set_upgrade_status("Login to Device ...")
    print("Login to Device ...")
    NTC_device=NTC(**upgrade_device)
    bootoption = NTC_device.get_boot_options()
    install = False
    try:
        if bootoption['sys'] == 'packages.conf':
            install = True
    except Exception as e:
        print(e)
    print("### Debug: Save running config")
    set_upgrade_status("Safe Config ...")
    NTC_device.save()
    if install:
        # Remove inactive Files in Install mode
        set_upgrade_status ("Remove inactive  ...")
        remove_inactve(device)
    print(f"### Debug: Uploading {file[0]} to {device.name} ..")
    set_upgrade_status("Uploading File ...")
    NTC_device.file_copy(f"./upload/{file[0]}")
    print("### Debug: Uploading done")
    set_upgrade_status("Installing Software ...")
    if install:
        NTC_device.install_os(file[0], install_mode=True)
    else:
        NTC_device.install_os(file[0])
        set_upgrade_status("Rebooting Device ...")
        NTC_device.reboot   
    return

@app.route("/")
def index():
    global devices
    content=get_status.get_status(devices)
    return render_template("index.html",status=content)

@app.route("/devicediscovery", methods=['GET', 'POST'])
def devicediscovery():
    global username, password, ip_network, devices
    content=get_status.get_status(devices)
    form = DeviceDiscoveryForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        ip_network=form.ip_network.data
        if not check_ip_network(ip_network):
            flash(f'non valid IPv4 Network: {ip_network}', 'success')
            return redirect(url_for('devicediscovery'))
        else:
            flash(f'Device Discovery is Startet...', 'success')
            return redirect(url_for('discover_loading'))
    return render_template("devicediscovery.html", form=form, title="Device Discovery", status=content)

@app.route("/discover_loading") # shows spinning weel and starts "trylogon"
def discover_loading():
    global ip_network, devices
    content=get_status.get_status(devices)
    NumberHosts = len(list(ipaddress.IPv4Network(ip_network).hosts()))
    logging.debug('webnetworkdump.discover_loading. Number of Hosts in Network: {NumberHosts}')
    return render_template('loading_discover.html', status=content, text=f'One moment please!\nDiscovering {NumberHosts} devices ...')

@app.route("/trylogon")
def trylogon():
    global username, password, ip_network, devices
    content=get_status.get_status(devices)
    login_devices=get_deviceinfos.ssh_login(ip_network, username, password)
    logging.debug(f'webnetworkdump.trylogon. Devices: {login_devices}')
    for device in login_devices:
        exist = False
        for old_device in devices:
            if device.name == old_device.name and device.type == old_device.type:
                logging.debug(f'webnetworkdump.trylogon. Device {device.name} alleady exist')
                exist = True
                break
        if exist == False:
            devices.append(device)
            logging.debug(f'webnetworkdump.trylogon. Device {device.name} addet to Devices')   
    content=get_status.get_status(devices)
    return render_template("index.html",status=content)

@app.route("/device_view", methods=['GET', 'POST'])
def device_view():
    global devices
    if request.method == 'POST':
        # Handle "Test Connectivity" action
        if request.form.get('action') == 'test_connectivity':
            test_connectivity()
        
        if request.form.get('action') == 'sw_upgrade':
            return redirect("/sw_upgrade")

        # Handle "Enable/Disable" toggle for a specific device
        elif request.form.get('action') == 'toggle_device':
            device_ip = request.form.get('device_ip')
            print (f"ENABLE: {device_ip}")
            for device in devices:
                if device.ip_addr == device_ip:
                    device.enabled = not device.enabled  # Toggle enabled status
                    break
        # Handle "Enable All" action
        elif request.form.get('action') == 'enable_all':
            for device in devices:
                device.enabled = True  # Set all devices to enabled
                       
        # Handle "Disable All" action
        elif request.form.get('action') == 'disable_all':
            for device in devices:
                device.enabled = False  # Set all devices to disabled

        # Handle "Export Devices" action
        elif request.form.get('action') == 'export_devices':
            write_device_file(devices)
            output_path = f"{DUMP_DIR}/device_file.csv"
            return send_file(output_path, as_attachment=True)
        
        # Handle "Import Devices" action
        elif request.form.get('action') == 'import_devices':
            return redirect("/upload")

    logging.debug(f'webnetworkdump.device_view. Device-Objects in View: {devices}')
    content=get_status.get_status(devices)
    return render_template("/device_view.html", status=content, devices=devices)

@app.route("/webssh/<string:device_ip>") # Connect to WebSSH-Server on localhost
def webssh(device_ip):
    global devices
    for device in devices:
        if device.ip_addr == device_ip:
            user = device.username
            password = device.password
            pwd = base64.urlsafe_b64encode(password.encode('utf-8'))
            pwd64 = pwd.decode('utf-8')
            webssh_host = request.host.split(':')[0]  
            print(webssh_host)
            webssh_url = f"http://{webssh_host}:8888/?hostname={device_ip}&username={user}&password={pwd64}"
            return redirect(webssh_url)

@app.route("/upload", methods=['GET', 'POST'])
def upload():
    '''Select file for upload and upload it.'''
    content=get_status.get_status(devices)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/upload')
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect('/upload')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # delete Upload Folder
            if os.path.exists("./upload"):
                shutil.rmtree("./upload", ignore_errors=False, onerror=None)
            path = os.path.join("./","upload")
            os.mkdir(path)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/import')
    return render_template("/upload.html",status=content)

@app.route("/dump_loading")
def dump_loading():
    global devices
    content=get_status.get_status(devices)
    return render_template('loading_dump.html', status=content, text=f"Now I dump {content['enableddevices']} devices and parse the receiving data ...")

@app.route("/dump")
def dump():
    global devices, data
    if len(devices) == 0:
        flash('There are no devices to dump. Do the discovery first!', 'success')
        return redirect('devicediscovery')
    # delete directory if old dumps exist and create new dir
    if os.path.exists("./dump"):
        shutil.rmtree("./dump", ignore_errors=False, onerror=None)
    path = os.path.join("./","dump")
    os.mkdir(path)
    if len(devices) <= 30 :
        num_threads=len(devices)
    else:
        num_threads=30
    threads = ThreadPool( num_threads )
    results = threads.map( dump_worker, devices )
    threads.close()
    threads.join()
    logging.debug(f'Dumping Data is done')
    write_device_file(devices)

#    
###### Parse collected Files  ######
#
    files = os.listdir(DUMP_DIR)
    try:
       files.remove("parsed")
       files.remove("running")
    except Exception:
        pass
    OUTPUT_DIR="./dump/parsed"
    if not os.path.exists("./dump"):
        return redirect(url_for('dump'))
    files = os.listdir(DUMP_DIR)  
    for file in files:
        if file == "device_file.csv":
            continue
        filename = f"{DUMP_DIR}/{file}"
        print(f"Parsing File: {file}")
        hostname = file[:-12]
        platform = find_type_from_hostname(devices,hostname)
        with open(filename) as f:
            f_data=f.read()
            f_data1 = f_data.split('\n****************************************\n')
            for blob in f_data1:
                try:
                    blobsplit=blob.split('\n**----------------------------------------**\n')
                    command=blobsplit[0]
                    output=blobsplit[1]
                except IndexError:
                   continue
                
                if ' vrf ' in command: 
                    parsed_vrf=parse_files.parse_textfsm(command.split(' vrf ')[0], output, platform)
                    vrf_name=command.split(' vrf ')[1]
                    command = command.split( 'vrf ')[0]
                    if command[-1] == " ":
                        command = command[:-1]
                    if parsed_vrf==("Error","Error"):
                        logging.debug(f'webnetworkdump.parsing. Parsing Error on : {hostname} for command: {command}')
                        continue
                    key=platform+'--'+command.replace(' ','_')
                    add_to_data(key, parsed_vrf, hostname, vrf_name)

                else:        
                    parsed=parse_files.parse_textfsm(command, output, platform)
                    if parsed==("Error","Error"):
                        logging.debug(f'webnetworkdump.parsing. Parsing Error on : {hostname} for command: {command}')
                        continue
                    key=platform+'--'+command.replace(' ','_')
                    add_to_data(key, parsed, hostname)
        
 
    # print(data)  
    with open (f'{DUMP_DIR}/parsed_data.json' , 'w') as file:
        file.write(json.dumps(data, indent=4))               
    content=get_status.get_status(devices)    
    create_csv_files(data)
    generate_drawio(data) #generate drawio file from parsed data
    return render_template('parse.html', status=content)

@app.route("/download_dump")
def download_dump():
    # Export dump_data
    shutil.make_archive("./output/NetworkDump", 'zip', "./dump")
    output_path = "./output/NetworkDump.zip"
    return send_file(output_path, as_attachment=True)#

@app.route("/sw_upgrade", methods=['GET', 'POST'])
def sw_upgrade():
    '''Select file for upload and upload it.'''
    content = get_status.get_status(devices)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/sw_upgrade')
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect('/sw_upgrade')
        else:
            filename = secure_filename(file.filename)
            if os.path.exists("./upload"):
                shutil.rmtree("./upload", ignore_errors=False, onerror=None)
            path = os.path.join("./", "upload")
            os.mkdir(path)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect('/sw_upgrade_loading')
    return render_template("/sw_upgrade.html", status=content)

@app.route("/sw_upgrade_loading")
def sw_upgrade_loading():
    content = get_status.get_status(devices)
    return render_template("sw_upgrade_loading.html", status=content)

@app.route("/sw_upgrade_run") 
def sw_upgrade_run():
    global devices
    content=get_status.get_status(devices)
    file = os.listdir("./upload")
    if len(file) > 1:
        redirect("/sw_upgrade")
    if len(devices) <= 30 :
        num_threads=len(devices)
    else:
        num_threads=30
    set_upgrade_status("File Uploadet to Server")
    print("File uploadet to Server")
    threads = ThreadPool( num_threads )
    results = threads.map( sw_upgrade_devices, devices )
    threads.close()
    threads.join()
    return redirect ('/device_view')

@app.route("/dhcp") # shows spinning weel and starts job
def dhcp_loading():
    global  devices
    ena_devices = enabled_devices(devices)
    content=get_status.get_status(devices)
    number_ena_devices = len(ena_devices)
    logging.debug(f'webnetworkdump.dhcp. Number of Hosts in Network: {number_ena_devices}')
    return render_template('dhcp_loading.html', status=content, text=f'One moment please!\nSearching and configuring Access-Ports on {number_ena_devices} devices ...')

@app.route("/dhcp_execute")   # sets dhcp-snooping on selected devices
def dhcp_execute():
    accessdevices =[]
    global devices
    ena_devices = enabled_devices(devices)
    number_ena_devices = len(ena_devices)
    for dev in ena_devices:  # prepair devices for quickcommand worker
        accessdevice=make_netmiko_device(dev)
        accessdevices.append(accessdevice)
    if number_ena_devices < 30 :
        num_threads=len(ena_devices)
    else:
        num_threads=30
    threads = ThreadPool( num_threads )
    results = threads.map( configure_dhcpsnooping, accessdevices )
    threads.close()
    threads.join()
    content=get_status.get_status(devices)
    return render_template('dhcp_execute.html', status=content )

@app.route("/access") # shows spinning weel and starts job
def access_loading():
    global  devices
    ena_devices = enabled_devices(devices)
    content=get_status.get_status(devices)
    number_ena_devices = len(ena_devices)
    logging.debug(f'webnetworkdump.access. Number of Hosts in Network: {number_ena_devices}')
    return render_template('access_loading.html', status=content, text=f'One moment please!\nSearching and configuring Access-Ports on {number_ena_devices} devices ...')

@app.route("/access_execute")   
def access_execute():
    accessdevices =[]
    global devices
    ena_devices = enabled_devices(devices)
    number_ena_devices = len(ena_devices)
    for dev in ena_devices:  # prepair devices for quickcommand worker
        accessdevice=make_netmiko_device(dev)
        accessdevices.append(accessdevice)
    if number_ena_devices < 30 :
        num_threads=len(ena_devices)
    else:
        num_threads=30
    threads = ThreadPool( num_threads )
    results = threads.map( configure_access_ports, accessdevices )
    threads.close()
    threads.join()
    content=get_status.get_status(devices)
    return render_template('access_execute.html', status=content )

@app.route("/quickcommands", methods=['GET', 'POST'])
def quickcommands():
    global global_quickcommands
    content=get_status.get_status(devices)
    form = QuickCommand()
    if form.validate_on_submit():
        commands=form.commands.data
        config=form.config.data
        global_quickcommands["commands"]=commands
        global_quickcommands["config"]=config
        return redirect(url_for('quickcommand_loading'))
    return render_template("quickcommands.html", form=form, title="QuickCommand", status=content)
    
@app.route("/quickcommand_loading") # shows spinning weel and starts job
def quickcommand_loading():
    global global_quickcommands, devices
    ena_devices = enabled_devices(devices)
    content=get_status.get_status(devices)
    number_ena_devices = len(ena_devices)
    number_quickcommands=len(global_quickcommands["commands"].split("\n"))
    logging.debug(f'webnetworkdump.quickcommand_loading. Number of Hosts in Network: {number_ena_devices}')
    return render_template('quickcommand_loading.html', status=content, text=f'One moment please!\nExecuting  {number_quickcommands} commands on {number_ena_devices} devices ...')
    
@app.route("/quickcommand_execute")    
def quickcommand_execute():
    quickdevices =[]
    global global_quickcommands, devices
    ena_devices = enabled_devices(devices)
    number_ena_devices = len(ena_devices)
    commands = global_quickcommands["commands"]
    config = global_quickcommands['config']
    for dev in ena_devices:  # prepair devices for quickcommand worker
        quickdevice=make_netmiko_device(dev)
        quickdevice["config"]=config
        quickdevice["commands"]=commands
        quickdevices.append(quickdevice)
    if number_ena_devices < 30 :
        num_threads=len(devices)
    else:
        num_threads=30
    threads = ThreadPool( num_threads )
    results = threads.map( execute_quickcommand, quickdevices )
    threads.close()
    threads.join()
    content=get_status.get_status(devices)
    return render_template('quickcommand_execute.html', status=content )

@app.route("/quickcommands_download")
def quickcommands_download():
    # Export quickcommands
    shutil.make_archive("./output/Quickcommands", 'zip', "./quickcommand")
    output_path = "./output/Quickcommands.zip"
    return send_file(output_path, as_attachment=True)

@app.route("/import", methods=['GET', 'POST'])
def import_devices():
    # Import Devices from device_file
    # Device file is from previous discovery and ony 1 Password is supported
    from models import network_device
    global  devices
    content=get_status.get_status(devices)
    form = PasswordForm()
    if form.validate_on_submit():
        password=form.password.data
        file = os.listdir("./upload")
        with open(f'./upload/{file[0]}') as f:
            file = f.read()
        for line in file.split('\n'):
            colums=line.split(',')
            if len(colums)<3:
                continue
            hostname=colums[0]
            device_type=colums[1]
            IP=colums[2]
            username=colums[3]
            if "IP-Address" in IP: #Exclude 1st Line
                continue            
            device = network_device(name=hostname, ip_addr=IP, username=username, password=password, dev_id=1, enabled=True, type=device_type, connected=True)
            devices.append(device)    
        return redirect('/device_view')
    return render_template("import.html", form=form, title="Device Import", status=content)

@app.route("/delete")
def delete():
    if os.path.exists("./dump"):
        shutil.rmtree("./dump", ignore_errors=False, onerror=None)
    #create empty dump directory
    path = os.path.join("./","dump")
    os.mkdir(path) #delete dump directory
    if os.path.exists("./output"):
        shutil.rmtree("./output", ignore_errors=False, onerror=None)
    #create empty dump directory
    path = os.path.join("./","output")
    os.mkdir(path) #delete quickdump directory
    if os.path.exists("./quickcommand"):
        shutil.rmtree("./quickcommand", ignore_errors=False, onerror=None)
    #create empty quickdump directory
    path = os.path.join("./","quickcommand")
    os.mkdir(path) #delete upload directory
    if os.path.exists("./upload"):
        shutil.rmtree("./upload", ignore_errors=False, onerror=None)
    #create empty upload directory
    path = os.path.join("./","upload")
    os.mkdir(path) #delete dump directory
    global devices 
    devices = []
    get_deviceinfos.delete_device()
    global quickcommands
    quickcommands = {}
    content=get_status.get_status(devices)
    return render_template("index.html",status=content)

@app.route("/delete_files")
def delete_files():
    if os.path.exists("./dump"):
        shutil.rmtree("./dump", ignore_errors=False, onerror=None)
    #create empty dump directory
    path = os.path.join("./","dump")
    os.mkdir(path) 
    if os.path.exists("./output"):
        shutil.rmtree("./output", ignore_errors=False, onerror=None)
    #create empty dump directory
    path = os.path.join("./","output")
    os.mkdir(path) 
    if os.path.exists("./quickcommand"):
        shutil.rmtree("./quickcommand", ignore_errors=False, onerror=None)
    #create empty quickdump directory
    path = os.path.join("./","quickcommand")
    os.mkdir(path) 
    #delete upload directory
    if os.path.exists("./upload"):
        shutil.rmtree("./upload", ignore_errors=False, onerror=None)
    #create empty upload directory
    path = os.path.join("./","upload")
    os.mkdir(path) 
    content=get_status.get_status(devices)
    return render_template("index.html",status=content)

@app.route("/about")
def about():
    global devices
    content=get_status.get_status(devices)
    return render_template("about.html",status=content) 

def set_upgrade_status(text):
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": text}, f)

@app.route("/sw_upgrade_status")
def sw_upgrade_status():
    try:
        with open(STATUS_FILE) as f:
            return f.read()
    except Exception:
        return json.dumps({"status": "Starting..."})

if __name__ == "__main__":
    threading.Thread(target=start_webssh_server, daemon=True).start()
    app.run(host="0.0.0.0", debug=False)   # 0.0.0.0 Needet when Container is used
