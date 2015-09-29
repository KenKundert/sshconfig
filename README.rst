SSH Config
==========

Installation Requirements
-------------------------

Uses docopt::

   yum install python-docopt  (or python3-docopt)

or::

   pip install docopt

Also requires my scripts package::

   git clone https://github.com/KenKundert/scripts.git
   cd scripts
   ./install


Introduction
------------
SSH Config generates an ssh config file adapted to the network you are currently 
using.  In this way, you always use the fastest paths available for your ssh 
related activities (sshfs, email, vnc, mercurial, etc.). You can also easily 
reconfigure ssh to make use of proxies as needed or select certain servers or 
ports based on your location or restrictions on the network.

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

The hosts that you would like to connect to are described in the hosts.py file.  
A very simple hosts.py file would look like this::

   from sshconfig import HostEntry

   class Zeebra(HostEntry):
       user = 'herbie'
       hostname = 'zeebra.he.net'

Hosts are described by directly subclassing HostEntry.  Attributes are added 
that are generally converted to fields in the ssh config file.  

The contents of ~/.ssh/config are replaced when you run::

   gensshconfig

The above hosts.py file is converted into the following ssh config file::

   # SSH Configuration for generic network
   # Generated at 1:04 PM on 22 July 2014.

   #
   # HOSTS
   #

   host zeebra
       user herbie
       hostname zeebra.he.net
       forwardAgent no

The transformation between a host entry in the hosts.py file and the ssh config 
file could be affected by the network you are on and any command line options 
that are specified to gensshconfig, but in this case it is not. Notice that the 
class name is converted to lower case when creating the hostname.

Configuration
-------------

The configuration of sshconfig involves two files, config.py and hosts.py.  In 
config.py you describe networks, proxies, locations, and general defaults. In 
hosts.py, you describe the machines you would like to connect to on a regular 
basis.

