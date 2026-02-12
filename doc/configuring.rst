Configuring
-----------

The configuration of *sshconfig* involves several files contained in 
~/.config/sshconfig directory. Specifically, hosts.conf, locations.conf, 
networks.conf, proxies.conf, and ssh.conf.

networks.conf
"""""""""""""

This file defines your known networks. It need not define all the networks you 
use, only those where you would like to customize the behavior of *sshconfig*.
A typical networks.conf file might look like:

.. code-block:: python

   #
   # Basic Network Configuration
   #
   # Defines known networks. Recognizes networks by the MAC addresses of their 
   # routers.  Can use this information to set default location, ports, 
   # initialization script and proxy.

   from sshconfig import NetworkEntry

   # Characteristics of the known networks
   class Home(NetworkEntry):
       routers = ['a8:93:14:8a:e4:31']   # Router MAC addresses
       location = 'home'

   class Work(NetworkEntry):
       routers = ['f0:90:76:9c:b1:37']   # Router MAC addresses
       location = 'home'

   class WorkWireless(NetworkEntry):
       routers = ['8b:38:10:3c:1e:fe']   # Router MAC addresses
       location = 'home'

   class Library(NetworkEntry):
       # Blocks port 22
       routers = [
           'e4:c7:22:f2:9a:46',  # Wireless
           '00:15:c7:01:a7:00',  # Wireless
           '00:13:c4:80:e2:89',  # Ethernet
           '00:15:c7:01:a7:00',  # Ethernet
       ]
       ports = [80, 443]
       location = 'home'
       init_script = 'unlock_library_network'

   class DC_Peets(NetworkEntry):
       routers = ['e4:15:c4:01:1e:95']  # Wireless
       location = 'washington'
       init_script = 'unlock-peets'

   # Preferred networks, in order. If one of these networks are not available,
   # another will be chosen at random from the available networks.
   PREFERRED_NETWORKS = ['Work']

All of these entries are optional.  Network are searched in the order they are 
given, which can be used to resolve ambiguities.

Subclassing NetworkEntry creates a network description that is described with 
the attributes. A subclass will inherit all the attributes of its parent. The 
following attributes are interpreted.

key:
   Name used when specifying the network. If not present, the class name in 
   lower case is used.

description:
   A description of the network. If not given, the class name is used with the 
   following modifications:
   - underscores are replaced by spaces
   - a space is added to separate a lower case to upper case transition
   - double underscores are replaced by ' - '

routers:
   A list of MAC addresses for the router that are used to identify the network.  
   To find these, connect to the network and run the /sbin/arp command.

location:
   The default setting for the location (value should be chosen from LOCATIONS) 
   when this network is active.

ports:
   The default list of ports that should be available when this network is 
   active.

proxy:
   The name of the proxy to use by default when this network is active.

exclude:
   When on a known network that is using a VPN, you generally want to exclude 
   the known networks to avoid confusion.  Use this setting for the network 
   associated with the VPN to exclude the base network or networks.  For this to 
   work, the network for the VPN must be the preferred network.

nmcli_connection:
   The name used by Network Manager to refer to this network.  This is normally 
   not necessary, however it allows secondary networks to be recognized.  
   Imagine a laptop that has both an ethernet and a wifi connection on different 
   networks.  Only one network will be used as a gateway by the laptop, and the 
   router for that network will be recognized through its MAC address.  Say that 
   this is the ethernet network.  By adding *nmcli_connection* to the wifi 
   network and setting it to the SSID of the access point (that is what *nmcli* 
   uses as the name of the network) you can now access both networks.  Further 
   imagine that the ethernet network is named ‘work’ and the wifi network is 
   named ‘home’.  Finally, imagine that a machine named ‘media’ is located on 
   the ‘home’ network.  If the entry for ‘media’ is given as follows:

   .. code-block:: python

       class Media(HostEntry):
           description = "Media server"
           hostname = {
               'home': '192.168.0.24',
               'default': 'terminus.home',
           }

   If you only provided *routers*, then there would be no match and you would 
   get *terminus.home* as the hostname, meaning that you would reach the media 
   server via the internet.  But if you set *nmcli_connection*, you will get 
   192.168.0.24 as the hostname, meaning that you will reach it directly through 
   your local wifi network.  Thus, use of *nmcli_connection* allows you to use 
   the access point name in addition to the router MAC when determining which 
   hostname to use.

