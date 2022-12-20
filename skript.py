import telnetlib
import requests
import time
import threading
import os
import argparse
import json
import re
import logging

#TODO logging, paths, match


def getProjectEndpoint(host="localhost", port="3080", projectName=None):
    """returns the GNS-API projectEndpoint"""


    global endPoint
    endPoint = "http://" + host + ":" + port + "/v2/projects"
    r = requests.get(endPoint)
    for project in r.json():
        if project["name"] == projectName:
            projectID = project["project_id"]
    return endPoint + "/" + projectID


def getDevices(projectEndpoint):
    """returns an iterator over all devices with the GNS-API-device information"""

    r = requests.get(projectEndpoint + "/nodes")
    return r.json()


def setMode(telnet):
    telnet.write(b"\n")
    telnet.write(b"\n")
    telnet.write(b"\n")
    time.sleep(1)
    telnet.write(b"\n")
    telnet.write(b"enable\n")
    telnet.write(b"conf t\n")
    telnet.write(b"end\n")
    telnet.write(b"terminal length 0\n")

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
                output += "no shutdown\n"
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
    return output


def getVlan(telnet):
    vlans = []

    telnet.write(b"show vlan brief\n")
    data = telnet.read_until(b"end sequence", 2).decode('utf-8')
    pattern = r'^(\d+)[\s]+([\S]+)[\s]+([\S]+)'

    for line in data.split("\n"):
        matches = re.finditer(pattern, line)

        print(matches)

        for match in matches:
                vlans.append((match.group(1), match.group(2), match.group(3)))

    return vlans

def switch_script_creates(config, telnet):
    vlans = getVlan(telnet)
    lines = config.split("\n")
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
    return output


def getRunning(telnet):
    telnet.write(b"show run\n")
    telnet.read_until(b" bytes", 2)
    return telnet.read_until(b"!\r\nend", 30).decode('utf-8') + "\n"





def getKonfig(telnet, switch=True):
    """retrieves the konfig and return it as a string"""

    setMode(telnet)

    if switch:
        konfig = switch_script_creates(getRunning(telnet), telnet)
    else:
        konfig = router_script_create(getRunning(telnet))

    return konfig


sw_hashes = ['14b981002e40b660f2d7400401e04c14', '8f14b50083a14688dec2fc791706bb3e']
ro_hashes = ['e7cb1bbd0c59280dd946feefa68fa270', '37c148ffa14a82f418a6e9c2b049fafe']


def saveItem(vmhost, device, path):
    """writes the konfig to a file"""

    with open(path, "w") as file:
        file.write(getKonfig(telnetlib.Telnet(vmhost, device["console"]),
                             switch=device['properties']['hda_disk_image_md5sum'] in sw_hashes))


def saveKonfig(vmhost, projectEndpoint, path):
    """creates multiple threads in order to open telnetconnections and save the configurations in parallel"""

    try:
        os.mkdir(path)
    except:
        print('path exists')

    threads = []
    for device in getDevices(projectEndpoint):
        print(device['properties']['hda_disk_image_md5sum'])
        thread = threading.Thread(target=saveItem, args=(vmhost, device, path + "/" + device["name"] + ".skript"))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def savePhysical(vmhost, projectEndpoint, path):
    """saves the physical config"""

    with open(path + "/konfig.konf", "w") as file:
        file.write(json.dumps(getDevices(projectEndpoint)))


def save(vmhost, projectName, path):
    """saves a GNS-project"""

    try:
        os.mkdir(path)
    except:
        print('path exists')

    projectEndpoint = getProjectEndpoint(projectName=projectName)
    saveKonfig(vmhost, projectEndpoint, path + "/skripts")
    savePhysical(vmhost, projectEndpoint, path)

    print(projectEndpoint)


def loadDevice(device, projectEndpoint):
    print(device)
    requests.post(projectEndpoint + "/templates/" + device["template_id"], '{"x": ' + str(device["x"]) + ', "y": ' + str(device["y"]) + '}')

def startDevice(device, projectEndpoint):
    print(projectEndpoint + "/nodes/" + device["node_id"] + "/start")
    requests.post(projectEndpoint + "/nodes/" + device["node_id"] + "/start", '{}')

def createProject(projectEndpoint):
    requests.post(endPoint, '{"name": ' + args.project + ', "path": "C:\\Users\\Security\\GNS3\\projects\\' + args.project + '"}')



def writeDevice(device, vmhost, konfig):
    print(vmhost + " " + str(device['console']))
    tel = telnetlib.Telnet(vmhost, device["console"])

    time.sleep(180)

    tel.write(b"enable\n")
    tel.write(b"conf t\n")
    for line in konfig.split("\n"):
        tel.write(str.encode(line + "\n"))
        time.sleep(0.05)


def createDevice(device, projectEndpoint, vmhost, konfig):
    print(konfig)

    startDevice(device, projectEndpoint)

    writeDevice(device, vmhost, konfig)


def load(vmhost, projectName, path):
    projectEndpoint = getProjectEndpoint(projectName=projectName)

    with open(path + "/konfig.konf", "r") as json_file:
        data = json.load(json_file)

    for device in data:
        loadDevice(device, projectEndpoint)

    threads = []
    for device in getDevices(projectEndpoint):
        with open(path + "/skripts/" + device["name"] + ".skript") as f:
            thread = threading.Thread(target=createDevice, args=(device, projectEndpoint, vmhost, f.read()))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()


parser = argparse.ArgumentParser(prog="GNScript", description="retrieves config-skripts from GNS")
parser.add_argument('-save', help="saves the configuration and stores it")
parser.add_argument('-load', help="loads the configuration")
parser.add_argument('-vmhost', help="IP of the GNS-VM")
parser.add_argument('-project', help="name of project")
args = parser.parse_args()

if args.save is not None:
    save(args.vmhost, args.project, args.save)
if args.load is not None:
    load(args.vmhost, args.project, args.load)