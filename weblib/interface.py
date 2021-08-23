import os
import tempfile

import weblib.peer
import weblib.vpn_subnet


# Interface database definitions:
# i[0] = ID
# i[1] = name
# i[2] = privatekey
# i[3] = publickey
# i[4] = vpn_subnet_id
# i[5] = passthrough_interface
        
        
#===========================================================================#
# Interface Class for WireGuard Interfaces and their Peers
#===========================================================================#
class Interface:
    def __init__(self, interface_id, interface_name, privatekey, publickey, vpn_subnet, passthrough_interface, peers):
    
        self.interface_id = interface_id
        self.name = interface_name
        self.privatekey = privatekey 
        self.publickey = publickey
        self.passthrough_interface = passthrough_interface
        
        self.vpn_subnet = vpn_subnet
        self.peers = []
        
        
    def write_interface_config(self):
        if len(self.peers) != 0:
            return False
        pass

    
    def register_peer(self, peer):
        self.peers.append(peer)
        
        
    def _init_new_keys(self):
        with tempfile.TemporaryDirectory() as t:
            command = f"umask 077; wg genkey | tee {t}/privatekey | wg pubkey > {t}/publickey"
            os.system(command)
            
            with open(f"{t}/privatekey", 'r') as f:
                self.privatekey = f.read()
            with open(f"{t}/publickey", 'r') as f:
                self.publickey = f.read()
        

#===========================================================================#
# Interface related database interactions
#===========================================================================#
def load_all_interfaces_from_db(db):
    sql = f"SELECT * FROM interfaces"
    cur = db.cursor()
    cur.execute(sql)
    interface_info = cur.fetchall() 
    db.commit() 
    
    interfaces = []
    for i in interface_info:
        interface_id   = i[0]
        interface_name = i[1]
        privatekey     = i[2]
        publickey      = i[3]
        vpn_subnet_id  = i[4]
        passthrough_interface = i[5]
        
        # let all peers know which interface they belong to, important for config generation
        peers = weblib.peer.load_peers_by_interface_id(db, interface, interface_id)
        
        # fetch the required VPN Subnet
        vpn_subnet = weblib.vpn_subnet.load_subnet_by_id(db, vpn_subnet_id)
    
        new_interface = Interface(interface_id, interface_name, privatekey, publickey, vpn_subnet, passthrough_interface, peers)
        interfaces.append(new_interface)
           
    return interfaces
    
