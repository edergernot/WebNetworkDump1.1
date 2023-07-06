# WebNetworkDump
This should help networkengineers for giving an overview of new networks. It will ask for IP-Network to do a discovery. It will try to login via SSH and find the devicetype.

Then it will login and execute a buntch of "show-commands" depending on devicetype. The ouput will be parsed and Raw-Datafiles and pared json file will be generated. Commands which will be executed can be modified in "get_dumps.py" file. 

This dump files and parsed files can be downloaded and used for deeper analysis.

I tested with Cisco IOS, IOS-XE, NX-OS and Paloalto Firewalls.
## Easystart with DockerContainer on local maschine!

- Get Container from Dockerhub
  - ```docker run -p 5000:5000 gerni1970/webnetworkdump```

- Start dumping the Network and browse to:
  - ```http://localhost:5000```

Just add devicecredentials to SSH into device and discovery-network.

