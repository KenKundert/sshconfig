#
# SSH Hosts
#

from sshconfig import HostEntry, VNC, ports, locations
from socket import gethostname

# Lucifer {{{1
class Home(HostEntry):
    description = "Home Server"
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
    identityFile = 'my2014key'
    localForward = [
        ('1025 localhost:25',  "Mail - SMTP"),
        ('1143 localhost:143', "Mail - IMAP"),
        (VNC(12), "VNC"),
    ]
    dynamicForward = 9999

# Work {{{1
class Work(HostEntry):
    description = "Work Gateway Server"
    aliases = ['earth']
    user = 'herbie'
    hostname = {
        'work': '192.168.1.168',
        'default': '150.485.10.87'
    }
    trusted = True
    identityFile = 'my2014key'
    localForward = [
        (VNC(16), "VNC on earth"),
        ('9100 192.168.1.51:9100', "Printer"),
        ('1025 venus:25',  "Mail - SMTP"),
        ('1143 venus:143', "Mail - IMAP"),
        ('4190 venus:4190', "Mail - Sieve"),
    ]

class Mail(Work):
    aliases = ['venus']
    description = "Designer's Guide mail server"

# Farm {{{1
class Farm(HostEntry):
    description = "Entry Host to Machine farm"
    aliases = ['mercury']
    user = 'herbie'
    hostname = {
        'work': '192.168.1.16',
        'default': '173.11.122.58'
    }
    trusted = True
    identityFile = 'my2014key'
    guests = [
        ('jupiter', "128GB Compute server"),
        ('saturn',  "96GB Compute server"),
        ('neptune', "64GB Compute server"),
    ]
    localForward = [
        (VNC(16), "VNC on mercury"),
    ]


# DigitalOcean {{{1
class DigitalOcean(HostEntry):
    description = "Web server"
    aliases = ['do', 'web']
    user = 'herbie'
    port = ports.choose([22, 80, 443])
    hostname = '107.170.65.89'
    identityFile = 'digitalocean'

# Tunnelr {{{1
class Tunnelr(HostEntry):
    description = "Commercial proxy server"
    user = 'herbie'
    hostname = locations.choose(
        locations = {
            'sf': ("65.19.130.60", "Fremont, CA, US (fremont.tunnelr.com)"),
            'la': ("173.234.163.226", "Los Angeles, CA, US (la.tunnelr.com)"),
            'wa': ("209.160.33.99", "Seattle, WA, US (seattle.tunnelr.com)"),
            'tx': ("64.120.56.66", "Dallas, TX, US (dallas.tunnelr.com)"),
            'va': ("209.160.73.168", "McLean, VA, US (mclean.tunnelr.com)"),
            'nj': ("66.228.47.107", "Newark, NJ, US (newark.tunnelr.com)"),
            'ny': ("174.34.169.98", "New York City, NY, US (nyc.tunnelr.com)"),
            'london': ("109.74.200.165", "London, UK (london.tunnelr.com)"),
            'uk': ("31.193.133.168", "Maidenhead, UK (maidenhead.tunnelr.com)"),
            'switzerland': ("178.209.52.219", "Zurich, Switzerland (zurich.tunnelr.com)"),
            'sweden': ("46.246.93.78", "Stockholm, Sweden (stockholm.tunnelr.com)"),
            'spain': ("37.235.53.245", "Madrid, Spain (madrid.tunnelr.com)"),
            'netherlands': ("89.188.9.54", "Groningen, Netherlands (groningen.tunnelr.com)"),
            'germany': ("176.9.242.124", "Falkenstein, Germany (falkenstein.tunnelr.com)"),
            'france': ("158.255.215.77", "Paris, France (paris.tunnelr.com)"),
        },
        maps={
            'bayarea': 'sf',
            'dallas': 'tx',
            'ann-arbor': 'nj',
            'shanghai': 'sweden',
            'bangalore': 'germany'
        },
        default='sf'
    )
    port = ports.choose([
        22, 21, 23, 25, 53, 80, 443, 524, 5555, 8888
    ])
    identityFile = 'tunnelr'
    dynamicForward = 9998

# Github {{{1
class Github(HostEntry):
    description = "Github.com"
    aliases = ['*.github.com']
    hostKeyAlias = 'github-server-pool.github.com'
    user = 'herbie'
    identityFile = 'github'
