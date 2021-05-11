import os
import configparser
from lib.Utils import Logger as Logger


class Client:
    def __init__(self, client_path, client, endpoint, dns, server_pubkey, access, client_vpn_ip):
        self.client_path = client_path
        self.client_name = client
        self.client_pubkey = "none"
        self.client_privkey = "none"
        self.client_psk = "none"
        self.endpoint = endpoint
        self.client_dns = dns
        self.server_pubkey = server_pubkey
        self.access = access
        self.client_vpn_ip = client_vpn_ip
        self.state = True
        self.generate_keys()

    def generate_keys(self):
        if os.path.isdir(self.client_path):
            if not (os.path.isfile(f"{self.client_path}/privatekey") and
                    os.path.isfile(f"{self.client_path}/publickey") and
                    os.path.isfile(f"{self.client_path}/presharedkey")):

                # public/privatekey
                command = f"umask 077; wg genkey | tee {self.client_path}/privatekey | wg pubkey > {self.client_path}/publickey"
                os.system(command)

                # presharedkey
                command = f"umask 077; wg genpsk > {self.client_path}/presharedkey"
                os.system(command)

            # read keys in any case
            with open(f"{self.client_path}/privatekey", 'r') as f:
                self.client_privkey = f.read()
            with open(f"{self.client_path}/publickey", 'r') as f:
                self.client_pubkey = f.read()
            with open(f"{self.client_path}/presharedkey", 'r') as f:
                self.client_psk = f.read()
        else:
            # something went horribly wrong when the clients got built. Or someone is messing with the client dir
            Logger.fatal("Client directory has not been created or was deleted intermittently")

    def write_client_config(self):
        path = f"{self.client_path}/wg0-{self.client_name}.conf"

        if not os.path.isfile(path):
            base_client_config = f"""[Interface]
PrivateKey = {str(self.client_privkey).strip()}
Address = {str(self.client_vpn_ip).strip()}/16
DNS = {str(self.client_dns).strip()}
    
[Peer] # wireguard server
PublicKey = {str(self.server_pubkey).strip()}
PresharedKey = {str(self.client_psk).strip()}
AllowedIPs = {str(self.access).strip()}
Endpoint = {str(self.endpoint).strip()}
PersistentKeepalive = 20"""

            with open(path, 'w') as f:
                f.write(base_client_config + "\n")
        # client config already exists, read the value of its IP-Address
        else:
            config = configparser.ConfigParser()
            config.read(f"{self.client_path}/wg0-{self.client_name}.conf")
            self.client_vpn_ip = config['Interface']['Address']
            self.client_vpn_ip = self.client_vpn_ip.split('/')[0]

        # create QR-Code
        command = f"qrencode -t PNG -o {self.client_path}/wg0-{self.client_name}.png <" + \
                  f" {self.client_path}/wg0-{self.client_name}.conf "
        os.system(command)
