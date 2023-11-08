Releases
========

Latest development release
--------------------------

    | Version: 2.2
    | Released: 2022-11-19

- Added *nmcli_connection* attribute to the *NetworkEntry* class.
- Added *NMCLI_CONNS* setting.

Both these changes support the use of secondary networks, meaning that if your 
machine is connected to multiple networks, you can configure a host so that ssh 
connects to it directly through a secondary network rather than using the 
primary gateway.


2.2 (2022-11-19)
----------------
- Make path to arp command user settable.


2.1 (2021-01-18)
----------------
- Make path to arp command user settable.


2.1 (2021-01-18)
----------------
- Improved the documentation.


2.0 (2020-04-16)
----------------
- Improve documentation.


1.3 (2020-03-11)
----------------
- Add available SSH algorithms filtering.
- Make SSH settings case insensitive.
- Added shared config files examples.
- Refine *identityfile* behavior.
- Eliminate *tun_trusted*.


1.2 (2020-01-07)
----------------
- Configuration is now external to the program source code
  (it is now in ``~/.config/sshconfig``).
