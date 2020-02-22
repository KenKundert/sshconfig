# Help
# Output a help topic.

# License {{{1
# Copyright (C) 2018-2020 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses.


# Imports {{{1
from textwrap import dedent

from inform import Error, error, output

from .command import Command
from .utilities import pager, two_columns


# HelpMessage base class {{{1
class HelpMessage(object):
    # get_name() {{{2
    @classmethod
    def get_name(cls):
        try:
            return cls.name.lower()
        except AttributeError:
            # consider converting lower to upper case transitions in __name__ to
            # dashes.
            return cls.__name__.lower()

    # topics {{{2
    @classmethod
    def topics(cls):
        for sub in cls.__subclasses__():
            yield sub

    # show {{{2
    @classmethod
    def show(cls, name=None):
        if name:
            # search commands
            try:
                command, _ = Command.find(name)
                if command:
                    return pager(command.help())
            except Error:
                pass

            # search topics
            for topic in cls.topics():
                if name == topic.get_name():
                    return pager(topic.help())

            error("topic not found.", culprit=name)
        else:
            from .main import synopsis

            cls.help(synopsis)

    # summarize {{{2
    @classmethod
    def summarize(cls, width=16):
        summaries = []
        for topic in sorted(cls.topics(), key=lambda topic: topic.get_name()):
            summaries.append(two_columns(topic.get_name(), topic.DESCRIPTION))
        return "\n".join(summaries)

    # help {{{2
    @classmethod
    def help(cls, desc):
        if desc:
            output(desc.strip() + "\n")

        output("Available commands:")
        output(Command.summarize())

        output("\nAvailable topics:")
        output(cls.summarize())


# Overview class {{{1
class Overview(HelpMessage):
    DESCRIPTION = "overview of sshconfig"

    @staticmethod
    def help():
        text = dedent(
            """
            SSH Config generates an SSH config file adapted to the network you
            are currently using.  In this way, you always use the fastest paths
            available for your SSH related activities (sshfs, email, vnc,
            mercurial, etc.). You can also easily reconfigure SSH to make use
            of proxies as needed or select certain servers or ports based on
            your location or restrictions on the network.
            """
        ).strip()
        return text
