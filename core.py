# Core Internal Classes for SSHConfig

from sshconfig import NetworkEntry
from fileutils import expandPath, makePath, normPath, getHead, Execute, ExecuteError
import os

DEFAULT_NETWORK_NAME = 'default'

# Fields Class {{{1
class Fields():
    def __init__(self):
        self.fields = []

    def append(self, field):
        if field:
            self.fields.append(field)

    def _convert(self, field):
        leader = '    '
        comment_leader = '\n%s%s# ' % (leader, leader)
        key, value, desc = field
        text = leader + '%s %s' % (key, value)
        if desc:
            if not isinstance(desc, list):
                desc = [desc]
            text += comment_leader + comment_leader.join(desc)
        return text

    # Iterate through fields, converting them to strings
    def render_host(self):
        return [self._convert(field) for field in self.fields]

    # Iterate through fields, converting them to strings while replacing
    # hostname with that of guest and adding proxy through host
    def render_guest(self, guestname, name):
        # guest are assumed to always use port 22
        fields = [
            ('hostname', guestname, None),
            (   'proxyCommand',
                'ssh {} -W {}:22'.format(name, guestname),
                # on old centos servers this is 'ssh {} nc {} 22'
                'Use {} as a proxy to access {}'.format(name, guestname)
            ),
        ] + [
            (key, val, desc)
            for key, val, desc in self.fields
            if key not in ['hostname', 'port']
        ]
        return [self._convert(field) for field in fields]

# Attributes Class {{{1
class Attributes():
    def __init__(self, attributes):
        # Copy attributes while converting to a simple dictionary.
        # It is important that we copy because attributes will be deleted in this
        # function and it is important that this not have side effects.
        self.attributes = dict(attributes)

    # return the attribute as a tuple containing key, value, desc
    def get(self, key, default=None):
        assert not isinstance(default, tuple)
        value = self.attributes.pop(key, default)
        if value is not default:
            if isinstance(value, tuple):
                assert len(value) is 2
                value, desc = value
                return key, value, desc
            else:
                return key, value, None

    # iterate through a list of attributes
    def getall(self, key):
        values = self.attributes.pop(key, [])
        for value in values:
            if isinstance(value, tuple):
                assert len(value) is 2
                value, desc = value
                yield key, value, desc
            else:
                yield key, value, None

    # remove an attribute
    def remove(self, key):
        self.attributes.pop(key, None)

    # iterate through remaining attributes
    def remaining(self):
        for key, value in self.attributes.items():
            if key != 'guests' and key[0:1] != '_':
                if isinstance(value, tuple):
                    assert len(value) is 2
                    value, desc = value
                    yield key, value, desc
                else:
                    yield key, value, None

    # does an attribute exist
    def __contains__(self, key):
        return key in self.attributes


