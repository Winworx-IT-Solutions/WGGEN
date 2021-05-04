# Manage Wireguard peer and server configurations


usage: `wggen.py [-h] -p LIST [LIST ...] -d DNS -c COUNT -e ENDPOINT -s
                VPN_SUBNET -i INTERFACE -a ACCESS -n BASE_DN -f FILTER -l
                LDAP_SERVER -b BIND_DN -w BIND_PW`

| Opt | long Opt     | Argument  | Description                                                                             |
|:---:|:------------:|:---------:|:---------------------------------------------------------------------------------------:|
|-h   | --help       |           |show a help message and exit                                                             |
|-p   |--list        |[PEERs ...]|List of peer names that will be created (they are added to the peers that come from ldap)|                         |
|-d   | --dns        |DNS        |DNS Server to be used by the clients                                                     |
|-c   | --count      |COUNT      |Number of peer's created for each name                                                   |
|-e   | --endpoint   |ENDPOINT   |Endpoint for the wireguard peers to connect to                                           |
|-s   | --vpn_subnet |VPN_SUBNET |Net-Part of a /24 subnet used for vpn connections i.e.: 192.168.254                      |
|-i   | -interface   |INTERFACE  |Interface, to which the VPN-Traffic gets routed                                          |
|-a   | --access     |ACCESS     |Subnet/Hosts to which all clients should have access to                                  |
|-n   | --base-dn    |BASE_DN    |Base DN for ldap search                                                                  |
|-f   | --filter     |FILTER     |Filter for ldap search                                                                   |
|-l   | --ldap-server|LDAP_SERVER|Address of ldap server                                                                   |
|-b   | --bind-dn    |BIND_DN    |bind user for ldap server                                                                |
|-w   | --bind-pw    |BIND_PW    |bind password for ldap server                                                            |
|-u   | --user-attr  |USER_ATTR  |ldap attribute to use as username                                                           |

