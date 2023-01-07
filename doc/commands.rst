Command Reference
=================

.. _sshconfig command line options:

Common Command Line Arguments
-----------------------------

::

    Usage:

        sshconfig [options] [<command> [<args>...]]

    Options:

        -l LOCATION, --location LOCATION  specifies location
        -n NETWORK, --network NETWORK     specifies the network
        -p PORTS, --ports PORTS           specifies list of available ports
        -P NAME, --proxy NAME             specifies the global proxy
        -q, --quiet                       suppress optional output

Specify the list of available ports as a comma separated list (no spaces). For
example, --ports=80,443.

Normally the network is determined automatically and need not be specified.

Run ``sshconfig help <command>`` for information on a specific command.

Run ``sshconfig help`` for list of available help topics.

Run ``sshconfig available`` to see available choices for proxies, locations, and 
networks.


.. _sshconfig available command:

**available** -- Show Available Option Choices
----------------------------------------------

Usage::

    sshconfig available

The ``--location``, ``--network``, and ``--proxies`` options all take values as 
arguments that were specified in your configuration files. The *available* 
command can be used to refresh your memory on what is available. It simply lists 
out all available choices for each of the three categories.  Specifically, it 
lists the names and descriptions for all configured locations, networks and 
proxies.


.. _sshconfig create command:

**create** -- Create the SSH config file
----------------------------------------

Create an SSH config file.

Usage::

    sshconfig [options]
    sshconfig [options] create

Normally you can create your SSH config file using ``sshconfig create`` or 
simply ``sshconfig``.  However, special circumstances may require that you 
specify command line options so as to modify the generated config file to meet 
your needs.  For example, if you find yourself in a coffee shop that blocks port 
22, you might create your SSH config file using::

    sshconfig -p 443,80

This tells *sshconfig* to use port 443 or port 80 if available when generating 
the SSH host entries.

Or perhaps you are traveling to the far east, you might want to use your server 
in Tokyo rather than the ones back home::

    sshconfig -l tokyo


.. _sshconfig find command:

**find** -- Find an SSH host configuration
------------------------------------------

Find SSH host configurations whose names contains a substring.

Usage::

    sshconfig find <text>


.. _sshconfig help command:

**help** -- Show Helpful Information
------------------------------------

Shows helpful information for each a command or a topic.

Usage::

    sshconfig help
    sshconfig help <command>
    sshconfig help <topic>

Run ``sshconfig help`` for a list of available commands and topics.


.. _sshconfig show command:

**show** -- Show a SSH Host Configuration
-----------------------------------------

Usage::

    sshconfig [options] show <name>

Shows the SSH host entry to be generated given a host name. This can be used to 
show you how the host entry changes based on various options such as 
``--ports``. This command does not affect your SSH config file.


.. _sshconfig version command:

**version** -- Show SSHConfig Version
-------------------------------------

Usage::

    sshconfig version
