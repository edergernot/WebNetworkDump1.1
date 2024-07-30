
from netmiko import ConnectHandler
import logging



def execute_quickcommand(device): 
    OUTPUT_DIR='./quickcommand'
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    quickcommands = device.pop('commands')
    commands = quickcommands.split("\n")
    config=device.pop('config')
    logging.debug(f'get_dumps.dump_cisco_ios: Try to Connect to {hostname}')
    try:
        ssh_session = ConnectHandler(**device)
        logging.debug(f"get_dumps.dump_cisco_ios: Connected to {ssh_session.find_prompt()}")
    except Exception as e:
        logging.debug(f'get_dumps.dump_cisco_ios: Something went wrong when connecting Device')
        logging.debug(e)
    if config:
        hostfilename = hostname +"_quick_config.txt"
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n") 
                try:
                    config_output = ssh_session.send_config_set(commands, read_timeout=30, cmd_verify=True)
                    if "[confirm]" in config_output:  # send 'y' wehen confirm is needet (f.e Clear counters)
                            config_output +=  ssh_session.send_command_timing('y')
                    outputfile.write(config_output)
                except UnboundLocalError:
                    print(f"SSH-Error on device {hostname}")
    else:
        hostfilename = hostname +"_quick_command.txt"
        try:
            with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")  
                for command in commands:
                    outputfile.write(command)
                    outputfile.write("\n")
                    outputfile.write("**"+"-"*40+"**")
                    outputfile.write("\n")
                    commandoutput = ssh_session.send_command_timing(command)
                    if "[confirm]" in commandoutput:  # send 'y' wehen confirm is needet (f.e Clear counters)
                        commandoutput +=  ssh_session.send_command_timing('y')
                    outputfile.write(commandoutput) 
                    outputfile.write("\n")
                    outputfile.write("*"*40)
                    outputfile.write("\n")
        except Exception as e:
            logging.debug('get_quickcommands.dump_cisco_ios: Somthing went wrong with sending commands')
            logging.debug(e)
    return

