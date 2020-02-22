__version__ = "1.2.1"
__released__ = "2020-02-21"

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
