__version__ = "1.3.0"
__released__ = "2020-03-11"

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