Config
''''''
A typical config.py file would start with would look like::

   #
   # SSH Config -- Basic Network Configuration
   #
   # Defines known networks. Recognizes networks by the MAC addresses of their 
   # routers, can use this information to set default location, ports, init 
   # script and proxy.
   #

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
       init_script = 'activate_library_network'

   class DC_Peets(NetworkEntry):
       routers = ['e4:15:c4:01:1e:95']  # Wireless
       location = 'washington'
       init_script = 'unlock-peets'

   # Preferred networks, in order. If one of these networks are not available,
   # another will be chosen at random from the available networks.
   PREFERRED_NETWORKS = ['Work']

   # Location of output file (must be an absolute path)
   CONFIG_FILE = "~/.ssh/config"

   # Attribute overrides for all hosts
   OVERRIDES = """
       Ciphers aes256-ctr,aes128-ctr,arcfour256,arcfour,aes256-cbc,aes128-cbc
   """

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
   """

   # Known proxies
   PROXIES = {
       'work_proxy': 'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80',
       'school_proxy': 'proxytunnel -q -p sproxy.fna.learning.edu:1080 -d %h:%p',
       'tunnelr_proxy': 'ssh tunnelr -W %h:%p',
           # it is not necessary to add tunnelr as a proxy, you can always 
           # specify a host as a proxy, and if you do you will get this 
           # proxyCommand by default. The only benefit adding this entry to 
           # PROXIES provides is that tunnelr is listed in the available proxies 
           # when using the --available command line option.
   }

   # My locations
   LOCATIONS = ['home', 'washington', 'toulouse']

All of these entries are optional.

Subclassing NetworkEntry creates a network description that is described with 
the attributes. A subclass will inherit all the attributes of its parent. The 
following attributes are interpreted.

routers:
   A list of MAC addresses for the router that are used to identify the network.  
   To find these, connect to the network and run the /sbin/arp command.

location:
   The default setting for the location (value should be chosen from LOCATIONS) 
   when this network is active.

ports:
   The default list of ports that should be available when this network is 
   active.

init_script:
   A script that should be run when on this network. May be a string or a list 
   of strings. If it is a list of strings they are joined together to form 
   a command.

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
   loose your connection to the Internet.  All of this tremendously abuses 
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
   
proxy:
   The name of the proxy to use by default when this network is active.

PREFERRED_NETWORKS specifies a list of preferred networks. It is useful your 
computer can access multiple networks simultaneously, such as when you are using 
a laptop connected to a wired network but you did not turn off the wireless 
networking.  SSH is configured for the first network on the PREFERRED_NETWORKS 
list that is available. If none of the preferred networks are available, then an 
available known network is chosen at random. If no known networks are available, 
SSH is configured for a generic network. In the example, the *Work* network is 
listed in the preferred networks because *Work* and *WorkWireless* would 
expected to often be available simultaneously, and *Work* is the wired network 
and is considerably faster than *WorkWireless*.

CONFIG_FILE specifies the name of the ssh config file; the default is 
~/.ssh/config. The path to the SSH config file should be an absolute path.

OVERRIDES contains ssh directives that are simply added to the top of the ssh 
config file.  Such settings override any settings specified in the host entries.  
Do not place ForwardAgent in OVERRIDES.  It will be added on the individual 
hosts and only set to yes if they are trusted.

DEFAULTS contains ssh directives that are added to the bottom of the ssh config 
file.  Such settings act as defaults.

PROXIES allows you to give names to proxyCommand values. These names can then be 
specified on the command line so that all hosts use the proxy.

LOCATIONS is the list of place names where you are likely to be located. It is 
needed only if you use the locations feature.


Hosts
'''''
A more typical hosts.py file would generally contain many host specifications.

You subclass HostEntry to specify a host and then add attributes to configure 
its behavior.  Information you specify is largely just placed in the ssh config 
file unmodified except:

1. The class name is converted to lower case to make it easier to type.
2. 'forwardAgent' is added and set based on whether the host is trusted.
3. Any attribute that starts with underscore (_) is ignored and so can be used 
   to hold intermediate values.

In most cases, whatever attributes you add to your class get converted into 
fields in the ssh host description. However, there are several attributes that 
are intercepted and used by SSH Config. They are:

description:
   A string that is added as a comment above the ssh host description.

aliases:
   A list of strings, each of which is added to the list of names that can be 
   used to refer to this host.

trusted:
   Indicates that the base host should be trusted. Currently that means that 
   agent forwarding will be configured for the non-tunneling version of the 
   host.

tun_trusted:
   Indicates that the tunneling version of the host should be trusted. Currently 
   that means that agent forwarding will be configured for the tunneling version 
   of the host.

guests:
   A list of machines that are accessed using this host as a proxy.

Here is a example::

   class DigitalOcean(HostEntry):
       description = "Web server"
       aliases = ['do', 'web']
       user = 'herbie'
       hostname = '107.170.65.89'
       identityFile = 'digitalocean'

This results in the following entry in the ssh config file::

   # Web server
   host digitalocean do web
       user herbie
       hostname 107.170.65.89
       identityFile /home/herbie/.ssh/digitalocean
       identitiesOnly yes
       forwardAgent no

When specifying the identityFile, you can either use an absolute or relative 
path. The relative path will be relative to the directory that will contain the 
ssh config file. Specifying identityFile results in identitiesOnly being added.

SSHconfig provides two utility functions that you can use in your hosts file to 
customize it based on either the hostname or username that are being used when 
gensshconfig is run. They are gethostname() and getusername() and both can be 
imported from sshconfig. For example, I generally use a different identity (ssh 
key) from each machine I operate from. To implement this, at the top of my hosts 
file I have::

   from sshconfig import gethostname

   class DigitalOcean(HostEntry):
       description = "Web server"
       aliases = ['do', 'web']
       user = 'herbie'
       hostname = '107.170.65.89'
       identityFile = gethostname()


Ports
'''''

If a host is capable of accepting connections on more than one port, you should 
use the choose() method of the ports object to select the appropriate port.

For example::

   from sshconfig import HostEntry, ports

   class Tunnelr(HostEntry):
       description = "Proxy server"
       user = 'kundert'
       hostname = 'fremont.tunnelr.com'
       port = ports.choose([22, 80, 443])
       identityFile = 'tunnelr'

An entry such as this would be used when sshd on the host has been configured to 
accept ssh traffic on a number of ports, in this case, ports 22, 80 and 443.

The actual port used is generally the first port given in the list provided to 
choose(). However this behavior can be overridden with the --ports (or -p) 
command line option.  For example::

   gensshconfig --ports=80,443

or::

   gensshconfig -p80,443

This causes ports.choose() to return the first port given in the --ports 
specification if it is given anywhere in the list of available ports given as an 
argument to choose(). If the first port does not work, it will try to return the 
next one given, and so on. So in this example, port 80 would be returned.  If 
-p443,80 were specified, then port 443 would be used.

You can specify as many ports as you like in a --ports specification, just 
separate them with a comma and do not add spaces.

In this next example, we customize the proxy command based on the port chosen::

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
traffic on port 22, and Apache is configured to act as a proxy for ssh on ports 
80 and 443 (see `SSH via HTTP 
<http://www.nurdletech.com/linux-notes/ssh/via-http.html>`.

If you prefer, you can use proxytunnel rather than socat in the proxy command::

   proxyCommand = 'proxytunnel -q -p %h:%p -d 127.0.0.1:22'


Attribute Descriptions
''''''''''''''''''''''

Most attributes can be given as a two element tuple. The first value in the pair 
is used as the value of the attribute, and the second should be a string that is 
added as a comment to describe the attribute. For example::

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
example::

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

Location
''''''''

It is also possible to choose the hostname based on location. The user specifies 
location using::

   gensshconfig --location=washington

or::

   gensshconfig -lwashington

You can get a list of the known locations using::

   gensshconfig --available

To configure support for locations, you first specify your list of known 
locations in LOCATIONS::

   LOCATIONS = ['home', 'washington', 'toulouse']

Then you must configure your hosts to use the location. To do so, you use the 
choose() method to set the location. The choose() method requires three things:

1. A dictionary that gives hostnames or IP addresses and perhaps descriptive 
   comment as a function of the location. These locations are generally specific 
   to the host.
2. Another dictionary that maps the user's locations into the host's locations.
3. A default location.

For example::

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
list given in LOCATIONS. As such, every maps argument should support each of 
those locations.  However, a user may given any location they wish. If the 
location given is not found in maps, then it will be looked for in locations, 
and if it is not in locations, the default location is used.


Forwards
''''''''

When forwards are specified, two ssh host entries are created. The first does 
not include forwarding. The second has the same name with '-tun' appended, and 
includes the forwarding. The reason this is done is that once one connection is 
setup with forwarding, a second connection that also attempts to performing 
forwarding will produce a series of error messages indicating that the ports are 
in use and so cannot be forwarded. Instead, you should only use the tunneling 
version once when you want to set up the port forwards, and you the base entry 
at all other times. Often forwarding connections are setup to run in the 
background as follows::

   ssh -f -N home-tun

If you have set up connection sharing using ControlMaster and then run::

   ssh home

SSH will automatically share the existing connection rather than starting a new 
one.

Both local and remote forwards should be specified as lists. The lists can 
either be simple strings, or can be tuple pairs if you would like to give 
a description for the forward. The string that describes the forward has the 
syntax: 'lclHost:lclPort rmtHost:rmtPort' where lclHost and rmtHost can be 
either a host name or an IP address and lclPort and rmtPort are port numbers.
For example::

   '11025 localhost:25'

The local host is used to specify what machines can connect to the port locally.
If the GatewayPorts setting is set to *yes* on the SSH server, then forwarded 
ports are accessible to any machine on the network. If the GatewayPorts setting 
is *no*, then the forwarded ports are only available from the local host.  
However, if GatewayPorts is set to *clientspecified*, then the accessibility of 
the forward address is set by the local host specified.  For example:

=============================== ==============================
5280 localhost:5280             accessible only from localhost
localhost:5280 localhost:5280   accessible only from localhost
\*:5280 localhost:5280          accessible from anywhere
0.0.0.0:5280 localhost:5280     accessible from anywhere
lucifer:5280 localhost:5280     accessible from lucifer
192.168.0.1:5280 localhost:5280 accessible from 192.168.0.1
=============================== ==============================

The VNC function is provided for converting VNC host and display number 
information into a setting suitable for a forward. You can give the local 
display number, the remote display number, and the remote host name (from the 
perspective of the remote ssh server) and the local host name.  For example::

   VNC(lclDispNum=1, rmtHost='localhost', rmtDispNum=12)

This allows a local VNC client viewing display 1 to show the VNC server running 
on display 12 of the SSH server host.

If you give a single number, it will use it for both display numbers.  If you 
don't give a name, it will use *localhost* as the remote host (in this case 
*localhost* represents the remote ssh server).  So the above VNC section to the 
local forwards could be shortened to::

   VNC(12)

if you configured the local VNC client to connect to display 12.

An example of many of these features::

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
           ('34190 localhost:4190', "Mail - Seive"),
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
       identitiesOnly yes
       forwardAgent yes

   # Lucifer Home Server (with forwards)
   host home-tun lucifer-tun
       user herbie
       hostname 74.125.232.64
       port = 22
       identityFile /home/herbie/.ssh/teneya
       identitiesOnly yes
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

For example::

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
       identitiesOnly yes
       forwardAgent yes

   # Entry Host to Machine Farm (with forwards)
   host farm-tun earth-tun
       user herbie
       hostname 231.91.164.92
       identityFile /home/herbie/.ssh/my2014key
       identitiesOnly yes
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
       identitiesOnly yes
       forwardAgent yes

   # 96GB Compute Server
   host farm-saturn
       hostname saturn
       proxyCommand ssh host -W %h:%p
       user herbie
       identityFile /home/herbie/.ssh/my2014key
       identitiesOnly yes
       forwardAgent yes

   # 64GB Compute Server
   host farm-netpune
       hostname neptune
       proxyCommand ssh host -W %h:%p
       user herbie
       identityFile /home/herbie/.ssh/my2014key
       identitiesOnly yes
       forwardAgent yes


Subclassing
'''''''''''

Subclassing is an alternative to guests that gives more control over how the 
attributes are set. When you create a host that is a subclass of another host 
(the parent), the parent is configured to be the proxy and only the 'user' and 
'identityFile' attributes are copied over from the parent, but these can be 
overridden locally.

For example::

   class Jupiter(Farm):
       description = "128GB Compute Server"
       hostname = 'jupiter'
       tun_trusted = True
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
       identitiesOnly yes
       forwardAgent no
       proxyCommand ssh farm -W %h:%p

   # 128GB Compute Server (with forwards)
   host jupiter-tun
       user herbie
       hostname jupiter
       identityFile /home/herbie/.ssh/my2014key
       identitiesOnly yes
       forwardAgent no
       proxyCommand ssh farm -W %h:%p
       remoteForward 14443 localhost:22

If you contrast this with farm-jupiter above, you will see that the name is 
different, as is the trusted status (farm-jupiter inherits 'trusted' from Host, 
whereas jupiter does not). Also, there are two versions, one with port 
forwarding and one without.


Proxies
-------

Some networks block connections to port 22. If your desired host accepts 
connections on other ports, you can use the --ports feature described above to 
work around these blocks. However, some networks block all ports and force you 
to use a proxy.  Or, if you do have open ports but your host does not accept ssh 
traffic on those ports, you can sometimes use a proxy to access your host.

Available proxies are specified by adding PROXIES to the hosts.py file. Then, if 
you would like to use a proxy, you use the --proxy (or -P) command line argument 
to specify the proxy by name. For example::

   PROXIES = {
       'work_proxy':   'proxytunnel -q -p webproxy.ext.workinghard.com:80 -d %h:%p',
       'school_proxy': 'proxytunnel -q -p sproxy.fna.learning.edu:1080 -d %h:%p',
   }

Two HTTP proxies are described, the first capable of bypassing the corporate 
firewall and the second does the same for the school's firewall. If preferred, 
you can use socat rather than proxytunnel to accomplish the same thing::

   PROXIES = {
       'work_proxy':   'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80',
       'school_proxy': 'socat - PROXY:sproxy.fna.learning.edu:%h:%p,proxyport=1080',
   }

When at work, you should generate your ssh config file using::

   gensshconfig --proxy=work_proxy

or::

   gensshconfig --Pwork_proxy

You can get a list of the pre-configured proxies using::

   gensshconfig --available

It is also possible to use ssh hosts as proxies. For example, when at an 
internet cafe that blocks port 22, you can work around the blockage 
even if your host only supports 22 using::

   gensshconfig --ports=80 --proxy=tunnelr

or::

   gensshconfig -p80 --Ptunnelr

Using the --proxy command line argument adds a proxyCommand entry to every host 
that does not already have one (except the host being used as the proxy). In 
that way, proxies are automatically chained. For example, in the example given 
above Jupiter subclasses Farm, and so it naturally gets a proxyCommand that 
causes it to be proxied through Farm, but Farm does not have a proxyCommand. By 
running gensshconfig with --proxy=tunnelr, Farm will get the proxyCommand 
indicating it should proxy through tunnelr, but Jupiter retains its original 
proxyCommand.  So when connecting to jupiter a two link proxy chain is used: 
packets are first sent to tunnelr, which then forwards them to farm, which 
forwards them to jupiter.

You can specify a proxy on the NetworkEntry for you network. If you do, that 
proxy will be used by default when on that network for all hosts that not on 
that network. A host is said to be on the network if the hostname is 
specifically given for that network. For example, assume you have a network 
configured for work::

   class Work(NetworkEntry):
       # Work network
       routers = ['78:92:4d:2b:30:c6']
       proxy = 'work_proxy'

Then assume you have a host that is not configured for that network (Home) and 
one that is (Farm)::

   class Home(HostEntry):
       description = "Home Server"
       aliases = ['lucifer']
       user = 'herbie'
       hostname = {
           'home': '192.168.0.1',
           'default': '74.125.232.64'
       }
       proxyCommand = 'socat - PROXY:webproxy.ext.workinghard.com:%h:%p,proxyport=80'

   class Farm(HostEntry):
       description = "Entry Host to Machine farm"
       aliases = ['mercury']
       user = 'herbie'
       hostname = {
           'work': '192.168.1.16',
           'default': '231.91.164.92'
       }

When on the work network, when you connect to Home you will use the proxy and 
when you connect to farm, you will not.