# Hosts Class {{{1
class Hosts():
    def __init__(self, network, networks, proxy, proxies, config_file):
        self.network = network
        self.networks = set(networks + [DEFAULT_NETWORK_NAME])
        self.proxy = proxy
        self.proxies = proxies
        self.config_file = config_file
        self.hosts = []

    def _append(
            self, name, fields, aliases=None, desc=None, guests=None):
        # process primary host
        names = ' '.join([name] + (aliases if aliases else []))
        if desc:
            header = "# %s\nhost %s" % (desc, names)
        else:
            header = "host %s" % (names)
        self.hosts.append('\n'.join([header] + fields.render_host()))

        # process guests
        for guest in guests:
            key, guestname, desc = guest
            fullname = '%s-%s' % (name, guestname)
            if desc:
                header = "# %s\nhost %s" % (desc, fullname)
            else:
                header = "host %s" % (fullname)
            self.hosts.append('\n'.join(
                [header] + fields.render_guest(guestname, name)
            ))

    def process(self, entry, tunnels):
        fields = Fields()

        # Get fields
        attributes = Attributes(entry.fields())
        name = entry.__name__.lower()
        forwards = False

        # Return if this is tunnels version and there are no tunnels
        if tunnels:
            if (
                'localForward' not in attributes and
                'remoteForward' not in attributes and
                'dynamicForward' not in attributes
            ):
                return
            name = '%s-tun' % name
        else:
            # Not interested in tunnels, so remove them
            attributes.remove('localForward')
            attributes.remove('remoteForward')
            attributes.remove('dynamicForward')

        # Host description
        attribute = attributes.get('description')
        if attribute:
            key, value, desc = attribute
            description = (value + ' (with tunnels)') if tunnels else value
        else:
            description = None

        # Aliases
        aliases = [
            val + ('-tun' if tunnels else '')
            for key, val, desc in attributes.getall('aliases')
        ]

        # User
        fields.append(attributes.get('user'))

        # Hostname
        attribute = attributes.get('hostname')
        if attribute:
            key, hostname, desc = attribute
            if isinstance(hostname, dict):
                unknown_networks = set(hostname.keys()) - self.networks
                if unknown_networks:
                    print('%s: uses unknown networks: %s' % (
                        name, ', '.join(sorted(unknown_networks))
                    ))
                if self.network in hostname:
                    hostname = hostname[self.network]
                elif DEFAULT_NETWORK_NAME in hostname:
                    hostname = hostname[DEFAULT_NETWORK_NAME]
                else:
                    exit("%s: missing '%s' hostname." % (
                        name, DEFAULT_NETWORK_NAME
                    ))
                attribute = key, hostname, desc
            fields.append(attribute)
        else:
            hostname = '%h'

        # Port
        attribute = attributes.get('port')
        if attribute:
            key, port, desc = attribute
            fields.append(attribute)
        else:
            port = '%p'

        # IdentityFile and IdentitiesOnly
        attribute = attributes.get('identityFile')
        if attribute:
            key, value, desc = attribute
            filename = expandPath(value)
            if not os.path.isabs(filename):
                filename = normPath(makePath(getHead(self.config_file), filename))
            attribute = key, filename, desc
            fields.append(attribute)
            fields.append(('identitiesOnly', 'yes', None))

        # ForwardAgent
        trusted = attributes.get('trusted')
        tun_trusted = attributes.get('tun_trusted')
        attribute = tun_trusted if tunnels else trusted
        if attribute:
            key, trusted, desc = attribute
        else:
            trusted = False
        fields.append(
            ('forwardAgent', 'yes' if trusted else 'no', None)
        )
        #fields.append(('forwardX11', 'no' if trusted else 'no', None))

        # LocalForwards
        for attribute in attributes.getall('localForward'):
            checkForward(attribute)
            fields.append(attribute)
            forwards = True

        # RemoteForwards
        for attribute in attributes.getall('remoteForward'):
            checkForward(attribute)
            fields.append(attribute)
            forwards = True

        # DynamicForward
        attribute = attributes.get('dynamicForward')
        if attribute:
            checkForward(attribute, True)
            fields.append(attribute)
            forwards = True

        # ExitOnForwardFailure
        if forwards:
            fields.append(('exitOnForwardFailure', 'yes', None))

        # ProxyCommand
        attribute = attributes.get('proxyCommand')
        if attribute:
            fields.append(attribute)
        elif self.proxy and self.proxy != entry.__name__.lower():
            fields.append((
                'proxyCommand',
                self.proxies.get(
                    self.proxy,
                    'ssh {} -W {}:{}'.format(self.proxy, hostname, port)
                    # on old centos servers this is 'ssh {} nc {} 22'
                ),
                'Use %s as global proxy to access %s' % (self.proxy, name)
            ))

        # Output any unknown attributes
        for attribute in attributes.remaining():
            fields.append(attribute)

        # Guests (hosts that use this host as a proxy)
        guests = [] if tunnels else attributes.getall('guests')

        # Save host
        self._append(name, fields, aliases, description, guests)

    def output(self):
        return '\n\n'.join(self.hosts)


# Identify Network {{{1
# Identifies which network we are on based on contents of /proc/net/arp
def identifyNetwork():
    unrecognized = 'generic', None
    try:
        arp = Execute(['/sbin/arp', '-a', '-n'])
    except ExecuteError as error:
        print(str(error))
        return unrecognized
    if arp.status:
        return unrecognized
    arpTable = arp.stdout.strip().split('\n')
    #arpTable = open('/proc/net/arp').readlines()

    for row in arpTable:
        #gateway, hwtype, flags, mac, mask, interface = row.split()
        try:
            ignore, gateway, ignore, mac, hwtype, ignore, iface = row.split()
        except ValueError:
            continue
        for network in NetworkEntry.all_networks():
            name = network.name()
            if mac in network.routers:
                # We are on a known network
                if network.ports:
                    ports.available(network.ports)
                if network.location:
                    locations.set_location(network.location)
                return network.name(), network.proxy
    return unrecognized

# checkForward{{{1
# Attribute is an SSH port forward, assure it has correct syntax
import re
re_ipaddr = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
re_hostname = r'(([a-z][\w-]*\.)*[\w-]*[a-z])'
re_asterix = r'(\*)'
re_port = r'(\d{1,5})'
re_forward = r'\A(({addr}|{host}|{all}):)?{port}\Z'.format(
    addr=re_ipaddr,
    host=re_hostname,
    all=re_asterix,
    port=re_port
)
forward_pattern = re.compile(re_forward, re.I)

def checkForward(attribute, dynamic=False):
    if dynamic:
        # expected format is [bindaddr:]port where port is an integer and bind 
        # address may be hostname, ip address, or *.
        forward = str(attribute[1])
        if not forward_pattern.match(forward):
            exit('Invalid dynamic forward: %s' % attribute[1])
    else:
        forwards = attribute[1].split()
        if (
           len(forwards) != 2 or
           not all([bool(forward_pattern.match(each)) for each in forwards])
        ):
            exit('Invalid dynamic forward: %s' % attribute[1])
