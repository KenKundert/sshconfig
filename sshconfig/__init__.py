__version__ = "2.1.0"
__released__ = "2021-01-18"

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
