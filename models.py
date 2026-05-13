'''
Used for basic Modeling of Device, Interface, and so on
'''

class network_device:
    def __init__(self, dev_id, name, ip_addr, username, password, type, enabled=True, connected = True, use_jumphost = False, jumphost = None, is_jumphost = False, port = 22):
        self.dev_id = dev_id
        self.name = name
        self.username = username
        self.ip_addr = ip_addr
        self.password = password
        self.port = port
        self.type = type
        self.enabled = enabled
        self.connected = enabled
        self.use_jumphost = use_jumphost
        self.jumphost = jumphost  # network_device object for the jumphost, or None
        self.is_jumphost = is_jumphost
        