init_script:
   A script that should be run before using this network. May be a string or 
   a list of strings. If it is a list of strings they are joined together to 
   form a command.

   The unlock-peets script is included as an example of such a script. It is 
   used to automate the process of accepting the terms & conditions on the 
   click-through page. Unfortunately, while unlock-peets represents a reasonable 
   example, each organization requires the basic script to be customized to fit 
   their particular click-through pages.

   To write a script it is helpful to understand how the unlocking process 
   works.  The organizations that lock their wifi generally allow your computer 
   to directly connect to their access point, however their firewall is 
   configured to block any network traffic from unapproved devices.  As you 
   connect, they grab the MAC address of your computer's wifi.  They then watch 
   for web requests emanating from your computer, which they then discard and 
   redirect your browser to their router which offers up a page that allows you 
   to accept their terms and conditions.  This page is customized particularly 
   for you: it contains your MAC address. When you accept, your MAC address is 
   returned to the router along with your acceptance, and the router then 
   rewrites its firewall rules to allow your computer to access the internet.  
   After some period of time (an hour? a day?) the rules are discarded and you 
   lose your connection to the Internet.  All of this tremendously abuses 
   Internet protocols, and causes its visitors headaches because this hack is 
   not compatible with HTTPS or VPN traffic. So for it to work, you must request 
   a plain HTTP site with any VPNs disabled, and plain HTTP sites are 
   disappearing.  The headaches this cause seems to provide very little value to 
   anyone. They break the Internet so as to force you to accept their terms and 
   conditions, which they presumably feel protects them from lawsuits, but it is 
   hard to imagine anybody suing the owner of a public wifi for the actions of 
   an anonymous user. But I digress.

   Debugging init scripts can be difficult because once you successfully unlock 
   the wifi, it generally remains unlocked for at least an hour, and maybe until 
   the next day, which limits your ability to test your script.  However, in 
   Linux it is possible to change your MAC address.  If you do so, the router no 
   longer recognizes you and you have to go through the unlock process again, 
   which allows you to thoroughly exercise and debug your script.  To change 
   your MAC address, right-click on the Network Manager applet, and select 'Edit 
   Connection ...', select the connection you are using, and click 'Edit', then 
   copy the 'Device MAC address' into 'Cloned MAC address' and change a few 
   digits. The digits are hexadecimal, so choose values between 0-9A-F. Then 
   click 'Save', 'Close', and restart your network connection.

In addition to the *NetworkEntry* class definitions, this file may also define 
*PREFERRED_NETWORKS*, *ROUTER_MACS*, *NMCLI_CONNS*.

*PREFERRED_NETWORKS*:
   A list of strings that specify the preferred networks. It is useful if your 
   computer can access multiple networks simultaneously, such as when you are 
   using a laptop connected to a wired network but you did not turn off the 
   wireless networking.  SSH is configured for the first network on the 
   *PREFERRED_NETWORKS* list that is available. If none of the preferred 
   networks are available, then an available known network is chosen at random.  
   If no known networks are available, SSH is configured for a generic network.  
   In the example, the *Work* network is listed in the preferred networks 
   because *Work* and *WorkWireless* would often be expected to be available 
   simultaneously, and *Work* is the wired network and is considerably faster 
   than *WorkWireless*.

*ROUTER_MACS*:
   A dictionary that specifies how *sshconfig* can determine the MAC addresss of 
   the available routers.  The following fields can be specified:

   *style*:
        May be either 'ip', 'arp', or 'custom'.  'ip' should be specified when 
        using the *ip neighbor* command is used.  'arp' should be used if the 
        *arp* is used.  And 'custom' should be used if you write your own 
        program to provide the MAC addresses.  Required.
        For all the choices, it is assumed that only one MAC address is provided 
        per line.  For 'arp' and 'custom' you should specify the *column* field.

    *executable*:
        The command to run to generate the MAC addresses. Required.

    *column*:
        The index of the column that holds the MAC address.  The index of the 
        first column is 1.

    Here is the default value::

        ROUTER_MACS = dict(
            style = "ip",
            executable = "ip neighbor",
        )

    Generally using *ip* is preferred.  If the *ip* command is not available you 
    can use::

        ROUTER_MACS = dict(
            style = "arp",
            executable = "/sbin/arp -e",
            column = "3",
        )

    or::

        ROUTER_MACS = dict(
            style = "arp",
            executable = "arp -a",
            column = "4",
        )

    This last version should be used on MacOS.


*NMCLI_CONNS*:
   Command to use to query the network names from Network Manager.  The default 
   is *None*, in which case *nmcli* is not run at all, with the result that any 
   *nmcli_connection* attributes on the network entries are ignored.  You should 
   set it to “nmcli -t -f name connection show --active” on those hosts that 
   need it.  You can use something like this

   .. code-block:: python

       from sshconfig import gethostname

       if gethostname()  in ['laptop']:
           NMCLI_CONNS = "nmcli -t -f name connection show --active"


ssh.conf
""""""""

This file allows you to control the entries in your SSH configuration file.
A typical ssh.conf file might look like:

