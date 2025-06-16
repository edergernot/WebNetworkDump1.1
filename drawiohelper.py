'''helper functions for drawio '''
def shrink_name(name):
    """Shrink the name by removing the part after the first dot."""
    return name.split('.')[0] if '.' in name else name

def make_link_id(link):
    id = f"{link['from']}-{link['to']}_{link['local_port']}-{link['remote_port']}"
    return(id)

def make_reverse_link_id(link):
    id = f"{link['to']}-{link['from']}_{link['remote_port']}-{link['local_port']}"
    return(id)

def short_portname(port):
    if "GigabitEthernet" in port:
        newport = port.replace("GigabitEthernet", "Gi")
    elif "FastEthernet" in port:
        newport = port.replace("FastEthernet", "Fa")
    elif "FortyGigabitEthernet" in port:
        newport = port.replace("FortyGigabitEthernet", "Fo")
    elif "HundredGigE" in port:
        newport = port.replace("HundredGigE", "Hu")
    elif "TenGigabitEthernet" in port:
        newport = port.replace("TenGigabitEthernet", "Te")
    elif "TwentyFiveGigE" in port:
        newport = port.replace("TwentyFiveGigE", "Twe")
    elif "TwoGigabitEthernet" in port:
        newport = port.replace("TwoGigabitEthernet", "Two")
    elif "FiveGigabitEthernet" in port:
        newport = port.replace("FiveGigabitEthernet", "Fi")
    elif "FourHundredGigE" in port:
        newport = port.replace("FourHundredGigE", "400G")
    elif "Ethernet" in port:
        newport = port.replace("Ethernet", "Eth")
    else:
        newport = port
    return (newport)

def check_nodes_exist(link):
    for node in nodes:
        source_node_dont_exist=True
        destination_node_dont_exist=True
        if link["from"] == node['id']:
            source_node_dont_exist = False
        if link["to"] == node['id']:
            destination_node_dont_exist=False
        if source_node_dont_exist:
            node_element = {'data':{'id':link['from'],'label':link['from']},
                    'classes':"Host"}
            node_elements.append(node_element)
        if destination_node_dont_exist:
            node_element = {'data':{'id':link['to'],'label':link['to']},
                    'classes':"Host"}
            node_elements.append(node_element)

def remove_duplicate_links(links):
    unique_links = []
    seen_ids = set()
    for link in links:
        link_id = make_link_id(link)
        reverse_link_id = make_reverse_link_id(link)
        if link_id not in seen_ids and reverse_link_id not in seen_ids:
            unique_links.append(link)
            seen_ids.add(link_id)
            seen_ids.add(reverse_link_id)
    return unique_links
