keywoards = ["service password", "hostname", "ip", "no", "username", "interface", "router", "banner motd", "line"]
f = open("res/R1.skript")
lines = f.readlines()
output = "en\nconf t\n"
write = False
ssh = False
shutdown_found = False
in_int = False

for i in lines:
    if i.startswith(keywoards[2] + " dhcp") or \
       i.startswith(keywoards[2] + " domain"):
        output += i
    if i.startswith(keywoards[3] + " ip domain"):
        output += i
    if i.startswith(keywoards[7]):
        output += i.replace("^C", "#")
    if i.startswith(keywoards[0]) or\
       i.startswith(keywoards[4]) or\
       i.startswith(keywoards[1]):
        output += i
    if i.startswith(keywoards[5]):
        in_int = True
    if i.startswith(keywoards[6]) or \
       i.startswith(keywoards[2] + " dhcp pool") or \
       i.startswith(keywoards[2] + " access-list") or \
       i.startswith(keywoards[8]):
        write = True
    if i.startswith("!") and write is True:
        output += "exit\n"
        write = False
    if write is True:
        if i.find("ssh"):
            ssh = True
        output += i
output += "crypto key generate rsa modulus 1024 exportable"
print(output)