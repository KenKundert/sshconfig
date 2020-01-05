# Usage {{{1
"""
Generate SSH Config File

Creates an ssh config file that is specifically tailored to the current network
situation.

Usage:
    sshconfig [options] [<command> [<args>...]]

Options:
    -l LOCATION, --location LOCATION  specifies location
    -n NETWORK, --network NETWORK     specifies the network
    -p PORTS, --ports PORTS           specifies list of available ports
    -P NAME, --proxy NAME             specifies the global proxy
    -q, --quiet                       suppress optional output.

Specify the list of available ports as a comma separated list (no spaces). For
example, --ports=80,443.

Normally the network is determined automatically and need not be specified.
"""

commands = """
Commands:
{commands}

Use 'sshconfig help <command>' for information on a specific command.
Use 'sshconfig help' for list of available help topics.
"""

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
from . import __version__, __released__
from .command import Command
from .preferences import CONFIG_DIR, DATA_DIR, LOG_FILE
from .settings import Settings
from docopt import docopt
from inform import Inform, Error, cull, display, done, fatal, os_error
from shlib import to_path, set_prefs as shlib_set_prefs
shlib_set_prefs(use_inform=True)


# Globals {{{1
synopsis = __doc__ + commands.format(commands=Command.summarize())
version = f'{__version__} ({__released__})'

from .command import Command
# Main {{{1
def main():
    with Inform(notify_if_no_tty=True, version=version) as inform:
        try:
            # assure config and log directories exist
            to_path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)
            to_path(DATA_DIR).mkdir(parents=True, exist_ok=True)
            inform.set_logfile(to_path(DATA_DIR, LOG_FILE))

            # read command line
            cmdline = docopt(synopsis, options_first=True, version=version)
            command = cmdline['<command>']
            args = cmdline['<args>']
            if cmdline['--quiet']:
                inform.quiet = True

            # find and run command
            settings = Settings(cmdline)
            cmd, cmd_name = Command.find(command)
            cmd.execute(cmd_name, args, settings, cmdline)

        except KeyboardInterrupt:
            display('Terminated by user.')
        except Error as e:
            e.terminate()
        except OSError as e:
            fatal(os_error(e))
        done()
