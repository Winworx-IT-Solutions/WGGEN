import sys
import os
import argparse
from random import randrange


class Logger:
    @staticmethod
    def fatal(error):
        print("FATAL: {}".format(error))
        sys.exit()

    @staticmethod
    def error(error):
        print("ERROR: {}".format(error))

    @staticmethod
    def warn(error):
        print("WARN: {}".format(error))

    @staticmethod
    def info(error):
        print("INFO: {}".format(error))


class Tools:
    @staticmethod
    def init_args():
        parser = argparse.ArgumentParser(description="Manage Wireguard peer and server configurations")
        parser.add_argument('-p', '--list', type=str, nargs='+',
                            help='List of peer names that will be created', required=False)
        parser.add_argument('-d', '--dns', type=str,
                            help='DNS Server to be used by the clients', required=True)
        parser.add_argument('-c', '--count', type=int,
                            help='Number of peer\'s created for each name', required=True)
        parser.add_argument('-e', '--endpoint', type=str,
                            help='Endpoint for the wireguard peers to connect to', required=True)
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
        parser.add_argument('-u', '--user-attr', type=str,
                            help='ldap attribute to use as username', required=True)

        return parser.parse_args()

    @staticmethod
    def get_base_ip(lastip_path):
        base = 0
        ip = 0
        if os.path.isfile(lastip_path):
            Logger.info("last_ip file found, reading last ip information from disk")
            with open(lastip_path) as f:
                content = f.read()
            base, ip = content.split(".")

        return int(base), int(ip)

    @staticmethod
    def get_vpn_subnet(subnet_file):
        if os.path.isfile(subnet_file):
            Logger.info("subnet file found, reading vpn-subnet information from disk")
            with open(subnet_file, 'r') as f:
                vpn_subnet = f.read()
        else:
            vpn_subnet = "10.{}".format(int(randrange(0, 254)))
            Logger.info("Creating new VPN-Subnet: {}".format(vpn_subnet))
            with open(subnet_file, 'w') as f:
                f.write(vpn_subnet)

        return vpn_subnet