.. code-block:: python

   # Location of output file (must be an absolute path)
   CONFIG_FILE = "~/.ssh/config"

   # Don't scramble known_hosts file on trusted hosts.
   TRUSTED_HOSTS = ['lucifer']

   # Attribute overrides for all hosts
   OVERRIDES = """
       Ciphers aes256-ctr,aes128-ctr,arcfour256,arcfour,aes256-cbc,aes128-cbc
   """.strip()

   # Attribute defaults for all hosts
   DEFAULTS = """
       ForwardX11 no

       # This will keep a seemingly dead connection on life support for 10 
       # minutes before giving up on it.
       TCPKeepAlive no
       ServerAliveInterval 60
       ServerAliveCountMax 10

       # Enable connection sharing
       ControlMaster auto
       ControlPath /tmp/ssh_mux_%h_%p_%r
   """.strip()

All of these entries are optional.  The following attributes are interpreted.

*CONFIG_FILE*:
    A string that specifies path to the SSH config file. If not given, 
    ~/.ssh/config is used.  The path to the SSH config file should be an 
    absolute path.

*TRUSTED_HOSTS*:
    A list of strings that specifies the host names of trusted hosts. The 
    *known_hosts* file is not scrambled on known hosts. Generally you should 
    only trust hosts that you control. If you do not scramble your *known_hosts*
    file they someone with root privileges could examine you *known_hosts* file 
    and determine which hosts you are using.

*OVERRIDES*:
    A string that specifies the SSH settings that should be used on all hosts,  
    overriding conflicting settings specified in the host entry.  They are 
    simply added to the top of the SSH config file.  Do not place ForwardAgent 
    in OVERRIDES.  It will be added on the individual hosts and only set to yes 
    if they are trusted.

*DEFAULTS*:
    A string that specifies the SSH settings that should be used on all hosts,
    without overriding conflicting settings specified in the host entry.  They 
    are added to the bottom of the SSH config file.

    It is a good idea to add your default algorithms to this entry. You might 
    want to consult `stribika 
    <https://stribika.github.io/2015/01/04/secure-secure-shell.html>`_ when 
    determining which algorithms to use.

In addition, the following are useful when supporting machines with older 
versions of SSH that might not have all the best algorithms.

*AVAILABLE_CIPHERS*:
    A list of available ciphers. If a cipher is specified on a host entry that 
    is not in this list, it is ignored when creating the SSH configuration.

*AVAILABLE_MACS*:
    A list of available MACs. If a MAC is specified on a host entry that is not 
    in this list, it is ignored when creating the SSH configuration.

*AVAILABLE_HOST_KEY_ALGORITHMS*:
    A list of available host key algorithms. If a host key algorithm  is 
    specified on a host entry that is not in this list, it is ignored when 
    creating the SSH configuration.

*AVAILABLE_KEX_ALGORITHMS*:
    A list of available key exchange algorithms. If a key exchange algorithm is 
    specified on a host entry that is not in this list, it is ignored when 
    creating the SSH configuration.

The following settings allow you to filter out unusable host entries.

*BLOCKED_PORTS*:
    A list of port numbers that are blocked by the local host.  This is useful 
    if host sits behind an oppressive firewall that blocks certain ports.

    Often using the *ports* setting on the network is a better approach to 
    blocked ports.

*BLOCKED_PORT_WARNING*:
    Issue a warning if a host has only blocked ports.

*DISCARD_ENTRIES*:
    A list of conditions that would result in a host entry to be discarded.  It 
    takes the following values:

    'without_ports':
        If, due to the presence of blocked ports, a host has no valid ports 
        available, the host entry will be discarded.

    'without_identities':
        If the identity file specified for a host is not present the host entry 
        is discarded.


proxies.conf
""""""""""""

This file allows you to define any non-SSH proxies that you might want to use.
A typical proxies.conf file might look like:

.. code-block:: python

   # Known proxies
   PROXIES = dict(
       work_proxy = 'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80',
       school_proxy = 'proxytunnel -q -p sproxy.fna.learning.edu:1080 -d %h:%p',
       tunnelr_proxy = 'ssh tunnelr -W %h:%p',
   )

Once defined, these proxies can be activated from the command line.

All of these entries are optional.  The following attributes are interpreted.

*PROXIES*:
   A dictionary that defines each proxy.  Each entry consists of a name and 
   string that would be used directly as the argument for a *proxyCommand* SSH 
   host attribute.  These names can then be specified on the command line so 
   that all hosts use the proxy.

   It is not necessary to add SSH hosts as proxies as with *tunnelr_proxy* above 
   as you can always specify any SSH host as a proxy, and if you do you will get 
   this proxyCommand by default.  The only benefit that adding this entry to 
   PROXIES provides is that *tunnelr_proxy* is listed in the available proxies 
   by *sshconfig settings*.

Once the available proxies have been specified in *PROXIES*, you can activate it 
using the ``--proxy`` (or ``-P``) command line argument to specify the proxy by 
name.  For example:

