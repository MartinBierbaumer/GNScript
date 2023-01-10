import re
def router_script_create(config):
    keywoards = ["ip", "interface", "router", "line"]
    output = "en\nconf t\n"
    write = False
    ssh = False
    shutdown_found = False
    in_int = False

    for line in config.split('\n'):
        if not line.strip():
            continue
        elif line.startswith(keywoards[1]):
            in_int = True
            write = True
        elif line.startswith(keywoards[2]) or \
                line.startswith(keywoards[0] + " dhcp pool") or \
                line.startswith(keywoards[0] + " access-list") or \
                line.startswith(keywoards[3]):
            write = True
        elif line.startswith("!") and write is True:
            if in_int is True and shutdown_found is False:
                output += " no shutdown\n"
            output += "exit\n\n"
            write = False
            in_int = False
            shutdown_found = False
        elif write is True:
            if line.find("ssh") >= 0:
                ssh = True
            if line.find("shutdown") >= 0:
                shutdown_found = True
            output += line + "\n"
            continue
        elif line.startswith("end"):
            continue
        output += line + "\n"

    if ssh is True:
        output += "crypto key generate rsa modulus 1024 exportable\nend\n"
    print(output)

def switch_script_creates(config, brief):
    text_file = open("res/SW1_VLAN_BRIEF.txt", "r")
    data = text_file.read()
    text_file.close()

    pattern = '^(?!1\s)([0-9]{1,4})[\s]*([0-9a-zA-Z]*)[\s]*(active|suspended){1}'
    vlans = []
    for line in data.split("\n"):
        matches = re.finditer(pattern, line)
        for match in matches:
            vlans.append((match.group(1), match.group(2)))

    with open("res/SW1.txt") as f:
        lines = f.readlines()
    output = "en\nconf t\n"
    write = False
    ssh = False
    for line in lines:
        if not line.strip():
            continue
        elif (line.startswith("interface") or
              line.startswith("line")):
            write = True
        elif write is True:
            if line.find("ssh") >= 0:
                ssh = True
            if line.startswith("!"):
                output += "exit\n"
                write = False
            output += line
            continue
        elif line.startswith("end"):
            continue
        output += line
    for vlan in vlans:
        output += "vlan " + vlan[0] + "\nname " + vlan[1] + "\n"
    output += "exit\n"
    if ssh is True:
        output += "crypto key generate rsa modulus 1024 exportable\nend\n"
    print(output)