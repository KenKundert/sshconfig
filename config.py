#
# SSH Config -- Basic Network Configuration
#
# Defines known networks. Recognizes networks by the MAC addresses of their 
# routers, can use this information to set default location, ports, and proxy.
#

from sshconfig import NetworkEntry
from socket import gethostname

# Characteristics of the known networks
#
# Use /sbin/arp to gather require information.
# Follow this prototype:
#
#     class BangaloreHyatt(NetworkEntry)
#         routers = [                       # Router MAC addresses
#             'e4:c7:22:f2:9a:46',
#             '00:15:c7:01:a7:00',
#         ]
#         location = 'bangalore'
#         ports = [80, 443]
#         proxy = 'hyatt'

class Home(NetworkEntry):
    # Home network
    routers = ['03:64:a8:e6:95:98']

class Work(NetworkEntry):
    # Work network
    routers = [
        '00:1f:9d:81:d8:00',
        '40:b3:95:68:a8:2a',
        '98:d6:f7:6a:d1:48',
        'd0:22:be:03:9f:53',
    ]
    proxy = 'work_proxy'

class Phone(NetworkEntry):
    # Phone network
    routers = [
        '3c:43:8e:77:69:4f',  # WiFi tether
        '96:80:88:af:18:8d'   # USB tether
    ]

class Library(NetworkEntry):
    # Blocks port 22
    routers = [
        'e4:c7:22:f2:9a:46',  # Wireless
        '00:15:c7:01:a7:00',  # Wireless
        '00:13:c4:80:e2:89',  # Ethernet
        '00:15:c7:01:a7:00',  # Ethernet
    ]
    ports = [80, 443]

# My locations
LOCATIONS = {
    'bayarea',
    'dallas',
    'ann-arbor',
    'shanghai',
    'bangalore'
}

# For now/place the ssh config file in a place where it will not do any damage 
# by overwriting the one we are actually using. Delete the line once you are 
# happy with your configuration.
CONFIG_FILE = "/tmp/sshconfig"

# List of trusted hosts (won't scramble known_hosts file)
TRUSTED_HOSTS = ['laptop', 'saturn.workinghard.com']

# Attribute overrides for all hosts
OVERRIDES = """
    # Require use of stronger ciphers
    Ciphers aes256-ctr,aes128-ctr,arcfour256,arcfour,aes256-cbc,aes128-cbc

    # Hash known_hosts file if this is not a trusted machine
    HashKnownHosts %s
""" % ('no' if gethostname() in TRUSTED_HOSTS else 'yes')

# Attribute defaults for all hosts
DEFAULTS = """
    ForwardX11 no

    # This will keep a seemingly dead connection on life support for 10 minutes 
    # before giving up on it.
    TCPKeepAlive no
    ServerAliveInterval 60
    ServerAliveCountMax 10

    # Enable connection sharing
    ControlMaster auto
    ControlPath /tmp/ssh_mux_%h_%p_%r
"""

# Known proxies
PROXIES = {
    'work_proxy':
        'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80',
}
