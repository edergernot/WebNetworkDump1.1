'''
Used for basic Modeling of Device, Interface, and so on
'''

class network_device:
    def __init__(self, dev_id, name, ip_addr, username, password, type, enabled=True, connected = True):
        self.dev_id = dev_id
        self.name = name
        self.username = username
        self.ip_addr = ip_addr
        self.password = password
        self.type = type
        self.enabled = enabled
        self.connected = enabled
        