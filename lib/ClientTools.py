from lib.Utils import Logger as Logger
from lib.LDAPTools import LDAPTools


class ClientTools:
    @staticmethod
    def get_client_list(args):

        target_clients = []
        clients = []
        ldap_clients = []

        # get ldap clients
        if args.enable_ldap:
            ldap = LDAPTools(args)
            ldap_clients = ldap.get_ldap_clients()

        if not args.list and not ldap_clients:
            Logger.fatal("Nothing to do, ldap disabled and no clients passed with -p")

        if args.list:
            for c in args.list:
                if c not in ldap_clients:
                    target_clients.append(c)

        if ldap_clients:
            for c in ldap_clients:
                target_clients.append(c)

        # create counter for clients
        for client in target_clients:
            if client == "SERVER":
                Logger.error(f"Cannot create client {client}: Invalid Name")
            else:
                for i in range(0, args.count):
                    clients.append(f"{client}-{i}")

        return clients

    @staticmethod
    def write_config_files(actual_clients):
        n_actual_clients = len(actual_clients)
        for i, client in enumerate(actual_clients):
            print(f"Writing config files: {int((i / (n_actual_clients - 1)) * 100)}%", end="\r")
            client.write_client_config()
        print(f"\nWritten {n_actual_clients} config files")
