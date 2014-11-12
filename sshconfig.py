#
# Utilities for ssh config file generator
#

_KEYS_TO_INHERIT = ['user', 'identityFile']

def VNC(
    dispNum=0,
    rmtHost='localhost',
    lclDispNum=None,
    rmtDispNum=None,
    lclHost=None
):
    if lclDispNum is None:
        lclDispNum = dispNum
    if rmtDispNum is None:
        rmtDispNum = dispNum
    lclHost = lclHost + ':' if lclHost else ''
    return "%s%d %s:%d" % (lclHost, 5900+lclDispNum, rmtHost, 5900+rmtDispNum)

# Used to describe an available host
class NetworkEntry():
    routers = []
    ports = None
    location = None
    proxy = None

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def all_networks(cls):
        for sub in cls.__subclasses__():
            yield sub
            for sub in sub.all_networks():
                yield sub

    @classmethod
    def name(cls):
        return cls.__name__.lower()

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

# Used to describe an available host
class HostEntry():
    def __init__(self):
        raise NotImplementedError

    @classmethod
    def all_hosts(cls):
        for sub in cls.__subclasses__():
            yield sub
            for sub in sub.all_hosts():
                yield sub

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
            hostname = my_fields.pop('hostname', cls.name())
            port = my_fields.pop('port', 22)
            fields = {key: parent_fields[key] for key in _KEYS_TO_INHERIT}
            fields.update({
                'proxyCommand': (
                    #'ssh {} -W %h:%p'.format(parent.name()),
                        # Above works in most cases, but it uses the ssh config 
                        # entry name as %h rather than the hostname, so it fails 
                        # when ssh config entry name does not correspond to 
                        # a know host by the proxy host (occurs with tunneling 
                        # entries).  So instead use the actual specified 
                        # hostname.
                    'ssh {} -W {}:{}'.format(parent.name(), hostname, port),
                    'Use {} as a proxy to access {} via port {}'.format(
                        parent.name(), hostname, port
                    )
                )
            })
        else:
            fields = {}

        # Override inherited fields with those that were specified
        fields.update(my_fields)

        return fields

# Used when selecting which port to use when several are available
class Ports():
    def __init__(self):
        self.available_ports = None

    def available(self, ports):
        try:
            self.available_ports = [int(port) for port in ports.split(',')]
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

ports = Ports()

# Used when selecting hostname as a function of current location
class Locations():
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
                location,
                location if location in locations else default
            )
        return locations.get(location)

    def unknown_locations(self, known_locations):
        seen = set(self.seen_locations.keys())
        for each in known_locations:
           seen.discard(each)
        return seen

locations = Locations()
