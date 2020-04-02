__version__ = "1.3.2"
__released__ = "2020-04-01"

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
