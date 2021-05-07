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
        with open("{}/privatekey".format(wg_base_path), 'r') as f:
            privkey = f.read()
        with open("{}/publickey".format(wg_base_path), 'r') as f:
            pubkey = f.read()

        return pubkey, privkey

    @staticmethod
    def generate_server_keypair(wg_base_path):
        """
        Generates server keypair

        :return: True or False depending on if the generation of the server keypair was successful
        """
        if os.path.isfile('{}/privatekey'.format(wg_base_path)) and os.path.isfile('{}/publickey'.format(wg_base_path)):
            Logger.info("Server keypair already exists. Skipping generation")
            return True

        Logger.info("Creating Server keypair")
        command = "umask 077; wg genkey | tee {}/privatekey | wg pubkey > {}/publickey".format(wg_base_path,
                                                                                               wg_base_path)
        os.system(command)

        if os.path.isfile('{}/privatekey'.format(wg_base_path)) and os.path.isfile('{}/publickey'.format(wg_base_path)):
            return True

        return False

    @staticmethod
    def write_server_config(actual_clients, args, vpn_subnet, wg_base_path):
        """
        build and write the server config
        """
        Logger.info("generating server config")
        path = "{}/wg0.conf".format(wg_base_path)
        server_pubkey, server_privkey = ServerTools.read_server_keys(wg_base_path)

        base_server_config = """[Interface] # wireguard-server
Address = {}.0.1/24
ListenPort = 51820
PrivateKey = {}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT; iptables -t nat -A POSTROUTING -o {} -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT; iptables -t nat -D POSTROUTING -o {} -j MASQUERADE
        """.format(
            str(vpn_subnet).strip(),
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
                str(client.client_pubkey).strip(),
                str(client.client_psk).strip(),
                str(client.client_vpn_ip).strip()
            )
            base_server_config = base_server_config + client_base_config

        with open(path, 'w') as f:
            f.write(base_server_config + "\n")
