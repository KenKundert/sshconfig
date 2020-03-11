# Settings

# License {{{1
# Copyright (C) 2018-2020 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from inform import Error, codicil, conjoin, display, full_stop, narrate, warn
from shlib import Run, to_path

from .core import Hosts
from .preferences import (
    ARP,
    CONFIG_DIR,
    SSH_CONFIG_FILE,
    UNKNOWN_NETWORK_NAME,
)
from .python import PythonFile
from .sshconfig import HostEntry, NetworkEntry, locations, ports, set_network_name

# Globals {{{1
sshconfig_names = set(
    """
    HostEntry NetworkEntry VNC ports locations is_ip_addr get_network_name
    gethostname getusername
    """.split()
)


# Settings class {{{1
class Settings:
    # Constructor {{{2
    def __init__(self, cmdline):
        self.settings = {}
        self.settings = dict()
        self.config_dir = to_path(CONFIG_DIR)
        self.read_confs()
        self.set_network(cmdline["--network"])
        self.set_proxy(cmdline["--proxy"])
        self.set_ports(cmdline["--ports"])
        self.set_location(cmdline["--location"])

    # read_confs() {{{2
    def read_confs(self):
        # read the .conf files in our config directory (except for hosts.conf)
        for name in "ssh networks locations proxies".split():
            conf_file = to_path(CONFIG_DIR, name + ".conf")
            if conf_file.exists():
                settings = PythonFile(conf_file).run()
                overlap = settings.keys() & self.settings.keys()
                overlap -= sshconfig_names
                overlap = [k for k in overlap if not k.startswith("_")]
                if overlap:
                    warn("conflicting settings:", conjoin(overlap), culprit=conf_file)
                self.settings.update(settings)

        self.ssh_config_file = to_path(
            self.settings.get("CONFIG_FILE", SSH_CONFIG_FILE)
        )
        if not self.ssh_config_file.is_absolute():
            raise Error(
                "path to SSH config file should be absolute.",
                culprit=self.ssh_config_file,
            )
        self.ssh_defaults = self.settings.get("DEFAULTS", "")
        self.ssh_overrides = self.settings.get("OVERRIDES", "")
        self.preferred_networks = self.settings.get("PREFERRED_NETWORKS", [])
        self.locations = self.settings.get("LOCATIONS", {})
        self.proxies = self.settings.get("PROXIES", {})

        self.available_ciphers = self.settings.get("AVAILABLE_CIPHERS")
        self.available_macs = self.settings.get("AVAILABLE_MACS")
        self.available_host_key_algorithms = self.settings.get("AVAILABLE_HOST_KEY_ALGORITHMS")
        self.available_kex_algorithms = self.settings.get("AVAILABLE_KEX_ALGORITHMS")

    # read_hosts() {{{2
    # must be read after port, location, and proxy choices are made
    def read_hosts(self):
        set_network_name(self.network.name())
        conf_file = to_path(CONFIG_DIR, "hosts.conf")
        narrate("reading:", conf_file)
        PythonFile(conf_file).run()

        # Process each host
        hosts = Hosts(self.network.name(), self.proxy, self.proxies, self)
        for host in HostEntry.all_hosts():
            hosts.process(host, forwards=False)
            hosts.process(host, forwards=True)
        self.hosts = hosts

    # set_network() {{{2
    def set_network(self, given=None):
        if given:
            network = NetworkEntry.find(given)
        if not given:
            network = self.identify_network()

        if not network:

            class UnknownNetwork(NetworkEntry):
                key = UNKNOWN_NETWORK_NAME

            network = NetworkEntry.find(UNKNOWN_NETWORK_NAME)
        self.network = network

        if network.ports:
            ports.available(network.ports)
        if network.location:
            locations.set_location(network.location)

    def initialize_network(self):
        network = self.network

        # run the init script if given
        try:
            if network.init_script:
                script = Run(network.init_script, "sOEW")
                if script.stdout:
                    display(script.stdout.rstrip())
        except AttributeError:
            pass
        except Error as e:
            warn(
                "{} network init_script failed: {}".format(
                    network.name(), network.init_script
                )
            )
            codicil(e.get_message())

    # set_proxy() {{{2
    def set_proxy(self, given=None):
        self.proxy = given if given else self.network.proxy

    # set_ports() {{{2
    def set_ports(self, given=None):
        ports.available(given if given else self.network.ports)

    # set_location() {{{2
    def set_location(self, given=None):
        locations.set_location(given if given else self.network.location)
        unknown = locations.unknown_locations(self.locations)
        if unknown:
            warn("the following locations are unknown (add them to LOCATIONS):")
            codicil(*sorted(unknown), sep="\n")
        self.location = self.locations.get(locations.my_location)
        if locations.my_location and not self.location:
            raise Error("unknown location, choose from:", conjoin(self.locations))

    # get_summary() {{{2
    def get_summary(self):
        summary = ["Network is", self.network.Name()]
        network_desc = self.network.description
        if network_desc:
            summary.append("({})".format(network_desc))
        if self.location:
            summary.append("located near {}".format(self.location))
        if ports.available_ports:
            summary.append(
                "using port {}".format(
                    conjoin([str(port) for port in ports.available_ports], " or ")
                )
            )
        if self.proxy:
            summary.append("proxying through {}".format(self.proxy))
        return full_stop(" ".join(summary))

    # identify_network() {{{2
    # Identifies which network we are on based on arp command
    def identify_network(self):
        # get MAC address of gateway
        try:
            arp = Run(ARP, "sOeW")
            arp_table = arp.stdout
        except Error as e:
            e.report()
            return

        gateway_macs = []
        other_macs = []
        for row in arp_table.split("\n"):
            try:
                name, ipaddr, at, mac, hwtype, on, interface = row.split()
                if name == "_gateway":
                    gateway_macs.append(mac)
                else:
                    other_macs.append(mac)
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

        for network in choose(self.preferred_networks):
            for mac in gateway_macs + other_macs:
                if mac in network.routers:
                    # We are on a known network
                    return network

    # write_ssh_config() {{{2
    def write_ssh_config(self, contents):
        narrate("writing:", self.ssh_config_file)
        self.ssh_config_file.parent.mkdir(parents=True, exist_ok=True)
        self.ssh_config_file.write_text(contents)
        self.ssh_config_file.chmod(0o600)

    # get attribute {{{2
    def __getattr__(self, name):
        return self.settings.get(name)

    # iterate through settings {{{2
    def __iter__(self):
        for key in sorted(self.settings.keys()):
            yield key, self.settings[key]
