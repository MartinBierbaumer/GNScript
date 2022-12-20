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


def getRunning(telnet):
    telnet.write(b"show run\n")
    telnet.read_until(b" bytes", 2)
    return telnet.read_until(b"!\r\nend", 30).decode('utf-8') + "\n"


def getVlan(telnet, switch):
    vlans = []

    if (switch):
        telnet.write(b"show vlan brief\n")
        data = telnet.read_until(b"end sequence", 2).decode('utf-8')
        pattern = r'^(\d+)[\s]+([\S]+)[\s]+([\S]+)'

        for line in data.split("\n"):
            matches = re.finditer(pattern, line)

            print(matches)

            for match in matches:
                vlans.append((match.group(1), match.group(2), match.group(3)))

        print(data)
        print(vlans)

    return "\n".join([f"vlan {vlan[0]}\nname {vlan[1]}" for vlan in vlans]) + "\n"


def getKonfig(telnet, switch=True):
    """retrieves the konfig and return it as a string"""

    setMode(telnet)
    running = getRunning(telnet)
    vlan = getVlan(telnet, switch)

    return running + vlan


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


def writeDevice(device, vmhost, konfig):
    print(vmhost + " " + str(device['console']))
    tel = telnetlib.Telnet(vmhost, device["console"])
    tel.expect([b"#", b">"], 300)
    tel.write(b"\n")
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

projectEndpoint = getProjectEndpoint(projectName=args.project)

if args.save is not None:
    save(args.vmhost, args.project, args.save)
if args.load is not None:
    load(args.vmhost, args.project, args.load)