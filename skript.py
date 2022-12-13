import telnetlib
import requests
import time
import threading
import os
import argparse
import json
import re


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

def getKonfig(telnet, switch=True):
    """retrieves the konfig and return it as a string"""

    telnet.write(b"\n")
    telnet.write(b"\n")
    telnet.write(b"\n")
    time.sleep(1)
    telnet.write(b"\n")
    telnet.write(b"enable\n")
    telnet.write(b"conf t\n")
    telnet.write(b"end\n")
    telnet.write(b"terminal length 0\n")
    telnet.write(b"show run\n")
    telnet.read_until(b" bytes", 2)

    running = telnet.read_until(b"!\r\nend", 30).decode('utf-8')

    telnet.write(b"show vlan brief\n")
    data = telnet.read_until(b"")
    pattern = '^(?!1\s)([0-9]{1,4})[\s]*([0-9a-zA-Z]*)[\s]*(active|suspended){1}'
    vlans = []

    for line in data.split("\n"):
        matches = re.finditer(pattern, line)

        for match in matches:
            vlans.append((match.group(1), match.group(2), match.group(3)))

    print(vlans)

    return running

sw_hashes = ['14b981002e40b660f2d7400401e04c14', '8f14b50083a14688dec2fc791706bb3e']
ro_hashes = ['e7cb1bbd0c59280dd946feefa68fa270']

def saveItem(vmhost, device, path):
    """writes the konfig to a file"""
    
    with open(path, "w") as file:
	    file.write(getKonfig(telnetlib.Telnet(vmhost, device["console"]), switch=device['properties']['hda_disk_image_md5sum'] in sw_hashes))

def saveKonfig(vmhost, projectEndpoint, path):
    """creates multiple threads in order to open telnetconnections and save the configurations in parallel"""
    
    try:
        os.mkdir(path)
    except:
        print('path exists')

    threads = []
    for device in getDevices(projectEndpoint):
        thread = threading.Thread(target=saveItem, args=(vmhost, device, path + "/" + device["name"] + ".skript"))
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()

def savePhysical(vmhost, projectEndpoint, path):
    """saves the physical config"""
    #TODO: implement

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



def load(vmhost, projectName, path):
    with open(path, "r") as json_file:
        data = json.load(json_file)
    for device in data:
        print(device)




parser = argparse.ArgumentParser(prog="GNScript", description="retrieves config-skripts from GNS")
parser.add_argument('-save', help="saves the configuration and stores it")
parser.add_argument('-load', help="loads the configuration")
parser.add_argument('-vmhost', help="IP of the GNS-VM")
parser.add_argument('-project', help="name of project")
args = parser.parse_args()

if args.save != None:
    save(args.vmhost, args.project, args.save)
if args.load != None:
    load(args.vmhost, args.project, args.load)
