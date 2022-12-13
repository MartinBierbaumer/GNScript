keywoards = ["service password", "hostname", "ip", "no", "username", "interface", "router", "banner motd", "line"]
f = open("res/R1.skript")
lines = f.readlines()
output = "en\nconf t\n"
write = False
ssh = False
shutdown_found = False
in_int = False


for line in lines:
    if not line.strip():
        continue
    if (line.startswith(keywoards[2] + " dhcp") or
        line.startswith(keywoards[2] + " domain")):
        output += line
    if line.startswith(keywoards[3] + " ip domain"):
        output += line
    if line.startswith(keywoards[7]):
        output += line.replace("^C", "#")
    if line.startswith(keywoards[0]) or\
       line.startswith(keywoards[4]) or\
       line.startswith(keywoards[1]):
        output += line
    if line.startswith(keywoards[5]):
        in_int = True
        write = True
    if line.startswith(keywoards[6]) or \
       line.startswith(keywoards[2] + " dhcp pool") or \
       line.startswith(keywoards[2] + " access-list") or \
       line.startswith(keywoards[8]):
        write = True
    if line.startswith("!") and write is True:
        if in_int is True and shutdown_found is False:
            output += "no shutdown\n"
        output += "exit\n"
        write = False
        in_int = False
        shutdown_found = False
    if write is True:
        if line.find("ssh") > 0:
            ssh = True
        if line.find("shutdown") > 0:
            shutdown_found = True
        output += line
if ssh is True:
    output += "crypto key generate rsa modulus 1024 exportable"
print(output)