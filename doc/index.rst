SSH Config
==========

:Author: Ken Kundert
:Version: 2.2
:Released: 2022-11-19


Introduction
------------

SSH Config generates an SSH config file adapted to the network you are currently 
using.  In this way, you always use the fastest paths available for your SSH 
related activities (sshfs, email, vnc, mercurial, etc.). You can also easily 
reconfigure SSH to make use of proxies as needed or select certain servers or 
ports based on your location or restrictions with the network.

The following situations are supported:

#. You may give the mac address or addresses for your router or routers and your 
   network will automatically be recognized.
#. You can configure which hostname or IP address is used for a particular host 
   depending on which network you are on. In this way you always use the fastest 
   connection available for each host.
#. You can specify that certain hosts are hidden behind other hosts, so that 
   a SSH proxy should be used to access them.
#. You can specify port forwarding information for each host. Then, two SSH 
   configurations will be created for those hosts, one that includes port 
   forwarding and one that does not. That way, once the port forwards are 
   established, you can open additional shells on that host without SSH trying 
   to create conflicting port forwards.
#. You can enter multiple hostnames or IP addresses and give their locations.  
   Then, if you specify your location, the closest server will be used 
   automatically.
#. You can specify proxy configurations and specify that one should be used for 
   all hosts not on your current network.
#. You can specify port restrictions and have SSH work around them if possible 
   (if your server supports alternative ports).
#. You can configure a default location, proxy, or set of port restrictions for 
   each of your known networks.
#. Once host names are defined, they do not change even though you are using 
   different configurations (different networks, locations, proxies, and port 
   restrictions). In this way you can hard code your host names in applications 
   such as Mercurial or Git, and they automatically adapt to your existing 
   network.
#. The entire application, including the configuration files, are Python code, 
   so you have considerable freedom to change the configuration based on things 
   like the name of the machine or the user when generating the SSH config file.


Trivial Configuration
---------------------

The hosts that you would like to connect to are described in the hosts.conf 
file.  A very simple hosts.conf file would look like this:

.. code-block:: python

   from sshconfig import HostEntry

   class Zeebra(HostEntry):
       user = 'herbie'
       hostname = 'zeebra.he.net'

Hosts are described by directly subclassing HostEntry.  Attributes are added 
that are generally converted to fields in the SSH config file.

The contents of ~/.ssh/config are replaced when you run::

   sshconfig

The above hosts.conf file is converted into the following SSH config file::

   # SSH Configuration for unknown network
   # Generated at 1:04 PM on 22 July 2014.

   #
   # HOSTS
   #

   host zeebra
       user herbie
       hostname zeebra.he.net
       forwardAgent no

The transformation between a host entry in the hosts.conf file and the SSH 
config file could be affected by the network you are on and any command line 
options that are specified to *sshconfig*, but in this case it is not. Notice 
that the class name is converted to lower case when creating the hostname.

In most cases, adding an attribute to the definition of your host simply results 
in that attribute being added the the SSH configuration, so:

.. code-block:: python

   class Zeebra(HostEntry):
       user = 'herbie'
       hostname = 'zeebra.he.net'
       port = 22022

becomes::

   host zeebra
       user herbie
       hostname zeebra.he.net
       port 22022
       forwardAgent no


Installation Requirements
-------------------------

You can download and install the latest
stable version of the code from `PyPI <https://pypi.python.org>`_ using::

    pip3 install --user sshconfig

You can find the latest development version of the source code on
`Github <https://github.com/KenKundert/sshconfig>`_.

Requires in Python3.6 or later.


Related Software
----------------

`AddSSHKeys <https://github.com/KenKundert/addsshkeys>`_ is a Python utility
that allows you to add all of your SSH keys to your agent in one go.


Issues
------

Please ask questions or report problems on
`Github Issues <https://github.com/KenKundert/sshconfig/issues>`_.


Contents
--------

.. toctree::
   :maxdepth: 1

   commands
   configuring
   examples
   releases

*  :ref:`genindex`
