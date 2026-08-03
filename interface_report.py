import os
from netmiko import ConnectHandler
from netmiko import exceptions
from datetime import datetime
import pandas as pd
import json
import sys
from multiprocessing.dummy import Pool as ThreadPool

### Init Vars 
starttime = datetime.now()
switches = []
switches_checked = []
Unconfigured_ports = []

def generate_oui_dict():
    #reads the json file and creats dictonary ‚
    with open("oui.json", "r") as f:
        oui_file=f.read()
    oui_dict=json.loads(oui_file)
    global oui_to_org
    oui_to_org=oui_dict["oui_to_org"]
    

def create_devicelist(file):
    devices = []
    with open(file, "r") as f:
        file = f.read()
    for line in file.split("\n"):
        if len(line)==0:
            continue
        if "Name,Type,IP-Address" in line:
            continue
        ip_addr=line.split(",")[2]
        devices.append(ip_addr)
    return(devices)

def mac_normalizer(MAC_ADDR:str):
    mac:str=MAC_ADDR.replace(".", "")
    mac=mac.replace(":","")
    mac=mac.replace("-","")
    mac=mac.lower()
    return (mac)

def interface_cdp(ssh,interface)->str: 
    cdps = ssh.send_command(f"show cdp neighbor {interface['port']}", use_textfsm=True)
    neighbor_name=""    
    if type(cdps) == list:
        neighbor_count=len(cdps)  
        if neighbor_count > 1:
            for neighbor in cdps:
                neighbor_name+=neighbor["neighbor_name"]+","
        neighbor_name=cdps[0]["neighbor_name"]
        #print(f"CDP-Nei: {neighbor_name}")
        return(neighbor_name)
    #print(f"CDP-Nei: {neighbor_name}")
    return ("")

def generate_interfaceconfig_dict(interface_config:str)->dict:
    # Generate a dict from interface configurations
    interface:dict = {}
    interface["speed"]="auto"
    interface["duplex"]="auto"
    interface["switchport_mode"]="Not configured!"
    for line in interface_config.split("\n"):
        if len(line)<=2:
            continue
        if line == "no switchport":
            interface["switchport_mode"]="routed"
        if "switchport mode" in line:
            interface["switchport_mode"]=line.split()[-1].strip()
            continue
        if "description" in line:
            interface["description"]=line.split("description")[1].strip()
            continue
        if "switchport access vlan" in line:
            interface["vlan"]=line.split("vlan")[1].strip()
            continue
        if "switchport voice vlan" in line:
            interface["voice-vlan"]=line.split("vlan")[1].strip()
            continue
        if "port-security maximum" in line:
            interface["max_port_security"]=line.split("port-security")[1].strip()
            continue
        if "storm-control broadcast" in line:
            interface["stormctl_broadcast"]=line.split("storm-control broadcast")[1].strip()
            continue
        if "storm-control multicast" in line:
            interface["stormctl_multicast"]=line.split("storm-control multicast")[1].strip()
            continue
        if "access-session port-control auto" in line:
            interface["Dot1x"] = "Enabled"
            continue
        if "authentication port-control auto" in line:
            interface["Dot1x"] = "Enabled"
            continue
        if "mab" in line:
            interface["Mab"] = "Enabled"
            continue
        if "service-policy type" in line:
            interface["ServicePolicy"]=line.split("service-policy type")[1].strip()
            continue
        if "dot1x pae" in line:
            interface["Dot1x_Int_Type"]=line.split("dot1x pae")[1].strip()
            continue
        if "speed" in line:
            interface["speed"]=line.split("speed")[1].strip()
            continue
        if "duplex" in line:
            interface["duplex"]=line.split("duplex")[1].strip()
        if "device-tracking attach-policy" in line:
            interface["device_tracking_policy"]=line.split("device-tracking attach-policy")[1].strip
        if "channel-group" in line:
            interface["portchannel"]=line.split("channel-group")[1].strip()
        if "switchport trunk allowed vlan" in line:
            try:
                vlans=interface["trunk_vlans"]
                vlans_add=line.split("add")[1].strip()
                interface["trunk_vlans"]=vlans+vlans_add
                continue
            except KeyError:
                interface["trunk_vlans"]=line.split("switchport trunk allowed vlan")[1].strip()
                continue
        if "switchport trunk native vlan" in line:
            interface["trunk_native_vlan"]=line.split("switchport trunk native vlan")[1].strip()
            continue
        if "device-tracking attach-policy" in line:
            interface["device_tracking_policy"]=line.split("device-tracking attach-policy")[1].strip()
            continue
        if "spanning-tree" in line:
            try:
                stp_setting=interface["spanning-tree"]
                stp_additional_setting=line.split("spanning-tree")[1].strip()
                interface["spanning-tree"]=stp_setting+","+stp_additional_setting
                continue
            except KeyError:
                interface["spanning-tree"]=line.split("spanning-tree")[1].strip()
                continue
    return(interface)

