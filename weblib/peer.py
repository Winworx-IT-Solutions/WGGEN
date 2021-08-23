import os
import tempfile

# Peer database definitions:
# p[0] = ID
# p[1] = name
# p[2] = privatekey
# p[3] = publickey
# p[4] = preshared_key
# p[5] = vpn_subnet_ip
# p[6] = allowed_ips
# p[7] = interface_id
        
        
#===========================================================================#
# Peer Class for WireGuard Peers and their Interfaces
#===========================================================================#
class Peer:
    def __init__(self, peer_id, name, privatekey, publickey, preshared_key, vpn_subnet_ip, allowed_ips, interface_id, interface):
    
        self.peer_id = peer_id
        self.name = name
        self.privatekey = privatekey 
        self.publickey = publickey
        self.preshared_key = preshared_key
        self.vpn_subnet_ip = vpn_subnet_ip
        self.allowed_ips = allowed_ips
        self.interface_id = interface_id
        self.interface = interface
        
        
    def write_peer_config(self):
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
def load_peers_by_interface_id(db, interface, interface_id):
    sql = f"SELECT * FROM peers WHERE interface_id = {interface_id}"
    cur = db.cursor()
    cur.execute(sql)
    peer_info = cur.fetchall() 
    db.commit() 
    
    peers = []
    for p in peer_info:
        new_peer = Peer(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], interface)
        peers.append(new_peer)

