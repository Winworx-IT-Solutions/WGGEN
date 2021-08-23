import os
import tempfile
import sqlite3

from random import randrange

# Subnet database definitions:
# s[0] = ID
# s[1] = base_ip
# s[2] = last_ip
# s[3] = netmask
        
        
#===========================================================================#
# Subnet Class for WireGuard Interfaces and their Peers
#===========================================================================#
class Subnet:
    def __init__(self, subnet_id, base_ip, last_ip, netmask, desc=None):
        self.subnet_id = subnet_id
        self.base_ip = base_ip
        self.last_ip = last_ip
        self.netmask = netmask
        self.desc = desc
        
        
#===========================================================================#
# Subnet related database interactions
#===========================================================================#
def load_subnet_by_id(db, subnet_id):
    sql = f"SELECT * FROM subnet_directory WHERE id = {subnet_id}"
    cur = db.cursor()
    cur.execute(sql)
    subnet_info = cur.fetchall() 
    db.commit() 
    
    subnets = []
    for s in subnet_info:
        new_subnet = Subnet(s[0], s[1], s[2], s[3])
        subnets.append(new_subnet)
        
    return subnets[0]


def create_new_subnet(db, netmask, desc=None):
    need_base_ip = True
    base_ip = ""
    while need_base_ip:
        base_ip = f"10.{int((randrange(0, 254)))}"
    
        sql = f"SELECT * FROM subnet_directory WHERE base_ip = {base_ip}"
        cur = db.cursor()
        cur.execute(sql)
        data = cur.fetchall()
        db.commit()
        
        if len(data) == 0:
            need_base_ip = False
    
        
    last_ip = "0.0"
    s = Subnet("NOT_A_REAL_ID", base_ip, last_ip, netmask, str(desc)) # dont give the subnet any real id here since it will be handled by sqlite3
    sql = f"INSERT INTO subnet_directory (base_ip, last_ip, netmask, description) VALUES (?, ?, ?, ?);"
    params = (s.base_ip, s.last_ip, s.netmask, s.desc)
    cur = db.cursor()
    
    try:
        cur.execute(sql, params)
        db.commit()
    except sqlite3.Error as er:
        print('SQLite error: %s' % (' '.join(er.args)))
        return False
    return True

    
def load_all_subnets(db):
    sql = f"SELECT * FROM subnet_directory"
    cur = db.cursor()
    cur.execute(sql)
    subnet_info = cur.fetchall() 
    db.commit() 
    
    subnets = []
    for s in subnet_info:
        new_subnet = Subnet(s[0], s[1], s[2], s[3])
        subnets.append(new_subnet)
        
    return subnets
