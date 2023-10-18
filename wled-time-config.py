import ipaddress
import argparse
import requests

def set_config(ip, config_changes):
    url = f"http://{ip}/settings/time"
    try:
        response = requests.post(url, data=config_changes, timeout=5)
        response.raise_for_status()
    except (requests.exceptions.RequestException) as e:
        print(f"Error setting config for {ip}: {e}")

def configure_devices(subnet, ntp_server=None, lat=None, lon=None, time_zone_option_index=None):
    net = ipaddress.ip_network(subnet, strict=False)
    for ip in net.hosts():
        config_changes = {}
        if ntp_server is not None:
            config_changes['NT'] = 'on'
            config_changes['NS'] = ntp_server
        if lat is not None:
            config_changes['LT'] = lat
        if lon is not None:
            config_changes['LN'] = lon
        if time_zone_option_index is not None:
            config_changes['CF'] = 'on'
            config_changes['TZ'] = time_zone_option_index
            config_changes['UO'] = '0'
        set_config(str(ip), config_changes)

def main():
    parser = argparse.ArgumentParser(description="Configure time settings for WLED devices on a subnet.")
    parser.add_argument('subnet', help="The subnet to scan (e.g. 192.168.1.0/24)")
    parser.add_argument('--ntp-server', help="The NTP server to use")
    parser.add_argument('--lat', help="The latitude of the device, with 2 decimal places")
    parser.add_argument('--lon', help="The longitude of the device, with 2 decimal places")
    parser.add_argument('--time-zone-option-index', help="The time zone option index to use. See README.")
    args = parser.parse_args()
    configure_devices(args.subnet, args.ntp_server, args.lat, args.lon, args.time_zone_option_index)

if __name__ == '__main__':
    main()