def check_link(interface,ssh):
    '''Returns the status, speed and duplex of interface'''
    speed = ssh.send_command(f"show interface {interface['port']} status", use_textfsm=True)
    if type(speed) == list:
        return {"current_status":speed[0]['status'], "current_speed":speed[0]['speed'], "current_duplex":speed[0]["duplex"]}
    return

def check_poe(interface,ssh) :
    poe={}
    try:
        power = ssh.send_command(f"show power inline {interface['port']}", use_textfsm=True)
    except Exception as e:
        print(f"Error while sending PoE Command: {e}")
        return(poe)
    try:
        poe['PoE_Admin_Status']=power[0]['admin_status']
        poe['PoE_Oper_Status']=power[0]['operational_status']
        poe['PoE_Power']=power[0]['power']
        poe['PoE_Device']=power[0]['device']
        poe['PoE_class']=power[0]['class']
        poe['PoE_Max']=power[0]['max']
    except Exception as e:
        print(f"Error during converting PoE Dicts: {e}")
        print(power)
        return(poe)
    return(poe)

def generate_excel(interfaces:list):
    try:
        os.remove("./dump/interface_cfg.xlsx")
    except Exception as e:
        print(e)
    df = pd.DataFrame(interfaces)
    writer = pd.ExcelWriter('./dump/interface_cfg.xlsx', engine='xlsxwriter')

    # Write the dataframe data to XlsxWriter. Turn off the default header and
    # index and skip one row to allow us to insert a user defined header.
    sheetname= starttime.strftime("%d.%m.%Y %H%M")
    df.to_excel(writer, sheet_name=sheetname, startrow=1, header=False, index=False)

    # Get the xlsxwriter workbook and worksheet objects.
    workbook = writer.book
    
    worksheet = writer.sheets[sheetname]

    # Get the dimensions of the dataframe.
    (max_row, max_col) = df.shape

    # Create a list of column headers, to use in add_table().
    column_settings = [{'header': column} for column in df.columns]

    # Add the Excel table structure. Pandas will add the data.
    worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings}, )

    # Make the columns wider for clarity.
    worksheet.set_column(0, max_col - 1, 15)

    # Close the Pandas Excel writer and output the Excel file.
    writer._save() # type: ignore

def current_mac_address(interface,ssh):
    global oui_to_org
    mac = ssh.send_command(f"show mac address-table interface {interface['port']}",use_textfsm=True )
    mac_return={}
    l_addr=[]
    l_vlan=[]
    l_mac_type=[]
    l_vendor=[]
    if type(mac) != list:
        mac_return["MAC_Count"]=0
        return(mac_return)
    if len(mac) < 4:
        for m in mac: # generate list objects to add to Mac Table
            addr = mac_normalizer(m["destination_address"])
            l_addr.append(addr)
            vl = m.get("vlan_id")
            l_vlan.append(vl)
            mac_type = m.get("type")
            l_mac_type.append(mac_type)
            oui = addr[:6]
            vendor = oui_to_org.get(oui,"Unknow")
            l_vendor.append(vendor)
    mac_return["MAC_Count"]=len(mac)     
    if len(l_addr) == 1:
        mac_return["MAC_Addr"]=l_addr[0]
    else :
        mac_return["MAC_Addr"]=l_addr
    if len(l_vendor) == 1:
        mac_return["MAC_Vendor"]=l_vendor[0]
    else:
        mac_return["MAC_Vendor"]=l_vendor
    if len(l_vlan) == 1:
        mac_return["MAC_Vlan"]=l_vlan[0]
    else:
        mac_return["MAC_Vlan"]=l_vlan
    if len(l_mac_type) == 1:
        mac_return["MAC_Type"]=l_mac_type[0]
    else:
        mac_return["MAC_Type"]=l_mac_type
    return(mac_return)

