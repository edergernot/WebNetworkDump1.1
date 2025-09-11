from drawiohelper import *
import json

def generate_drawio(data):
    from drawio import NetPlot
    try:
        ios_cdpdata = data['cisco_ios--show_cdp_neighbors_detail']
    except KeyError:
        print("No Cisco-IOS CDP-Data found")
        ios_cdpdata=[]
    try: 
        nxos_cdp_data = data['cisco_nxos--show_cdp_neighbors_detail']
    except KeyError:
        print("No NXOS CDP-Data found")
        nxos_cdp_data = []

    nodes = []
    links = []
    parsed_devices = []

    cdpdata=ios_cdpdata+nxos_cdp_data
    if len(cdpdata) == 0:
        return

    for line in cdpdata:
        host_exist = False
        node = {}
        link = {}
        local_node = shrink_name(line['Devicename'])
        parsed_devices.append(local_node)
        try:  # IOS-CDP -- Parser
            remote_node = shrink_name(line['destination_host'])
        except KeyError:
            pass
        try:  # NXOS-CDP -- Parser
            remote_node = shrink_name(line['dest_host'])
            remote_node = remote_node.split("(")[0]
        except KeyError:
            pass
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
    nodes = remove_duplicate_hosts(nodes)

    drawio = NetPlot()
    drawio.addNodeList(nodes)
    drawio.addLinkList(links)
    drawio.exportXML('./dump/drawio_all.xml')
    
    # create reduced Draw-IO, use only with dumped-Devices
    reduced_nodes=[]
    reduced_links=[]
    for line in cdpdata:
        node={}
        link={}
        local_node = shrink_name(line['Devicename'])
        try:  # IOS-CDP -- Parser
            remote_node = shrink_name(line['destination_host'])
        except KeyError:
            pass
        try:  # NXOS-CDP -- Parser
            remote_node = shrink_name(line['dest_host'])
            remote_node = remote_node.split("(")[0]
        except KeyError :
            pass
        if remote_node in parsed_devices and local_node in parsed_devices:
            node['id']=remote_node
            node['type']=line['capabilities'].split(" ")[0] # get the first capability
            link["from"]=local_node
            link["to"]=remote_node
            link["local_port"]=short_portname(line["local_port"])
            link["remote_port"]=short_portname( line["remote_port"])
            reduced_links.append(link) 
            host_exist = False
            for existing_node in reduced_nodes:  # check if node allready exist
                if node["id"] == existing_node["id"]:
                    host_exist = True
            if not host_exist:
                reduced_nodes.append(node)
                host_exist = False
    for line in cdpdata: # Append source Device if not as neigbor in CDP-Data
        node_allready_exist=False
        for node in reduced_nodes:
            if line['Devicename'] == node["id"]:
                node_allready_exist = True
                continue
        if not node_allready_exist:
            node["id"]=line["Devicename"]
            node["type"]="Host"
            reduced_nodes.append(node)
    reduced_links = remove_duplicate_links(reduced_links)
    reduced_nodes = remove_duplicate_hosts(reduced_nodes)

    small_drawio = NetPlot()
    small_drawio.addNodeList(reduced_nodes)
    small_drawio.addLinkList(reduced_links)
    small_drawio.exportXML('./dump/drawio_reduced.xml')

if __name__ == "__main__":
    jsonfile = "dump/parsed_data.json" 
    try:
        with open (jsonfile) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Datadump dont exist, please parse before running")
        exit(code = 1)
    generate_drawio(data)