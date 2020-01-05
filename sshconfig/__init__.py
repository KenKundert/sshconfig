__version__ = '1.0.1'
__released__ = '2019-11-21'

from .sshconfig import (
    HostEntry, NetworkEntry, VNC,
    ports, locations, is_ip_addr, get_network_name
)
from .utilities import gethostname, getusername

