# WLED-Manager

Collection of script to manage WLED devices


## wled-backup

Downloads all files from WLED devices in a subnet in [CIDR notation](https://www.ipaddressguide.com/cidr) (config and presets), and commits them into a git directory, and pushes changes.

Requirements:
 * python
 * git

Usage (for a /27 subnet):
```bash
./wled-backup.py --output /path/to/git/repo 192.168.1.192/27
```

Usage (for a single device):
```bash
./wled-backup.py --output /path/to/git/repo 192.168.1.220
```

Usage (for entire typical home network):
```bash
./wled-backup.py --output /path/to/git/repo 192.168.1.1/24
```

Automating with cron:

This cron job will run every 5 minutes. Of course, this is excessive, but it only takes a few seconds to run and only commits when changes are made, so it's not a big deal.

```bash
# m     h  dom mon dow   command
  */5   *  *   *   *     /path/to/wled-backup.py --output /path/to/git/repo 192.168.1.192/27
```

## wled-time-config

Sets various time settings on WLED devices in a subnet in [CIDR notation](https://www.ipaddressguide.com/cidr).

To determine the `time-zone-option-index` for your timezone, navigate to a WLED device's web interface, and go to the Time & Macros page.  The index is the (0 based) number in the dropdown for your timezone. For example, for US-EST/EDT, the index is 4.

`--lat` and `--lon` must only have two decimal places. For example, Indianapolis, IN is 39.77, -86.16. You can find your latitude and longitude at [latlong.net](https://www.latlong.net/).

Requirements:
 * python

Usage:
```bash
./wled-time-config.py --ntp-server time.cloudflare.com --lat 39.77 --lon -86.16 --time-zone-option-index 4
```
