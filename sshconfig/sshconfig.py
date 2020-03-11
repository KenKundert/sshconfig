# SSHConfig utility classes and functions
#
# These are used by the user in the conf files.

# Imports {{{1
import re

# Globals {{{1
KEYS_TO_INHERIT = ["user", "identityFile"]
LOWER_TO_UPPER_TRANSITION = re.compile(r"([a-z])([A-Z])")

# Utilities {{{1
# network_name {{{2
# called from main with the name of the chosen network
# allows users to change their configuration based on the active network
chosen_network_name = None


def set_network_name(name):
    global chosen_network_name
    chosen_network_name = name.lower()


def get_network_name():
    "Returns name of network (lowercase)"
    return chosen_network_name


# is_ip_addr {{{2
ip_addr_ptn = re.compile(r"\A\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*\Z")


def is_ip_addr(addr):
    return ip_addr_ptn.match(addr)


# VNC {{{2
# Generates forwards for VNC
def VNC(dispNum=0, rmtHost="localhost", lclDispNum=None, rmtDispNum=None, lclHost=None):
    if lclDispNum is None:
        lclDispNum = dispNum
    if rmtDispNum is None:
        rmtDispNum = dispNum
    lclHost = lclHost + ":" if lclHost else ""
    return "%s%d %s:%d" % (lclHost, 5900 + lclDispNum, rmtHost, 5900 + rmtDispNum)


# NetworkEntry class {{{1
# Used to describe a known network
class NetworkEntry:
    key = None  # succinct version of the name (optional)
    description = None  # descriptive version of the name (optional)
    routers = []
    ports = None
    location = None
    proxy = None

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def all_networks(cls):
        # yields all known networks
        for subclass in cls.__subclasses__():
            yield subclass
            for subclass in subclass.all_networks():
                yield subclass

    @classmethod
    def name(cls):
        return cls.key.lower() if cls.key else cls.__name__.lower()

    @classmethod
    def Name(cls):
        return cls.key if cls.key else cls.__name__

    @classmethod
    def desc(cls):
        # the descriptions that are created from the class name are
        # unattractive, and the rest of the code tends to use cls.description
        # rather than cls.desc().
        if cls.description:
            return cls.description
        # Return formatted name
        # '__' is converted to ' - ', so Library__MV becomes 'Library - MV'
        # '_' is replaced by ' '
        # space inserted upon lower case to upper case transitions
        description = cls.__name__.replace("__", " - ")
        description = description.replace("_", " ")
        description = LOWER_TO_UPPER_TRANSITION.sub(r"\1 \2", description)
        return description

    @classmethod
    def fields(cls):
        parents = cls.__bases__
        assert len(parents) == 1
        parent = parents[0]
        my_fields = dict(cls.__dict__)

        # Inherit fields from the parent, overriding fields that were specified
        fields = dict(parent.__dict__)
        fields.update(my_fields)
        return fields

    @classmethod
    def find(cls, name):
        name = name.lower()
        for subclass in cls.__subclasses__():
            if subclass.key and subclass.key.lower() == name:
                return subclass
            if subclass.__name__.lower() == name:
                return subclass
        return None

    @classmethod
    def known(cls):
        # yields the names associated with any known network
        for subclass in cls.__subclasses__():
            if subclass.key:
                yield subclass.key.lower()
            yield subclass.__name__.lower()

    @classmethod
    def get_location(cls, given=None):
        return given if given else cls.location


# HostEntry class {{{1
# Used to describe an available host
class HostEntry:
    def __init__(self):
        raise NotImplementedError

    @classmethod
    def all_hosts(cls):
        for subclass in sorted(cls.__subclasses__(), key=lambda s: s.__name__):
            yield subclass
            for subclass in subclass.all_hosts():
                yield subclass

    @classmethod
    def name(cls):
        return cls.__name__.lower()

    @classmethod
    def fields(cls):
        parents = cls.__bases__
        assert len(parents) == 1
        parent = parents[0]
        my_fields = dict(cls.__dict__)

        # Inherit selected fields from the parent
        if parent.__name__ != HostEntry.__name__:
            parent_fields = parent.__dict__
            # Get the hostname and port number
            hostname = my_fields.pop("hostname", cls.name())
            port = my_fields.pop("port", 22)
            fields = {
                key: parent_fields[key]
                for key in KEYS_TO_INHERIT
                if key in parent_fields
            }
            fields.update(
                {
                    "proxyCommand": (
                        # 'ssh {} -W %h:%p'.format(parent.name()),
                        # Above works in most cases, but it uses the ssh config
                        # entry name as %h rather than the hostname, so it fails
                        # when ssh config entry name does not correspond to
                        # a known host by the proxy host (occurs with forwarding
                        # entries).  So instead use the actual specified
                        # hostname.
                        "ssh {} -W {}:{}".format(parent.name(), hostname, port),
                        "Use {} as a proxy to access {} via port {}".format(
                            parent.name(), hostname, port
                        ),
                    )
                }
            )
        else:
            fields = {}

        # Override inherited fields with those that were specified
        fields.update(my_fields)

        return fields


# Ports class {{{1
# Used when selecting which port to use when several are available
class Ports:
    def __init__(self):
        self.available_ports = None

    def available(self, ports):
        try:
            self.available_ports = [int(port) for port in ports.split(",")]
        except AttributeError:
            self.available_ports = ports

    def not_available(self, port):
        return self.available_ports and port not in self.available_ports

    def choose(self, supported_ports):
        if self.available_ports is None:
            return supported_ports[0]
        for port in self.available_ports:
            if port in supported_ports:
                return port
        return None


# Locations class {{{1
# Used when selecting hostname as a function of current location
class Locations:
    def __init__(self):
        self.my_location = None
        self.seen_locations = {}

    def set_location(self, location):
        self.my_location = location

    def choose(self, locations, maps, default):
        location = self.my_location
        if maps:
            self.seen_locations.update(maps)
            location = maps.get(
                location, location if location in locations else default
            )
        return locations.get(location)

    def unknown_locations(self, known_locations):
        seen = set(self.seen_locations.keys())
        for each in known_locations:
            seen.discard(each)
        return seen


ports = Ports()
locations = Locations()
