#!/usr/bin/env python3

import argparse
import subprocess
import ipaddress
import logging
import json
import os
import socket
from urllib import request, error

logging.basicConfig()
LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)

def repair(ip, name):
    LOG.info("Repair broken presets on %s - %s", ip, name)


def saveHost(ip, output, repair = False):
    cfg = None
    name = None
    LOG.debug("check %s" % str(ip))
    try:
        with request.urlopen(f"http://{ip}/cfg.json", timeout=1) as cfg:
            config_json = cfg.read()
            try:
                cfg = json.loads(config_json)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                LOG.info("config not valid, skipping host")
                return
            name = cfg.get("id", {}).get("name", None)
            if not name or name.lower() == "wled":
                LOG.warning("Does not have a propper name")
                name = str(ip)
            else:
                LOG.info("Found WLED %s at %s", name, ip)

            outPath = os.path.join(output, name)
            os.makedirs(outPath, exist_ok=True)
            with open(os.path.join(outPath, "last_ip"), "w") as fp:
                fp.write(str(ip))
    except (error.URLError, error.HTTPError, socket.timeout) as e:
        LOG.debug("IP %s not a WLED node" % ip)
        return

    try:
        with request.urlopen(f"http://{ip}/edit?list=/", timeout=5) as fp:
            files_json = fp.read()
            try:
                files = json.loads(files_json)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                LOG.info("files not valid :(")
                if repair:
                    repair(ip, name)
            else:
                for file in files:
                    if file.get("type") == "file":
                        file_name = file.get("name").lstrip("/")
                        with request.urlopen(f"http://{ip}/{file_name}", timeout=5) as file_content:
                            print(os.path.join(outPath, file_name))
                            with open(os.path.join(outPath, file_name), "wb") as fp:
                                fp.write(file_content.read())
    except (error.URLError, error.HTTPError, socket.timeout) as e:
        LOG.debug("Error downlading files: %s", e)
        return

    if name:
        subprocess.call(["git", "-C", output, "add", name])


def scanSubnet(subnet, output):
    net = ipaddress.ip_network(subnet, strict=False)
    LOG.debug(net)

    if net.num_addresses == 1:
        saveHost(net.network_address, output)
    else:
        for ip in net.hosts():
            saveHost(ip, output)

def main():
    parser = argparse.ArgumentParser(description="""
        Create backups from WLED config files and presets.
        Output directory should be a git repo or subdirectory of one.
        Run this script from a cronjob to backup all your WLED devices in your networks.
    """)
    parser.add_argument('subnets', metavar='subnets', type=str, nargs='+',
                        help='IP/Subnet to scan')
    parser.add_argument('--output', dest='output', required=True,
                        help='output git repository')
    args = parser.parse_args()
    print(args)

    for subnet in args.subnets:
        scanSubnet(subnet, args.output)
    subprocess.call(["git", "-C", args.output, "commit", "-m", "wled-backup sync"])
    subprocess.call(["git", "-C", args.output, "push"])

if __name__ == "__main__":
    main()
