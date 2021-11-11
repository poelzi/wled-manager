#!/usr/bin/env python3

import argparse
import subprocess
import ipaddress
import logging
import json
import os
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
        with request.urlopen("http://%s/cfg.json" % str(ip), timeout=5) as cfg:
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
            with open(os.path.join(outPath, "cfg.json"), "wb") as fp:
                fp.write(config_json)
            with open(os.path.join(outPath, "last_ip"), "w") as fp:
                fp.write(str(ip))
    except (error.URLError, error.HTTPError) as e:
        LOG.debug("IP %s not a WLED node" % ip)
        return

    try:
        with request.urlopen("http://%s/presets.json" % str(ip), timeout=5) as fp:
            presets_json = fp.read()
            try:
                cfg = json.loads(presets_json)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                LOG.info("presets not valid :(")
                if repair:
                    repair(ip, name)
            else:
                with open(os.path.join(outPath, "presets.json"), "wb") as fp:
                    fp.write(presets_json)
    except (error.URLError, error.HTTPError) as e:
        LOG.debug("Error downlading presets.json: %s", e)

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

if __name__ == "__main__":
    main()