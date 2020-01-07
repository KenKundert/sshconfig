__version__ = '1.2.0'
__released__ = '2020-01-07'

from .sshconfig import (
    HostEntry, NetworkEntry, VNC,
    ports, locations, is_ip_addr, get_network_name
)
from .utilities import gethostname, getusername

