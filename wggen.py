#!/usr/bin/python3.7
"""
Creates and manages WireGuard Peers coming from an LDAP-Search query.

Author: Florian Fink @ 03.05.2021
"""
import os
import argparse
from lib.Utils import Logger as Logger
from lib.Client import Client as Client
from ldap3 import Server, Connection, ALL

WG_CLIENT_BASE_PATH = "/etc/wireguard/clients"
WG_BASE_PATH = "/etc/wireguard"


def main():
    """
    Main entrypoint of the program
    """
    # init argparse
    parser = argparse.ArgumentParser(description="Manage Wireguard peer and server configurations")

    # add args
    parser.add_argument('-d', '--dns', type=str,
                        help='DNS Server to be used by the clients', required=True)
    parser.add_argument('-c', '--count', type=int,
                        help='Number of peer\'s created for each name', required=True)
    parser.add_argument('-e', '--endpoint', type=str,
                        help='Endpoint for the wireguard peers to connect to', required=True)
    parser.add_argument('-s', '--vpn_subnet', type=str,
                        help='Net-Part of a /24 subnet used for vpn connections i.e.: 192.168.254 or 10.11.12',
                        required=True)
    parser.add_argument('-i', '--interface', type=str,
                        help='Interface, to which the VPN-Traffic gets routed', required=True)
    parser.add_argument('-a', '--access', type=str,
                        help='Subnet/Hosts to which all clients should have access to', required=True)
    parser.add_argument('-n', '--base-dn', type=str,
                        help='Base DN for ldap search', required=True)
    parser.add_argument('-f', '--filter', type=str,
                        help='Filter for ldap search', required=True)
    parser.add_argument('-l', '--ldap-server', type=str,
                        help='Address of ldap server', required=True)
    parser.add_argument('-b', '--bind-dn', type=str,
                        help='bind user for ldap server', required=True)
    parser.add_argument('-w', '--bind-pw', type=str,
                        help='bind password for ldap server', required=True)

    args = parser.parse_args()

    # check for required binaries and root privileges
    if not os.path.isfile("/usr/bin/wg"):
        Logger.fatal("wg command not found. Have you installed WireGuard?")
    if not os.path.isfile("/usr/bin/qrencode"):
        Logger.fatal("qrencode command not found. Have you installed qrencode?")
    if not os.getuid() == 0:
        Logger.fatal("This script needs to be run with Root-Privileges")

    # setup functions
    if not initialize_directory_structure():
        Logger.fatal("Failed to generate base directory structure")
    if not generate_server_keypair():
        Logger.fatal("Failed to generate server keypair")

    # get client list from ldap
    server = Server(args.ldap_server, get_info=ALL)
    conn = Connection(server, args.bind_dn, args.bind_pw, auto_bind=True)
    potential_clients = get_ldap_user_list(conn, args.base_dn, args.filter)

    clients = []
    actual_clients = []

    # create counter for clients
    for client in potential_clients:
        if client == "SERVER":
            Logger.error("Cannot create client {}: Invalid Name".format(client))
        else:
            for i in range(0, args.count):
                clients.append("{}-{}".format(client, i))

    # get server publickey
    server_pubkey, server_privkey = read_server_keys()

    # build clients
    for i, client in enumerate(clients):
        client_path = "{}/{}".format(WG_CLIENT_BASE_PATH, client)
        try:
            os.makedirs(client_path)
        except OSError:
            pass
        generated_client = Client(client_path, client, args.endpoint, args.dns, server_pubkey, args.vpn_subnet,
                                  args.access, i)
        actual_clients.append(generated_client)
        if not generated_client.state:
            Logger.warn("Failed to create client: {}".format(client))

    # generate clients
    for client in actual_clients:
        client.write_client_config()

    # write the server config
    write_server_config(actual_clients, args)


def get_ldap_user_list(c, base_dn, ldap_filter):
    c.search(base_dn, ldap_filter, attributes=['*'])
    name_list = []
    for entry in c.entries:
        name_list.append(entry.uid)

    return name_list


def write_server_config(actual_clients, args):
    """
    build and write the server config
    """
    Logger.info("generating server config")
    path = "{}/wg0.conf".format(WG_BASE_PATH)
    server_pubkey, server_privkey = read_server_keys()

    base_server_config = """[Interface] # wireguard-server
Address = {}.1/24
ListenPort = 51820
PrivateKey = {}
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o {} -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -D FORWARD -o wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o {} -j MASQUERADE
    """.format(
        str(args.vpn_subnet).strip(),
        str(server_privkey).strip(),
        str(args.interface).strip(),
        str(args.interface).strip()
    )

    for client in actual_clients:
        client_base_config = """
[Peer] # {}
PublicKey = {}
PresharedKey = {}
AllowedIPs = {}/32
        """.format(
            str(client.client_name).strip(),
            str(server_pubkey).strip(),
            str(client.client_psk).strip(),
            str(client.client_vpn_ip).strip()
        )
        base_server_config = base_server_config + client_base_config

    with open(path, 'w') as f:
        f.write(base_server_config + "\n")


def read_server_keys():
    """
    read server keypair

    :return: Public and Privatekey of the wireguard server
    """
    # read keys
    with open("{}/privatekey".format(WG_BASE_PATH), 'r') as f:
        privkey = f.read()
    with open("{}/publickey".format(WG_BASE_PATH), 'r') as f:
        pubkey = f.read()

    return pubkey, privkey


def generate_server_keypair():
    """
    Generates server keypair

    :return: True or False depending on if the generation of the server keypair was successful
    """
    if os.path.isfile('{}/privatekey'.format(WG_BASE_PATH)) and os.path.isfile('{}/publickey'.format(WG_BASE_PATH)):
        return True

    Logger.info("Creating Server keypair")
    command = "umask 077; wg genkey | tee {}/privatekey | wg pubkey > {}/publickey".format(WG_BASE_PATH, WG_BASE_PATH)
    os.system(command)

    if os.path.isfile('{}/privatekey'.format(WG_BASE_PATH)) and os.path.isfile('{}/publickey'.format(WG_BASE_PATH)):
        Logger.info("Server keypair already exists. Skipping generation")
        return True

    return False


def initialize_directory_structure():
    """
    Checks for required directories and attempts to create them if they are missing

    :return: True or False depending on if the creation of the directories was successful
    """
    # check and create base config dir
    if not os.path.isdir(WG_BASE_PATH):
        print("WGGEN: WireGuard config directory is missing, creating: {}".format(WG_BASE_PATH))
        try:
            os.makedirs(WG_BASE_PATH, exist_ok=True)
        except OSError:
            print("Failed to create WireGuard config directory: {}".format(WG_BASE_PATH))

    # check and create client config dir
    if not os.path.isdir(WG_CLIENT_BASE_PATH):
        print("WGGEN: WireGuard config client directory is missing, creating: {}".format(
            WG_CLIENT_BASE_PATH))
        try:
            os.makedirs(WG_CLIENT_BASE_PATH, exist_ok=True)
        except OSError:
            print("Failed to create WireGuard client config directory: {}".format(
                WG_CLIENT_BASE_PATH))

    # check if we were able to create the config directories
    if os.path.isdir(WG_BASE_PATH) and os.path.isdir(WG_CLIENT_BASE_PATH):
        return True

    return False


if __name__ == "__main__":
    main()
