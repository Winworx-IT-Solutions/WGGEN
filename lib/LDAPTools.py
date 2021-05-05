from ldap3 import Server, Connection, ALL
from lib.Utils import Logger as Logger


class LDAPTools:
    def __init__(self, args):
        self.server = Server(args.ldap_server, get_info=ALL)
        self.conn = Connection(self.server, args.bind_dn, args.bind_pw, auto_bind=True)
        self.ldap_filter = args.filter
        self.base_dn = args.base_dn
        self.user_attr = args.user_attr

        Logger.info("Trying to connect to ldap server {} with {} and password: {}".format(args.ldap_server,
                                                                                          args.bind_dn, args.bind_pw))

    def get_ldap_clients(self):
        self.conn.search(self.base_dn, self.ldap_filter, attributes=['*'])
        name_list = []
        for entry in self.conn.entries:
            name_list.append(entry[self.user_attr])

        Logger.info("Fetched {} clients from ldap".format(len(name_list)))
        return name_list

