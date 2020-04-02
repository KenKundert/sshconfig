# Commands

# License {{{1
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
import sys
from textwrap import dedent

import arrow
from docopt import docopt

from inform import Error, columns, display, full_stop, narrate, output

from .preferences import (
    DATE_FORMAT,
    DEFAULT_COMMAND,
    SSH_DEFAULTS,
    SSH_HEADER,
    SSH_HOSTS,
    SSH_OVERRIDES,
)
from .sshconfig import NetworkEntry
from .utilities import two_columns


# Utilities {{{1
# title() {{{2
def title(text):
    return full_stop(text.capitalize())


# Command base class {{{1
class Command(object):
    @classmethod
    def commands(cls):
        for cmd in cls.__subclasses__():
            if hasattr(cmd, "NAMES"):
                yield cmd
            for sub in cmd.commands():
                if hasattr(sub, "NAMES"):
                    yield sub

    @classmethod
    def commands_sorted(cls):
        for cmd in sorted(cls.commands(), key=lambda c: c.get_name()):
            yield cmd

    @classmethod
    def find(cls, name):
        if not name:
            name = DEFAULT_COMMAND
        for command in cls.commands():
            if name in command.NAMES:
                return command, command.NAMES[0]
        raise Error("unknown command.", culprit=name)

    @classmethod
    def execute(cls, name, args, settings, options):
        if hasattr(cls, "run"):
            narrate("running {} command".format(name))
            exit_status = cls.run(name, args if args else [], settings, options)
            return 0 if exit_status is None else exit_status

    @classmethod
    def summarize(cls, width=16):
        summaries = []
        for cmd in Command.commands_sorted():
            summaries.append(two_columns(", ".join(cmd.NAMES), cmd.DESCRIPTION))
        return "\n".join(summaries)

    @classmethod
    def get_name(cls):
        return cls.NAMES[0]

    @classmethod
    def help(cls):
        text = dedent(
            """
            {title}

            {usage}
        """
        ).strip()

        return text.format(title=title(cls.DESCRIPTION), usage=cls.USAGE)


# CreateCommand command {{{1
class CreateCommand(Command):
    NAMES = "create".split()
    DESCRIPTION = "create an SSH config file"
    USAGE = dedent(
        """
        Usage:
            sshconfig create
        """
    ).strip()

    @classmethod
    def run(cls, command, args, settings, options):
        # read command line
        docopt(cls.USAGE, argv=[command] + args)

        # display summary
        display(full_stop(settings.get_summary()))

        # initialize the network
        settings.initialize_network()
        # initializing the network must be done before reading the hosts
        # file as it may try to do network operations

        # create SSH config file components
        # header
        name = settings.network.Name()
        desc = settings.network.description
        if desc:
            network = f"{name} network -- {desc}"
        else:
            network = f"{name} network"
        now = arrow.now()
        time = now.format(DATE_FORMAT)
        header = SSH_HEADER.format(
            network=network, time=time, config_dir=settings.config_dir
        )

        # overrides
        overrides = settings.ssh_overrides
        if overrides:
            overrides = SSH_OVERRIDES.format(overrides=overrides)

        # hosts
        settings.read_hosts()
        hosts = SSH_HOSTS.format(hosts=settings.hosts.output())

        # defaults
        defaults = settings.ssh_defaults
        if defaults:
            defaults = SSH_DEFAULTS.format(defaults=defaults)

        # combine everything and write as SSH config file
        contents = "\n\n\n".join(
            section.strip()
            for section in [header, overrides, hosts, defaults]
            if section
        )
        settings.write_ssh_config(contents)


# FindCommand command {{{1
class FindCommand(Command):
    NAMES = "find".split()
    DESCRIPTION = "find SSH host configurations whose names contains a substring"
    USAGE = dedent(
        """
        Usage:
            sshconfig find <text>
        """
    ).strip()

    @classmethod
    def run(cls, command, args, settings, options):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)
        text = cmdline["<text>"]

        # display matches
        settings.read_hosts()
        for name in settings.hosts.hosts_by_name.keys():
            if text in name:
                display(name)


# HelpCommand {{{1
class HelpCommand(Command):
    NAMES = "help".split()
    DESCRIPTION = "give information about commands or other topics"
    USAGE = dedent(
        """
        Usage:
            sshconfig help [<topic>]
        """
    ).strip()
    REQUIRES_EXCLUSIVITY = False
    COMPOSITE_CONFIGS = None

    @classmethod
    def run(cls, command, args, settings, options):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)

        from .help import HelpMessage

        HelpMessage.show(cmdline["<topic>"])
        return 0


# AvailableCommand command {{{1
class AvailableCommand(Command):
    NAMES = "available".split()
    DESCRIPTION = "list available choices for command line options"
    USAGE = dedent(
        """
        Usage:
            sshconfig available
        """
    ).strip()

    @classmethod
    def run(cls, command, args, settings, options):
        # read command line
        docopt(cls.USAGE, argv=[command] + args)

        display("Explicit proxies (you can also use SSH hosts as proxies):")
        display(columns(sorted(settings.proxies.keys())))
        display()

        display("Locations:")
        for loc in sorted(settings.locations.keys()):
            display(
                loc=loc,
                desc=settings.locations[loc],
                template=["    {loc}: {desc}", "    {loc}"],
            )
        display()

        display("Networks:")
        for nw in sorted(NetworkEntry.all_networks(), key=lambda n: n.name()):
            display(
                nw=nw.name(), desc=nw.desc(), template=["    {nw}: {desc}", "    {nw}"]
            )
        display()


# ShowCommand command {{{1
class ShowCommand(Command):
    NAMES = "show".split()
    DESCRIPTION = "show an SSH host configuration"
    USAGE = dedent(
        """
        Usage:
            sshconfig show <name>
        """
    ).strip()

    @classmethod
    def run(cls, command, args, settings, options):
        # read command line
        cmdline = docopt(cls.USAGE, argv=[command] + args)
        name = cmdline["<name>"]

        # display summary
        display(full_stop(settings.get_summary()))
        display()

        # display host
        settings.read_hosts()
        try:
            display(settings.hosts.hosts_by_name[name])
        except KeyError:
            raise Error("not found.", culprit=name)


# VersionCommand {{{1
class VersionCommand(Command):
    NAMES = ("version",)
    DESCRIPTION = "display sshconfig version"
    USAGE = dedent(
        """
        Usage:
            sshconfig version
        """
    ).strip()

    @classmethod
    def run(cls, command, args, settings, options):

        # get the Python version
        python = "Python %s.%s.%s" % (
            sys.version_info.major,
            sys.version_info.minor,
            sys.version_info.micro,
        )

        # output the SSHconfig version along with the Python version
        from .__init__ import __version__, __released__

        output("sshconfig version: %s (%s) [%s]." % (__version__, __released__, python))
