
from netmiko import ConnectHandler
import logging



def execute_quickcommand(device): 
    OUTPUT_DIR='./quickcommand'
    hostname = device.pop('hostname') # remove Hostname from Dict, not used for Netmiko
    quickcommands = device.pop('commands')
    commands = quickcommands.split("\n")
    config=device.pop('config')
    try:
        ssh_session = ConnectHandler(**device)
    except Exception as e:
        logging.debug(f'get_dumps.dump_cisco_ios: Something went wrong when connecting Device')
        logging.debug(e)
    if config:
        hostfilename = hostname +"_quick_config.txt"
        with open (f"{OUTPUT_DIR}/{hostfilename}","w") as outputfile:
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n") 
                config_output = ssh_session.send_config_set(commands)
                outputfile.write(config_output)
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
                    outputfile.write(commandoutput) 
                    outputfile.write("\n")
                    outputfile.write("*"*40)
                    outputfile.write("\n")
        except Exception as e:
            logging.debug('get_quickcommands.dump_cisco_ios: Somthing went wrong with sending commands')
            logging.debug(e)
    return

