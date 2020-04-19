__version__ = "2.0.1"
__released__ = "2020-04-18"

from .sshconfig import (
    VNC,
    HostEntry,
    NetworkEntry,
    get_network_name,
    is_ip_addr,
    locations,
    ports,
)
from .utilities import gethostname, getusername
