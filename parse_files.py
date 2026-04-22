def split_commands(text):
    lines = text.split("\n")
    command_seperator=[]
    for index in range(0,len(lines)):
        if lines[index] == '****************************************':
            command_seperator.append(index)
    commands=[]
    for index in range(0,len(command_seperator)):
        if index == len(command_seperator)-1:  #last command in file
            command = lines[command_seperator[index]+1:]
        else:
            command = lines[command_seperator[index]+1:command_seperator[index+1]]
        output = "\n".join(command)
        commands.append(output)
    return commands


def parse_textfsm(command,raw_cli_output,platform):
    from ntc_templates.parse import parse_output 
    import os
    try:    
        parsed_output = parse_output(platform=platform, command=command, data=raw_cli_output)
    except Exception as e:
        #print(e)
        return("Error","Error")
    return(parsed_output)



