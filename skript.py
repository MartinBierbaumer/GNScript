import telnetlib
import requests
import time
import sys
import threading
import os
import json
import re
import argparse


def getProjectEndpoint(host="localhost", port="3080", projectName=None):
    """returns the GNS-API projectEndpoint"""
    
    endPoint = "http://" + host + ":" + port + "/v2/projects"
    r = requests.get(endPoint)
    for project in r.json():
        if project["name"] == projectName:
            projectID = project["project_id"]
    return endPoint + "/" + projectID

def getDevices(projectEndpoint, verbose=False):
    """returns an iterator over all devices with the GNS-API-device information"""
    
    r = requests.get(projectEndpoint + "/nodes")
    for device in r.json():
        if (verbose):
            print(device['name'], device['properties']['hda_disk_image_md5sum'])
        yield device

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

    return telnet.read_until(b"!\r\nend", 30).decode('utf-8')

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
        for device in getDevices(projectEndpoint):
            file.write("")

def save(vmhost, projectName, path):
    """saves a GNS-project"""

    try:
        os.mkdir(path)
    except:
        print('path exists')
    projectEndpoint = getProjectEndpoint(projectName=projectName)
    saveKonfig(vmhost, projectEndpoint, path + "/skripts")
    savePhysical(vmhost, projectEndpoint, path)




parser = argparse.ArgumentParser(prog="GNScript", description="retrieves config-skripts from GNS")
parser.add_argument('-save', help="saves the configuration and stores it")
parser.add_argument('-load', help="loads the configuration")
parser.add_argument('-vmhost', help="IP of the GNS-VM")
parser.add_argument('-project', help="name of project")
args = parser.parse_args()

if args.save != None:
    save(args.vmhost, args.project, args.save)
if args.load != None:
    load(args.load)