.. code-block:: python

   PROXIES = {
       'work_proxy':   'corkscrew webproxy.ext.workinghard.com 80 %h %p',
       'school_proxy': 'corkscrew sproxy.fna.learning.edu 1080 %h %p',
   }

Two HTTP proxies are described, the first capable of bypassing the corporate 
firewall and the second does the same for the school's firewall. Each is 
a command that takes its input from stdin and produces its output on stdout.  
The program `corkscrew <https://github.com/bryanpkc/corkscrew>`_ is designed to 
proxy a TCP connection through an HTTP proxy.  The first two arguments are the 
host name and port number of the proxy.  corkscrew connects to the proxy and 
passes the third and fourth arguments, the host name and port number of desired 
destination.

There are many alternatives to *corkscrew*.  One is *socat*:

.. code-block:: python

   PROXIES = {
       'work_proxy':   'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80',
       'school_proxy': 'socat - PROXY:sproxy.fna.learning.edu:%h:%p,proxyport=1080',
   }

Another alternative is `proxytunnel <https://proxytunnel.sourceforge.io>`_:

.. code-block:: python

   PROXIES = {
       'work_proxy':   'proxytunnel -q -p webproxy.ext.workinghard.com:80 -d %h:%p',
       'school_proxy': 'proxytunnel -q -p sproxy.fna.learning.edu:1080 -d %h:%p',
   }

For more information on configuring proxies see :ref:`proxies <proxies>`.

When at work, you should generate your SSH config file using::

   sshconfig --proxy=work_proxy

or::

   sshconfig --Pwork_proxy

You can get a list of the pre-configured proxies using::

   sshconfig --available

It is also possible to use SSH hosts as proxies. For example, when at an 
internet cafe that blocks port 22, you can work around the blockage even if your 
host only supports 22 using::

   sshconfig --ports=80 --proxy=tunnelr

or::

   sshconfig -p80 --Ptunnelr

Using the --proxy command line argument adds a *proxyCommand* entry to every 
host that does not already have one (except the host being used as the proxy).  
In that way, proxies are automatically chained.

Rather than always specifying the proxy by command line, you can specify a proxy 
on the *NetworkEntry* for you network.  If you do, that proxy will be used by 
default when on that network for all hosts that are not on that network. A host 
is said to be on the network if the hostname is specifically given for that 
network. For example, assume you have a network configured for work:

.. code-block:: python

   class Work(NetworkEntry):
       # Work network
       routers = ['78:92:4d:2b:30:c6']
       proxy = 'work_proxy'

Then assume you have a host that is not configured for that network (Home) and 
one that is (Farm):

.. code-block:: python

   class Home(HostEntry):
       description = "Home Server"
       aliases = ['lucifer']
       user = 'herbie'
       hostname = {
           'home': '192.168.0.1',
           'default': '74.125.232.64'
       }

   class Farm(HostEntry):
       description = "Entry Host to Machine farm"
       aliases = ['mercury']
       user = 'herbie'
       hostname = {
           'work': '192.168.1.16',
           'default': '231.91.164.92'
       }

When on the work network, when you connect to home you will use the proxy and 
when you connect to farm, you will not.


locations.conf
""""""""""""""

This file allows you to define any locations that you might frequent.  A typical 
locations.conf file might look like:

.. code-block:: python

   # My locations
   LOCATIONS = dict(
      home = 'San Francisco',
      washington = 'Washington DC',
      toulouse = 'Toulouse',
   )

The *LOCATIONS* entry is optional.  It is a dictionary of place names and 
descriptions.  It is needed only if expect to change the server you access based 
on your location.


