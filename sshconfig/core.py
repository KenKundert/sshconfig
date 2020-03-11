# Core internal classes and functions

# Imports {{{1
import re

from inform import display, is_str, warn
from shlib import to_path

from .preferences import DEFAULT_NETWORK_NAME, SSH_SETTINGS
from .sshconfig import NetworkEntry


# Fields Class {{{1
class Fields:
    def __init__(self):
        self.fields = []

    def append(self, field):
        if field:
            self.fields.append(field)

    def _format_field(self, field):
        comment_leader = "\n        # "
        key, value, desc = field
        if key.lower() not in SSH_SETTINGS:
            warn('unknown SSH setting.', culprit=key)
        key = SSH_SETTINGS.get(key.lower(), key)
        if value is True:
            value = 'yes'
        elif value is False:
            value = 'no'
        text = "    {} {}".format(key, value)
        if desc:
            if not isinstance(desc, list):
                desc = [desc]
            text += comment_leader + comment_leader.join(desc)
        return text

    # Iterate through fields, converting them to strings
    def render_host(self):
        return [self._format_field(field) for field in self.fields]

    # Iterate through fields, converting them to strings while replacing
    # hostname with that of guest and adding proxy through host
    def render_guest(self, guestname, name):
        # guest are assumed to always use port 22
        fields = [
            ("hostname", guestname, None),
            (
                "proxyCommand",
                "ssh {} -W {}:22".format(name, guestname),
                # on old centos servers this is 'ssh {} nc {} 22'
                "Use {} as a proxy to access {}".format(name, guestname),
            ),
        ] + [
            (key, val, desc)
            for key, val, desc in self.fields
            if key not in ["hostname", "port"]
        ]
        return [self._format_field(field) for field in fields]


# Attributes Class {{{1
class Attributes:
    def __init__(self, attributes):
        # Copy attributes while converting to a simple dictionary.
        # It is important that we copy because attributes will be deleted in this
        # function and it is important that this not have side effects.
        self.attributes = dict((k.lower(), v) for k, v in attributes.items())

    # return the attribute as a tuple containing key, value, desc
    def get(self, key, default=None):
        assert not isinstance(default, tuple)
        value = self.attributes.pop(key.lower(), default)
        if value is not default:
            if isinstance(value, tuple):
                assert len(value) == 2
                value, desc = value
                return key, value, desc
            else:
                return key, value, None

    # iterate through a list of attributes
    def getall(self, key):
        values = self.attributes.pop(key.lower(), [])
        for value in values:
            if isinstance(value, tuple):
                assert len(value) == 2
                value, desc = value
                yield key, value, desc
            else:
                yield key, value, None

    # remove an attribute
    def remove(self, key):
        self.attributes.pop(key.lower(), None)

    # iterate through remaining attributes
    def remaining(self):
        for key, value in self.attributes.items():
            if key != "guests" and key[0:1] != "_":
                if isinstance(value, tuple):
                    assert len(value) == 2
                    value, desc = value
                    yield key, value, desc
                else:
                    yield key, value, None

    # does an attribute exist
    def __contains__(self, key):
        return key.lower() in self.attributes


