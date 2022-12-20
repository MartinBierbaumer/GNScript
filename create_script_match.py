keywoards = ["service password", "hostname", "ip", "no", "username", "interface", "router", "banner motd", "line"]
with open("res/R1.skript") as f:
    lines = f.readlines()
output = "en\nconf t\n"
write = False
ssh = False
shutdown_found = False
in_int = False

dhcp = ""
interfaces = ""
routing = ""
cons = ""
acls = ""
grundkonfig = ""

for line in lines:
    match line.split(" "):
        case["ip", "dhcp", "excluded-address", *all]:
            dhcp += "ip dhcp excluded-address " + str(*all)
            print(dhcp)
        case ["ip", *all]:
            print("ip {}".format(*all))
