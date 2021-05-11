import os
from lib.Utils import Logger as Logger


class ServerTools:
    @staticmethod
    def read_server_keys(wg_base_path):
        """
        read server keypair

        :return: Public and Privatekey of the wireguard server
        """
        # read keys
        with open(f"{wg_base_path}/privatekey", 'r') as f:
            privkey = f.read()
        with open(f"{wg_base_path}/publickey", 'r') as f:
            pubkey = f.read()

        return pubkey, privkey

    @staticmethod
    def generate_server_keypair(wg_base_path):
        """
        Generates server keypair

        :return: True or False depending on if the generation of the server keypair was successful
        """
        if os.path.isfile(f'{wg_base_path}/privatekey') and os.path.isfile(f'{wg_base_path}/publickey'):
            Logger.info("Server keypair already exists. Skipping generation")
            return True

        Logger.info("Creating Server keypair")
        command = f"umask 077; wg genkey | tee {wg_base_path}/privatekey | wg pubkey > {wg_base_path}/publickey"
        os.system(command)

        if os.path.isfile(f'{wg_base_path}/privatekey') and os.path.isfile(f'{wg_base_path}/publickey'):
            return True

        return False

    @staticmethod
    def write_server_config(actual_clients, args, vpn_subnet, wg_base_path):
        """
        build and write the server config
        """
        Logger.info("generating server config")
        path = f"{wg_base_path}/wg0.conf"
        server_pubkey, server_privkey = ServerTools.read_server_keys(wg_base_path)

        base_server_config = f"""[Interface] # wireguard-server
Address = {str(vpn_subnet).strip()}.0.1/24
ListenPort = 51820
PrivateKey = {str(server_privkey).strip()}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {str(args.interface).strip()} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {str(args.interface).strip()} -j MASQUERADE
"""

        for client in actual_clients:
            client_base_config = f"""
[Peer] # {str(client.client_name).strip()}
PublicKey = {str(client.client_pubkey).strip()}
PresharedKey = {str(client.client_psk).strip()}
AllowedIPs = {str(client.client_vpn_ip).strip()}/32
"""
            base_server_config = base_server_config + client_base_config

        with open(path, 'w') as f:
            f.write(base_server_config + "\n")
