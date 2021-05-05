#!/usr/bin/python3.7
"""
Creates and manages WireGuard Peers coming from an LDAP-Search query.

Author: Florian Fink @ 03.05.2021
"""
import os
from lib.ServerTools import ServerTools
from lib.ClientTools import ClientTools
from lib.Client import Client

from lib.Utils import Tools, Logger
from lib.Setup import Setup

WG_CLIENT_BASE_PATH = "/etc/wireguard/clients"
WG_BASE_PATH = "/etc/wireguard"
subnet_file = "/etc/wireguard/subnet"
lastip_file = "/etc/wireguard/last_ip"


def main():
    """
    Main entrypoint of the program
    """
    # get args passed by the command line
    args = Tools.init_args()

    # check for required binaries and root privileges and run server keypair generation and dir structure check
    Setup.check_prerequisits()
    Setup.start(WG_BASE_PATH, WG_CLIENT_BASE_PATH)

    # get final list of clients (ldap and local), server keypair and base vpn, and negotiate a vpn_subnet
    clients = ClientTools.get_client_list(args)
    server_pubkey, server_privkey = ServerTools.read_server_keys(WG_BASE_PATH)
    base, ip = Tools.get_base_ip(lastip_file)
    vpn_subnet = Tools.get_vpn_subnet(subnet_file)

    # build clients
    n_clients = len(clients)
    actual_clients = []
    for i, client in enumerate(clients):
        # determine client path
        client_path = "{}/{}".format(WG_CLIENT_BASE_PATH, client)
        try:
            os.makedirs(client_path)
        except OSError:
            pass

        # determine client vpn ip
        ip += 1
        if ip > 254:
            base += 1
            ip = 1
        client_vpn_ip = "{}.{}.{}".format(vpn_subnet, base, ip)

        # generate client
        generated_client = Client(client_path, client, args.endpoint, args.dns, server_pubkey,
                                  args.access, client_vpn_ip)
        actual_clients.append(generated_client)
        if not generated_client.state:
            Logger.warn("Failed to create client: {}".format(client))

        # save last ip on last client
        if i == n_clients:
            with open(lastip_file, 'w') as f:
                f.write("{}.{}".format(base, ip))

        print("Creating clients: {}%".format(int((i/(n_clients-1))*100)), end="\r")
    print("\nCreated {} clients".format(n_clients))

    # write client config files and server config file
    ClientTools.write_config_files(actual_clients)
    ServerTools.write_server_config(actual_clients, args, vpn_subnet, WG_BASE_PATH)


if __name__ == "__main__":
    main()
