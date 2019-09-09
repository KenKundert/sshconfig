# Core Internal Classes for SSHConfig

from sshconfig import NetworkEntry, locations, ports
from scripts import join, normpath, head, Run, ScriptError
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
    def __init__(self, network, proxy, proxies, config_file):
        self.network = network
        self.proxy = proxy
        self.proxies = proxies
        self.config_file = config_file
        self.hosts = []

    def _append(self, name, fields, aliases=None, desc=None, guests=None):
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

    def process(self, entry, forwards):
        fields = Fields()

        # Get fields
        attributes = Attributes(entry.fields())
        name = entry.__name__.lower()
        forwarding = False

        # Return if this is forwarding version and there are no forwards
        if forwards:
            if (
                'localForward' not in attributes and
                'remoteForward' not in attributes and
                'dynamicForward' not in attributes
            ):
                return
            name = '%s-tun' % name
        else:
            # Not interested in forwards, so remove them
            attributes.remove('localForward')
            attributes.remove('remoteForward')
            attributes.remove('dynamicForward')

        # Host description
        attribute = attributes.get('description')
        if attribute:
            key, value, desc = attribute
            description = (value + ' (with forwards)') if forwards else value
        else:
            description = None

        # Aliases
        aliases = [
            val + ('-tun' if forwards else '')
            for key, val, desc in attributes.getall('aliases')
        ]

        # User
        fields.append(attributes.get('user'))

        # Hostname
        attribute = attributes.get('hostname')
        if attribute:
            key, hostnames, desc = attribute
            if isinstance(hostnames, dict):
                unknown_networks = (
                    set(hostnames.keys()) 
                  - set(list(NetworkEntry.known()) + [DEFAULT_NETWORK_NAME])
                )
                if unknown_networks:
                    print('%s: uses unknown networks: %s' % (
                        name, ', '.join(sorted(unknown_networks))
                    ))
                if self.network in hostnames:
                    hostname = hostnames[self.network]
                elif DEFAULT_NETWORK_NAME in hostnames:
                    hostname = hostnames[DEFAULT_NETWORK_NAME]
                else:
                    return
                attribute = key, hostname, desc
            else:
                hostnames = {}
                hostname = hostnames
            fields.append(attribute)
        else:
            hostname = '%h'
            hostnames = {}

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
            filename = join(value)
            if not os.path.isabs(filename):
                filename = normpath(join(head(self.config_file), filename))
            attribute = key, filename, desc
            fields.append(attribute)
            #fields.append(('identitiesOnly', 'yes', None))
                # not sure this is a good idea
                # causes problems if I copy a config file to a remote machine
                # that does not have local copies of the keys and instead are
                # using a forwarded agent.
            fields.append(('pubkeyAuthentication', 'yes', None))

        # ForwardAgent
        trusted = attributes.get('trusted')
        tun_trusted = attributes.get('tun_trusted')
        attribute = tun_trusted if forwards else trusted
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
            forwarding = True

        # RemoteForwards
        for attribute in attributes.getall('remoteForward'):
            checkForward(attribute)
            fields.append(attribute)
            forwarding = True

        # DynamicForward
        attribute = attributes.get('dynamicForward')
        if attribute:
            checkForward(attribute, True)
            fields.append(attribute)
            forwarding = True

        # ExitOnForwardFailure
        if forwarding:
            fields.append(('exitOnForwardFailure', 'yes', None))

        # ProxyCommand
        attribute = attributes.get('proxyCommand')
        network = NetworkEntry.find(self.network)
        network_proxy = network.proxy if network else None
        if attribute:
            fields.append(attribute)
        elif (
            self.proxy and not (
                self.proxy == entry.__name__.lower() or (
                    (self.proxy == network_proxy) and (self.network in hostnames)
                )
            )
        ):
            # This host does not have a ProxyCommand entry, add it if a global 
            # proxy is requested unless this host is the itself the proxy or if 
            # this host is on the same network as the proxy.
            # Specifically, do not use a proxy if proxy in use was specified on 
            # a network for which this host is specifically configured.  That 
            # generally indicates that there is a direct path to this host on 
            # this network and the proxy is not needed.

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
        guests = [] if forwards else attributes.getall('guests')

        # Save host
        self._append(name, fields, aliases, description, guests)

    def output(self):
        return '\n\n'.join(self.hosts)


# Identify Network {{{1
# Identifies which network we are on based on contents of /proc/net/arp
def identifyNetwork(preferred):
    try:
        arp = Run(['/sbin/arp', '-a', '-n'], 'sOeW')
    except ScriptError as error:
        print(str(error))
        return 'unknown'
    if arp.status:
        return 'unknown'
    arpTable = arp.stdout.strip().split('\n')
    #arpTable = open('/proc/net/arp').readlines()

    macs = []
    for row in arpTable:
        #gateway, hwtype, flags, mac, mask, interface = row.split()
        try:
            ignore, gateway, ignore, mac, hwtype, ignore, iface = row.split()
            macs.append(mac)
        except ValueError:
            continue

    def choose(preferred):
        # First offer the preferred networks, in order
        for name in preferred:
            network = NetworkEntry.find(name)
            if network:
                yield network
        # Offer the remaining networks in arbitrary order
        for network in NetworkEntry.all_networks():
            yield network

    for network in choose(preferred):
        for mac in macs:
            if mac in network.routers:
                # We are on a known network
                return network.name()

    return 'unknown'

# Initialize network {{{1
def initializeNetwork(network):
    if network.ports:
        ports.available(network.ports)
    if network.location:
        locations.set_location(network.location)
    try:
        if network.init_script:
            script = Run(network.init_script, 'soew')
            script.wait()
    except AttributeError:
        pass
    except ScriptError:
        # not capturing output, so user should already have error message
        print("%s network init_script failed (ignored): '%s'" % (
            network.name(), str(script)
        ))

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
