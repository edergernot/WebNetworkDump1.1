
from get_dumps import _connect
import logging

def execute_quickcommand(device):
    OUTPUT_DIR='./quickcommand'
    hostname = device.pop('hostname')
    quickcommands = device.pop('commands')
    commands = quickcommands.split("\n")
    config = device.pop('config')

    # Connect — fail fast and visibly if it doesn't work
    try:
        device['secret'] = device['password']
        ssh_session = _connect(device)
        print(f'QuickCommand: connected to {hostname}')
    except Exception as e:
        print(f'QuickCommand: cannot connect to {hostname}: {e}')
        return

    # Enable — some devices don't need it, so just warn and continue
    try:
        ssh_session.enable()
    except Exception as e:
        print(f'QuickCommand: enable() failed on {hostname} (continuing): {e}')

    if config:
        hostfilename = hostname + "_quick_config.txt"
        with open(f"{OUTPUT_DIR}/{hostfilename}", "w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n")
            try:
                config_output = ssh_session.send_config_set(commands, read_timeout=30, cmd_verify=True)
                if "[confirm]" in config_output:
                    config_output += ssh_session.send_command_timing('y')
                outputfile.write(config_output)
            except Exception as e:
                print(f'QuickCommand: config error on {hostname}: {e}')
    else:
        hostfilename = hostname + "_quick_command.txt"
        with open(f"{OUTPUT_DIR}/{hostfilename}", "w") as outputfile:
            outputfile.write("\n")
            outputfile.write("*"*40)
            outputfile.write("\n")
            for command in commands:
                outputfile.write(command)
                outputfile.write("\n")
                outputfile.write("**" + "-"*40 + "**")
                outputfile.write("\n")
                try:
                    commandoutput = ssh_session.send_command_timing(command)
                    if "[confirm]" in commandoutput:
                        commandoutput += ssh_session.send_command_timing('y')
                except Exception as e:
                    commandoutput = f'ERROR: {e}'
                    print(f'QuickCommand: command "{command}" failed on {hostname}: {e}')
                outputfile.write(commandoutput)
                outputfile.write("\n")
                outputfile.write("*"*40)
                outputfile.write("\n")
    return

