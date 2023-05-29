#! /usr/bin/env python3

import subprocess
import sys
from pexpect import spawn

IFACE = "enp0s3"
IP = "10.254.254.10"
USER = "user"


if __name__ == "__main__":
    p = subprocess.run(["ip", "netns", "list"], capture_output=True)

    for ns in p.stdout.split(b'\n'):
        if b"netns0" in ns:
            sh = spawn(f'ip netns exec netns0 zsh -c "su {user}"')
            sys.exit(sh.interact())

    routes = subprocess.run(["ip", "route", "show", "dev", IFACE], capture_output=True)
    for route in routes.stdout.split(b'\n'):
        if b"default" in route:
            gateway = route.split(b" ")[2].decode()
            break
    else:
        sys.exit(1)

    print(subprocess.run(["ip", "netns", "add", "netns0"]))
    print(subprocess.run(["ip", "netns", "exec", "netns0", "ip", "link", "set", "lo", "up"]))
    print(subprocess.run(["ip", "link", "add", "macvlan0", "link", IFACE, "type", "macvlan", "mode", "bridge"]))
    print(subprocess.run(["ip", "link", "set", "macvlan0", "netns", "netns0"]))
    print(subprocess.run(["ip", "netns", "exec", "netns0", "ip", "link", "set", "macvlan0", "up"]))
    print(subprocess.run(["ip", "netns", "exec", "netns0", "ip", "addr", "add", IP, "peer", gateway + "/32", "dev", "macvlan0"]))
    print(subprocess.run(["ip", "netns", "exec", "netns0", "ip", "r", "add", "default", "via", gateway, "dev", "macvlan0"]))

    sh = spawn(f'ip netns exec netns0 zsh -c "su {user}"')
    sys.exit(sh.interact())