# Hosts Class {{{1
class Hosts:
    def __init__(self, network, proxy, proxies, settings):
        self.network = network
        self.proxy = proxy
        self.proxies = proxies
        self.config_file = settings.ssh_config_file
        self.config_dir = settings.ssh_config_file.parent
        self.settings = settings
        self.hosts = []
        self.hosts_by_name = {}

    def _append(self, name, fields, aliases=None, desc=None, guests=None):
        # process primary host
        names_as_list = [name] + (aliases if aliases else [])
        names = " ".join(names_as_list)
        if desc:
            header = "# {}\nhost {}".format(desc, names)
        else:
            header = "host {}s".format(names)
        host = "\n".join([header] + fields.render_host())
        self.hosts.append(host)
        for name in names_as_list:
            self.hosts_by_name[name] = host

        # process guests
        for guest in guests:
            key, guestname, desc = guest
            fullname = "-".join([name, guestname])
            if desc:
                header = "# {}\nhost {}".format(desc, fullname)
            else:
                header = "host {}".format(fullname)
            host = "\n".join([header] + fields.render_guest(guestname, name))
            self.hosts.append(host)
            self.hosts_by_name[fullname] = host

    def process(self, entry, forwards):
        fields = Fields()

        # Get fields
        attributes = Attributes(entry.fields())
        name = entry.__name__.lower()
        forwarding = False

        # Return if this is forwarding version and there are no forwards
        if forwards:
            if (
                "localForward" not in attributes
                and "remoteForward" not in attributes
                and "dynamicForward" not in attributes
            ):
                return
            name = "%s-tun" % name
        else:
            # Not interested in forwards, so remove them
            attributes.remove("localForward")
            attributes.remove("remoteForward")
            attributes.remove("dynamicForward")

        # Host description
        attribute = attributes.get("description")
        if attribute:
            key, value, desc = attribute
            description = (value + " (with port forwards)") if forwards else value
        else:
            description = None

        # Aliases
        aliases = [
            val + ("-tun" if forwards else "")
            for key, val, desc in attributes.getall("aliases")
        ]

        # User
        fields.append(attributes.get("user"))

        # Hostname
        attribute = attributes.get("hostname")
        if attribute:
            key, hostnames, desc = attribute
            if isinstance(hostnames, dict):
                unknown_networks = set(hostnames.keys()) - set(
                    list(NetworkEntry.known()) + [DEFAULT_NETWORK_NAME]
                )
                if unknown_networks:
                    display(
                        "{}: uses unknown networks: {}".format(
                            name, ", ".join(sorted(unknown_networks))
                        )
                    )
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
            hostname = "%h"
            hostnames = {}

        # Port
        attribute = attributes.get("port")
        if attribute:
            key, port, desc = attribute
            fields.append(attribute)
        else:
            port = "%p"

        # IdentityFile and IdentitiesOnly
        attribute = attributes.get("identityFile")
        if attribute:
            key, value, desc = attribute
            file_found = False
            if is_str(value):
                value = [value]
            for filename in value:
                filepath = to_path(self.config_dir, filename)
                if filepath.exists():
                    file_found = True
                    fields.append((key, filepath, desc))
            if file_found:
                fields.append(('identitiesOnly', 'yes', None))
                fields.append(("pubkeyAuthentication", "yes", None))
            else:
                warn('no identity files found.', culprit=name)

        # ForwardAgent
        attribute = attributes.get("trusted")
        if attribute:
            key, trusted, desc = attribute
        else:
            trusted = False
        fields.append(("forwardAgent", trusted, None))
        # fields.append(('forwardX11', 'no' if trusted else 'no', None))

        # LocalForwards
        for attribute in attributes.getall("localForward"):
            check_forward(attribute)
            fields.append(attribute)
            forwarding = True

        # RemoteForwards
        for attribute in attributes.getall("remoteForward"):
            check_forward(attribute)
            fields.append(attribute)
            forwarding = True

        # DynamicForward
        attribute = attributes.get("dynamicForward")
        if attribute:
            check_forward(attribute, True)
            fields.append(attribute)
            forwarding = True

        # ExitOnForwardFailure
        if forwarding:
            fields.append(("exitOnForwardFailure", "yes", None))

        # ProxyCommand
        attribute = attributes.get("proxyCommand")
        network = NetworkEntry.find(self.network)
        network_proxy = network.proxy if network else None
        if attribute:
            fields.append(attribute)
        elif self.proxy and not (
            self.proxy == entry.__name__.lower()
            or ((self.proxy == network_proxy) and (self.network in hostnames))
        ):
            # This host does not have a ProxyCommand entry, add it if a global
            # proxy is requested unless this host is the itself the proxy or if
            # this host is on the same network as the proxy.
            # Specifically, do not use a proxy if proxy in use was specified on
            # a network for which this host is specifically configured.  That
            # generally indicates that there is a direct path to this host on
            # this network and the proxy is not needed.

            fields.append(
                (
                    "proxyCommand",
                    self.proxies.get(
                        self.proxy,
                        "ssh {} -W {}:{}".format(self.proxy, hostname, port)
                        # on old centos servers this is 'ssh {} nc {} 22'
                    ),
                    "Use %s as global proxy to access %s" % (self.proxy, name),
                )
            )

        # SSH algorithms
        def add_algorithms(name, available):
            if available:
                attribute = attributes.get(name)
                if attribute:
                    key, value, desc = attribute
                    values = value.split(',')
                    values = [v for v in values if v in available]
                    fields.append((key, ','.join(values), desc))

        add_algorithms("ciphers", self.settings.available_ciphers)
        add_algorithms("macs", self.settings.available_macs)
        add_algorithms("hostkeyalgorithms", self.settings.available_host_key_algorithms)
        add_algorithms("kexalgorithms", self.settings.available_kex_algorithms)

        # Output any unknown attributes
        for attribute in attributes.remaining():
            fields.append(attribute)

        # Guests (hosts that use this host as a proxy)
        guests = [] if forwards else attributes.getall("guests")

        # Save host
        self._append(name, fields, aliases, description, guests)

    def output(self):
        return "\n\n".join(self.hosts)


# check_forward {{{1
# Attribute is an SSH port forward, assure it has correct syntax
re_ipaddr = r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
re_hostname = r"(([a-z][\w-]*\.)*[\w-]*[a-z])"
re_asterix = r"(\*)"
re_port = r"(\d{1,5})"
re_forward = r"\A(({addr}|{host}|{all}):)?{port}\Z".format(
    addr=re_ipaddr, host=re_hostname, all=re_asterix, port=re_port
)
forward_pattern = re.compile(re_forward, re.I)


def check_forward(attribute, dynamic=False):
    if dynamic:
        # expected format is [bindaddr:]port where port is an integer and bind
        # address may be hostname, ip address, or *.
        forward = str(attribute[1])
        if not forward_pattern.match(forward):
            exit("Invalid dynamic forward: %s" % attribute[1])
    else:
        forwards = attribute[1].split()
        if len(forwards) != 2 or not all(
            [bool(forward_pattern.match(each)) for each in forwards]
        ):
            exit("Invalid dynamic forward: %s" % attribute[1])