def write_json(Interface_cfg):
    import json
    with open ("./dump/interface_cfg.json", "a") as jsonfile:
        for Interface in Interface_cfg:
            json_out = json.dumps(Interface) + '\n'
            jsonfile.write(json_out)

def json_dump(interfaces):
    with open("jsondump.json", 'w') as out:
        for interface in interfaces:
            json_out = json.dumps(interface) + '\n'
            out.write(json_out)

def interface_report(ssh):
    generate_oui_dict()   # Read OUI.json file and create dict
    Interface_cfg=[]
    hostname = ssh.find_prompt()[:-1]

    ### Interface Status, to get the Interfaces ###
    interface_status=ssh.send_command("show interface status", use_textfsm=True)
    for interface in interface_status:
        interface_config_dict:dict={}
        interface_config_dict['host']=hostname
        if  interface['port'][:2]=='Ap' : # type: ignore # Ignore AP Ports
            continue
        #if interface["name"]=='' and interface['vlan_id'] == '1':
        #    interface["Device"]=hostname
        #    Unconfigured_ports.append(interface)
        interface_config_command : str =f'show run interface {interface["port"]}' # type: ignore
        interface_config_dict["interface"]=interface.get('port') # type: ignore
        interface_config_dict["Current_Vlan"]=interface.get('vlan_id')
        try:
            interface_config=ssh.send_command(interface_config_command).split("!")[1] # type: ignore
        except IndexError:
            print(f"Error when executing command: {interface_config_command}")
            interface_config=""
        generated_intconfig_dict:dict=generate_interfaceconfig_dict(interface_config)
        #generated_intconfig_dict['macaddress_count']=count_mac_address(interface,ssh)
        current_status : dict =check_link(interface, ssh) # type: ignore
        for key in current_status.keys():
            interface_config_dict[key]= current_status[key]
        for key in generated_intconfig_dict.keys():  
            interface_config_dict[key]=generated_intconfig_dict[key]
        current_poe : dict = check_poe(interface,ssh) 
        for key in current_poe.keys():
            interface_config_dict[key]=current_poe[key]
        current_macs :dict = current_mac_address(interface,ssh)
        for key in current_macs.keys():
            interface_config_dict[key]=current_macs[key]
        interface_config_dict["cdp"]=interface_cdp(ssh,interface)
        Interface_cfg.append(interface_config_dict)
        #print(f"Check {interface_config.split("\n")[1]}")
    write_json(Interface_cfg)
    
    
        
if __name__ == "__main__":
    print("generate OUI-Dict")
    generate_oui_dict()  # Read OUI json file and create dict
    if len(sys.argv) == 1: # no device-file was added. Crawl from seedswitch
        interface_report(seeddevice)
        for switch in switches:
            interface_report(switch)
    else:  # device-file added. do Multitasking!
        file = sys.argv[1]
        devices = create_devicelist(file)
        if len(devices) <= 30 :
            num_threads=len(devices)
        else:
            num_threads=30
        threads = ThreadPool( num_threads )
        results = threads.map( interface_report, devices )
        threads.close()
        threads.join()
    print("#"*20)
    print("Generate Excel")
    generate_excel(All_Interfaces)
    print("save JsonFile")
    json_dump(All_Interfaces)
    print("#"*20)
    print(f"Switches checked {len(switches_checked)}: {switches_checked}\n")

    ### Timemessurement
    endtime = datetime.now()
    duration = endtime - starttime
    total_seconds = duration.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    tenths = int((total_seconds - int(total_seconds)) * 10)
    print(f"Finished in {hours:02}:{minutes:02}:{seconds:02}:{tenths} ")
   