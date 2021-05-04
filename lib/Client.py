import os
from lib.Utils import Logger as Logger


class Client:
    def __init__(self, client_path, client, endpoint, dns, server_pubkey, vpn_subnet, access, client_id):
        self.client_path = client_path
        self.client_name = client
        self.client_pubkey = "none"
        self.client_privkey = "none"
        self.client_psk = "none"
        self.endpoint = endpoint
        self.client_dns = dns
        self.server_pubkey = server_pubkey
        self.access = access
        self.client_vpn_ip = "{}.{}".format(vpn_subnet, client_id + 10)
        self.state = True

        if client_id + 10 > 255:
            self.state = False

        self.generate_keys()

    def generate_keys(self):
        if os.path.isdir(self.client_path):
            if not (os.path.isfile("{}/privatekey".format(self.client_path)) and
                    os.path.isfile("{}/publickey".format(self.client_path)) and
                    os.path.isfile("{}/presharedkey".format(self.client_path))):

                Logger.info("Creating keys for client: {}".format(self.client_name))

                # public/privatekey
                command = "umask 077; wg genkey | tee {}/privatekey | wg pubkey > {}/publickey".format(self.client_path,
                                                                                                       self.client_path)
                os.system(command)

                # presharedkey
                command = "umask 077; wg genpsk > {}/presharedkey".format(self.client_path)
                os.system(command)

            # read keys in any case
            with open("{}/privatekey".format(self.client_path), 'r') as f:
                self.client_privkey = f.read()
            with open("{}/publickey".format(self.client_path), 'r') as f:
                self.client_pubkey = f.read()
            with open("{}/presharedkey".format(self.client_path), 'r') as f:
                self.client_psk = f.read()
        else:
            # something went horribly wrong when the clients got built. Or someone is messing with the client dir
            Logger.fatal("Client directory has not been created or was deleted intermittently")

    def write_client_config(self):
        path = "{}/wg0-{}.conf".format(self.client_path, self.client_name)

        if not os.path.isfile(path):
            Logger.info("generating config for client: {}".format(self.client_name))
            base_client_config = """[Interface]
PrivateKey = {}
Address = {}/24
DNS = {}
    
[Peer] # wireguard server
PublicKey = {}
PresharedKey = {}
AllowedIPs = {}
Endpoint = {}
PersistentKeepalive = 20
                """.format(
                str(self.client_privkey).strip(),
                str(self.client_vpn_ip).strip(),
                str(self.client_dns).strip(),
                str(self.server_pubkey).strip(),
                str(self.client_psk).strip(),
                str(self.access).strip(),
                str(self.endpoint).strip()
            )

            with open(path, 'w') as f:
                f.write(base_client_config + "\n")

            Logger.info("config for {} generated".format(self.client_name))
            # end else

        # create QR-Code
        Logger.info("creating QR-Code for {}".format(self.client_name))
        command = "qrencode -t PNG -o {}/wg0-{}.png < {}/wg0-{}.conf".format(self.client_path, self.client_name,
                                                                             self.client_path, self.client_name)
        os.system(command)