hosts.conf
""""""""""

A typical hosts.conf file generally contains many host specifications.

You subclass *HostEntry* to specify a host and then add attributes to configure 
its behavior.  Information you specify is largely just placed in the SSH config 
file unmodified except:

1. The class name is converted to lower case to make it easier to type.
2. 'forwardAgent' is added and set based on whether the host is trusted.
3. Any attribute that starts with underscore (_) is ignored and so can be used 
   to hold intermediate values.

In most cases, whatever attributes you add to your class get converted into 
fields in the SSH host description. However, there are several attributes that 
are intercepted and used by *sshconfig*. They are:

*description*:
   A string that is added as a comment above the SSH host description.

*aliases*:
   A list of strings, each of which is added to the list of names that can be 
   used to refer to this host.

*trusted*:
   Indicates that the host should be trusted (it is fully under your
   control, no untrusted parties have root access).  This enables agent
   forwarding for the host.  If you are using agent forwarding, then it is 
   possible for someone with root permissions to access and use your agent. So 
   you should only mark a host as trusted if you trust the individuals that have 
   administrative access on that machine.

*guests*:
   A list of machines that are accessed using this host as a proxy.

Here is a example:

.. code-block:: python

   class DigitalOcean(HostEntry):
       description = "Web server"
       aliases = ['do', 'web']
       user = 'herbie'
       hostname = '107.170.65.89'
       identityFile = 'digitalocean'

This results in the following entry in the SSH config file:

.. code-block:: python

   # Web server
   host digitalocean do web
       user herbie
       hostname 107.170.65.89
       identityFile /home/herbie/.ssh/digitalocean
       forwardAgent no

When specifying the *identityFile*, you can either use an absolute or relative 
path. The relative path will be relative to the directory that contains the SSH 
config file. Specifying *identityFile* results in *identitiesOnly* and 
*pubkeyAuthentication* being added.  *identityFile* may be a string, or a list 
of strings.  Only those files that actually exist will be used.

*SSHconfig* provides two utility functions that you can use in your hosts file 
to customize it based on either the hostname or username that are being used 
when *sshconfig* is run. They are *gethostname()* and *getusername()* and both 
can be imported from *sshconfig*. For example, I generally use a different 
identity (SSH key) from each machine I operate from. To implement this, at the 
top of my hosts file I have:

.. code-block:: python

   from sshconfig import gethostname

   class DigitalOcean(HostEntry):
       description = "Web server"
       aliases = ['do', 'web']
       user = 'herbie'
       hostname = '107.170.65.89'
       identityFile = gethostname()


Ports
'''''

The default SSH port is 22. However, many ISPs block port 22. For examples, your 
employer may block port 22 to discourage the use of SSH, which makes them 
nervous. Coffee shops also have a habit of blocking port 22. To work around 
these blocks, it is useful to configure SSH to respond to other ports. However, 
if port 22 is blocked, there is a good chance other ports are blocked as well.  
For example, one company I was associated with blocked all but ports 80, 443, 
and 554 (http, https, and real-time streaming protocol) (554 was used by the 
RealPlayer, which was once heavily used but no longer, so port 554 traffic is no 
longer allowed through).  A coffee shop I visited blocked everything but ports 
80 and 443.  Finally, while it is rare to find port 80 blocked, it is common for 
the ISP to pass all port 80 traffic through a transparent http proxy. This would 
prevent port 80 from being used by SSH.  So, if at a very minimum, if you are 
going to configure a server to support multiple SSH ports, you should try to 
include port 443 in your list.  If you would like to support more, I recommend 
22 (SSH), 80 (HTTP), 443 (HTTPS).  In my experience, these are the least likely 
to be blocked.

If a host is capable of accepting connections on more than one port, you should 
use the *choose()* method of the ports object to select the appropriate port.

For example:

.. code-block:: python

   from sshconfig import HostEntry, ports

   class Tunnelr(HostEntry):
       description = "Proxy server"
       user = 'kundert'
       hostname = 'fremont.tunnelr.com'
       port = ports.choose([22, 80, 443])
       identityFile = 'tunnelr'

An entry such as this would be used when sshd on the host has been configured to 
accept SSH traffic on a number of ports, in this case, ports 22, 80 and 443.

The actual port used is generally the first port given in the list provided to 
*choose()*.  However this behavior can be overridden with the --ports (or -p) 
command line option.  For example::

   sshconfig --ports=443,80

or::

   sshconfig -p443,80

This causes ports.choose() to return the first port given in the --ports 
specification if it is given anywhere in the list of available ports given as an 
argument to choose(). If the first port does not work, it will try to return the 
next one given, and so on. So in this example, port 443 would be returned.  If 
-p80,443 were specified, then port 80 would be used.

You can specify as many ports as you like in a --ports specification, just 
separate them with a comma and do not add spaces.

In this next example, we customize the proxy command based on the port chosen:

.. code-block:: python

   class Home(HostEntry):
       description = "Home server"
       user = 'herbie'
       hostname = {
           'home': '192.168.1.32',
           'default': '231.91.164.05'
       }
       port = ports.choose([22, 80])
       if port in [80]:
           proxyCommand = 'socat - PROXY:%h:127.0.0.1:22,proxyport=%p'
       identityFile = 'my2014key'
       dynamicForward = 9999

An entry such as this would be used if sshd is configured to directly accept 
traffic on port 22, and Apache on the same server is configured to act as 
a proxy for ssh on port 80 (see `SSH via HTTP 
<http://www.nurdletech.com/linux-notes/ssh/via-http.html>`_).

If you prefer, you can use proxytunnel rather than socat in the proxy command::

   proxyCommand = 'proxytunnel -q -p %h:%p -d 127.0.0.1:22'

You can also use this command for port 443, but you may need to add the -E 
option if encryption is enabled on port 443.

An alternate scenario is that you need to use a port that the host does not 
support.  In this case you would use another server as an intermediate jump 
host.  For example:

.. code-block:: python

   class Backups(HostEntry):
       description = "Backups server"
       user = 'dumper'
       hostname = '143.18.194.32'
       port = ports.choose([22, 80, 443])
       if port in [80, 443]:
           proxyJump = 'tunnelr'
           port = 22
       identityFile = 'my2014key'

In this example *Backups* indicates that it supports ports 22, 80 and 443 even 
though the server itself only supports port 22. However, if port 80 or port 443 
is selected, then *tunnelr* is configured as a jump server. The port must be 
reset to port 22 so that the jump server connects to port 22 on the Backups 
server.


Attribute Descriptions
''''''''''''''''''''''

Most attributes can be given as a two element tuple. The first value in the pair 
is used as the value of the attribute, and the second should be a string that is 
added as a comment to describe the attribute. For example:

.. code-block:: python

   hostname = '65.19.130.60', 'fremont.tunnelr.com'

is converted to::

   hostname 65.19.130.60
      # fremont.tunnelr.com


Hostname
''''''''

The hostname may be a simple string, or it may be a dictionary. If given as 
a dictionary, each entry will have a string key and string value. The key would 
be the name of the network (in lower case) and the value would be the hostname 
or IP address to use when on that network. One of the keys may be 'default', 
which is used if the network does not match one of the given networks. For 
example:

.. code-block:: python

   class Home(HostEntry):
       hostname = {
           'home': '192.168.0.1',
           'default': '74.125.232.64'
      }

When on the home network, this results in an ssh host description of::

   host home
       hostname 192.168.0.1
       forwardAgent no

When not on the home network, it results in an ssh host description of::

   host home
       hostname 74.125.232.64
       forwardAgent no

The ssh config file entry for this host will not be generated if not on one of 
the specified networks and if default is not specified.

It is sometimes appropriate to set the hostname based on which host you are on 
rather than on which network. For example, if a *sshconfig* host configuration 
file is shared between multiple machines, then it is appropriate to give the 
following for a host which may become localhost:

.. code-block:: python

   class Home(HostEntry):
       if gethostname() == 'home':
           hostname = '127.0.0.1'
       else:
           hostname = '192.168.1.4'


Location
''''''''

It is also possible to choose the hostname based on location. The user specifies 
location using::

   sshconfig --location=washington

or::

   sshconfig -lwashington

You can get a list of the known locations using::

   sshconfig settings

To configure support for locations, you first specify your list of known 
locations in *LOCATIONS* (in *locations.conf*):

.. code-block:: python

   LOCATIONS = {
      'home': 'San Francisco',
      'washington': 'Washington DC',
      'toulouse': 'Toulouse',
   }

Then you must configure your hosts to use the location. To do so, you use the 
choose() method to set the location. The choose() method requires three things:

1. A dictionary that gives hostnames or IP addresses and perhaps descriptive 
   comment as a function of the location. These locations are generally specific 
   to the host.
2. Another dictionary that maps the user's locations into the host's locations.
3. A default location.

For example:

.. code-block:: python

   from sshconfig import HostEntry, locations, ports

   class Tunnelr(HostEntry):
       description = "Commercial proxy server"
       user = 'kundert'
       hostname = locations.choose(
          locations = {
              'sf':          ("65.19.130.60",    "Fremont, CA, US (fremont.tunnelr.com)"),
              'la':          ("173.234.163.226", "Los Angeles, CA, US (la.tunnelr.com)"),
              'wa':          ("209.160.33.99",   "Seattle, WA, US (seattle.tunnelr.com)"),
              'tx':          ("64.120.56.66",    "Dallas, TX, US (dallas.tunnelr.com)"),
              'va':          ("209.160.73.168",  "McLean, VA, US (mclean.tunnelr.com)"),
              'nj':          ("66.228.47.107",   "Newark, NJ, US (newark.tunnelr.com)"),
              'ny':          ("174.34.169.98",   "New York City, NY, US (nyc.tunnelr.com)"),
              'london':      ("109.74.200.165",  "London, UK (london.tunnelr.com)"),
              'uk':          ("31.193.133.168",  "Maidenhead, UK (maidenhead.tunnelr.com)"),
              'switzerland': ("178.209.52.219",  "Zurich, Switzerland (zurich.tunnelr.com)"),
              'sweden':      ("46.246.93.78",    "Stockholm, Sweden (stockholm.tunnelr.com)"),
              'spain':       ("37.235.53.245",   "Madrid, Spain (madrid.tunnelr.com)"),
              'netherlands': ("89.188.9.54",     "Groningen, Netherlands (groningen.tunnelr.com)"),
              'germany':     ("176.9.242.124",   "Falkenstein, Germany (falkenstein.tunnelr.com)"),
              'france':      ("158.255.215.77",  "Paris, France (paris.tunnelr.com)"),
          },
          maps={
              'home':       'sf',
              'washington': 'va',
              'toulouse':   'france',
          },
          default='sf'
       )
       port = ports.choose([
           22, 21, 23, 25, 53, 80, 443, 524, 5555, 8888
       ])
       identityFile = 'tunnelr'

Now if the user specifies --location=washington on the command line, then it is 
mapped to the host location of va, which becomes mclean.tunnelr.com 
(209.160.73.168).  Normally, users are expected to choose a location from the 
list given in *LOCATIONS*. As such, every *maps* argument should support each of 
those locations.  However, a user may given any location they wish. If the 
location given is not found in *maps*, then it will be looked for in locations, 
and if it is not in locations, the default location is used.


Forwards
''''''''

When forwards are specified, two SSH host entries are created. The first does 
not include forwarding. The second has the same name with '-tun' appended, and 
includes the forwarding. The reason this is done is that once one connection is 
setup with forwarding, a second connection that also attempts forwarding will 
produce a series of error messages indicating that the ports are in use and so 
cannot be forwarded. Instead, you should only use the tunneling version once 
when you want to set up the port forwards, and you the base entry at all other 
times. Often forwarding connections are setup to run in the background as 
follows::

   ssh -f -N home-tun

If you have set up connection sharing using *ControlMaster* and then run::

   ssh home

SSH will automatically share the existing connection rather than starting a new 
one.

Both local and remote forwards should be specified as lists. The lists can 
either be simple strings, or can be tuple pairs if you would like to give 
a description for the forward. The string that describes the forward has the 
syntax: '[host1:]port1 host2:port2' where each host can be either a host name or 
an IP address and each port is a port number.  *host1* is optional and defaults 
to *localhost*.

With `local forwards 
<https://www.ssh.com/academy/ssh/tunneling-example#local-forwarding>`_ *host1* 
and *port1* are given from the perspective of the local host (the host from 
which you initiated the ssh connection) and *host2* and *port2* are given from 
the perspective of the remote host (the host to which you are connecting).  
Imagine you are on the host *earth* and using ssh to connect to the host *mars* 
with a local forward specification of 'localhost:8080 localhost:80'.  Then, 
anything sent to port 8080 on *earth* is forwarded to port 80 on *mars*.  Once 
such a connection is in place, navigating to 'http://localhost:80' in your 
browser allows you to view pages from *marse* if it has a webserver monitoring 
port 80.  Notice that *localhost* was used twice in the forwarding 
specification, but each represented a different host.

With `remote forwards 
<https://www.ssh.com/academy/ssh/tunneling-example#remote-forwarding>`_ *host1* 
and *port1* are given from the perspective ot the remote host (the host to which 
you are connecting) and *host2* and *port2* are given from the perspective of 
the local host (the host from which you initiated the ssh connection).  Imagine 
you are on the host *earth* and using ssh to connect to the host *mars*.  Then 
a remote forward specification of 'localhost:2222 localhost:22' connect port 
2222 on *mars* to port 22 on *earch*.  Once such a connection is in place, using 
'ssh -p 2222 localhost' from *mars* connects you to *earth*.

The optional first host specifies what machines can connect to the port.
If the *GatewayPorts* setting is set to *yes* on the SSH server, then forwarded 
ports are accessible to any machine on the network. If the *GatewayPorts* 
setting is *no*, then the forwarded ports are only available from the local 
host.  However, if *GatewayPorts* is set to *clientspecified*, then the 
accessibility of the forward address is set by the local host specified.  For 
example:

=============================== ==============================
5280 localhost:5280             accessible only from localhost
localhost:5280 localhost:5280   accessible only from localhost
\*:5280 localhost:5280          accessible from anywhere
0.0.0.0:5280 localhost:5280     accessible from anywhere
lucifer:5280 localhost:5280     accessible from lucifer
192.168.0.1:5280 localhost:5280 accessible from 192.168.0.1
=============================== ==============================

*GatewayPorts* is a setting you specify to the SSH server.  Thus, it should 
placed in /etc/ssh/sshd_config on the host you are connecting to.

The VNC function is provided for converting VNC host and display number 
information into a setting suitable for a forward. You can give the local 
display number, the remote display number, and the remote host name (from the 
perspective of the remote ssh server) and the local host name.  For example:

.. code-block:: python

   VNC(lclDispNum=1, rmtHost='localhost', rmtDispNum=12)

This allows a local VNC client viewing display 1 to show the VNC server running 
on display 12 of the SSH server host.

If you give a single number, it will use it for both display numbers.  If you 
don't give a name, it will use *localhost* as the remote host (in this case 
*localhost* represents the remote ssh server).  So the above VNC section to the 
local forwards could be shortened to:

.. code-block:: python

   VNC(12)

if you configured the local VNC client to connect to display 12.

An example of many of these features:

.. code-block:: python

   from sshconfig import HostEntry, ports, locations, VNC

   class Home(HostEntry):
       description = "Lucifer Home Server"
       aliases = ['lucifer']
       user = 'herbie'
       hostname = {
           'home': '192.168.0.1',
           'default': '74.125.232.64'
       }
       port = ports.choose([22, 80])
       if port in [80]:
           proxyCommand = 'socat - PROXY:%h:127.0.0.1:22,proxyport=%p'
       trusted = True
       identityFile = gethostname()
       localForward = [
           ('30025 localhost:25',  "Mail - SMTP"),
           ('30143 localhost:143', "Mail - IMAP"),
           ('34190 localhost:4190', "Mail - Sieve"),
           ('39100 localhost:9100', "Printer"),
           (VNC(lclDispNum=1, rmtDispNum=12), "VNC"),
       ]
       dynamicForward = 9999

On a foreign network it produces::

   # Lucifer Home Server
   host home lucifer
       user herbie
       hostname 74.125.232.64
       port = 22
       identityFile /home/herbie/.ssh/teneya
       forwardAgent yes

   # Lucifer Home Server (with forwards)
   host home-tun lucifer-tun
       user herbie
       hostname 74.125.232.64
       port = 22
       identityFile /home/herbie/.ssh/teneya
       forwardAgent yes
       localForward 11025 localhost:25
           # Mail - SMTP
       localForward 11143 localhost:143
           # Mail - IMAP
       localForward 14190 localhost:4190
           # Mail - Sieve
       localForward 19100 localhost:9100
           # Printer
       localForward 5901 localhost:5912
           # VNC
       dynamicForward 9999
       exitOnForwardFailure yes


Guests
''''''

The 'guests' attribute is a list of hostnames that would be accessed by using 
the host being described as a proxy. The attributes specified are shared with 
its guests (other than hostname, port, and port forwards).  The name used for 
the guest in the ssh config file would be the hostname combined with the guest 
name using a hyphen.

For example:

.. code-block:: python

   class Farm(HostEntry):
       description = "Entry Host to Machine farm"
       aliases = ['earth']
       user = 'herbie'
       hostname = {
           'work': '192.168.1.16',
           'default': '231.91.164.92'
       }
       trusted = True
       identityFile = 'my2014key'
       guests = [
           ('jupiter', "128GB Compute server"),
           ('saturn', "96GB Compute server"),
           ('neptune', "64GB Compute server"),
       ]
       localForward = [
           (VNC(dispNum=21, rmtHost=jupiter), "VNC on Jupiter"),
           (VNC(dispNum=22, rmtHost=saturn), "VNC on Saturn"),
           (VNC(dispNum=23, rmtHost=neptune), "VNC on Neptune"),
       ]

On a foreign network produces::

   # Entry Host to Machine Farm
   host farm earth
       user herbie
       hostname 231.91.164.92
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent yes

   # Entry Host to Machine Farm (with port forwards)
   host farm-tun earth-tun
       user herbie
       hostname 231.91.164.92
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent yes
       localForward 5921 jupiter:5921
           # VNC on jupiter
       localForward 5922 saturn:5922
           # VNC on Saturn
       localForward 5923 neptune:5923
           # VNC on Neptune

   # 128GB Compute Server
   host farm-jupiter
       hostname jupiter
       proxyCommand ssh host -W %h:%p
       user herbie
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent yes

   # 96GB Compute Server
   host farm-saturn
       hostname saturn
       proxyCommand ssh host -W %h:%p
       user herbie
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent yes

   # 64GB Compute Server
   host farm-netpune
       hostname neptune
       proxyCommand ssh host -W %h:%p
       user herbie
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent yes


Subclassing
'''''''''''

Subclassing is an alternative to guests that gives more control over how the 
attributes are set. When you create a host that is a subclass of another host 
(the parent), the parent is configured to be the proxy and only the 'user' and 
'identityFile' attributes are copied over from the parent, but these can be 
overridden locally.

For example:

.. code-block:: python

   class Jupiter(Farm):
       description = "128GB Compute Server"
       hostname = 'jupiter'
       remoteForward = [
           ('14443 localhost:22', "Reverse SSH tunnel used by sshfs"),
       ]

Notice, that Jupiter subclasses Farm, which was described in an example above.  
This generates::

   # 128GB Compute Server
   host jupiter
       user herbie
       hostname jupiter
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent no
       proxyCommand ssh farm -W %h:%p

   # 128GB Compute Server (with port forwards)
   host jupiter-tun
       user herbie
       hostname jupiter
       identityFile /home/herbie/.ssh/my2014key
       forwardAgent no
       proxyCommand ssh farm -W %h:%p
       remoteForward 14443 localhost:22

If you contrast this with farm-jupiter above, you will see that the name is 
different, as is the trusted status (farm-jupiter inherits 'trusted' from Host, 
whereas jupiter does not). Also, there are two versions, one with port 
forwarding and one without.


local.conf
""""""""""

This file may contain any other setting.  It is used to contain local overrides.  
Here the assumption is that you are copying your configuration files to multiple 
machines and you need to override certain settings on select machines.

