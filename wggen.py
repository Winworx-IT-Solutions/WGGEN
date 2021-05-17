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
    if n_clients > 65531:  # we cannot manage more than this amount of clients, don't even try
        Logger.fatal("You are trying to create more than 65531 peers. This exceeds the /16 VPN-Subnet and is "
                     "not supported by WGGEN.")
    Logger.info(f"Will be creating {n_clients} peers")
    actual_clients = []
    for i, client in enumerate(clients):
        # determine client path
        client_path = f"{WG_CLIENT_BASE_PATH}/{client}"
        try:
            os.makedirs(client_path)
        except OSError:
            pass

        # determine client vpn ip
        ip += 1
        if ip > 254:
            base += 1
            if base > 255:
                Logger.fatal(f"Ran out of VPN-Subnet Addresses at client {i} of {n_clients}")
            ip = 1
        client_vpn_ip = f"{vpn_subnet}.{base}.{ip}"

        # generate client
        generated_client = Client(client_path, client, args.endpoint, args.dns, server_pubkey,
                                  args.access, client_vpn_ip)
        actual_clients.append(generated_client)
        if not generated_client.state:
            Logger.warn(f"Failed to create client: {client}")

        print(f"Creating clients: {int((i/(n_clients-1))*100)}%", end="\r")

    # save last ip on last client
    with open(lastip_file, 'w') as f:
        f.write(f"{base}.{ip}")
    print(f"\nCreated {n_clients} clients")

    # write client config files and server config file
    ClientTools.write_config_files(actual_clients)
    ServerTools.write_server_config(actual_clients, args, vpn_subnet, WG_BASE_PATH)


if __name__ == "__main__":
    main()
