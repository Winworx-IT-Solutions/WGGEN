import sqlite3
import os
import tempfile







class Helper:

    #============================#
    # make the login requirement 
    # more readable in the main 
    # application
    #============================#
    @staticmethod
    def user_logged_in(session):
        if 'username' in session:
            return True
        return False
    
    #============================#
    # List all Configured WG
    # Interfaces
    #============================#
    @staticmethod
    def generate_new_wg_interface(db, name):
    
        # generate keys first
        with tempfile.TemporaryDirectory() as t:
            command = f"umask 077; wg genkey | tee {t}/privatekey | wg pubkey > {t}/publickey"
            os.system(command)
            
            with open(f"{t}/privatekey", 'r') as f:
                privatekey = f.read()
            with open(f"{t}/publickey", 'r') as f:
                publickey = f.read()
        
        sql = f"""
            INSERT INTO interfaces (
                name,
                privatekey,
                publickey,
                vpn_subnet_ip
            ) VALUES (
                "{name}",
                "{privatekey}",
                "{publickey}",
                "10.x.x.x/16"
            );
        """
        cur = db.cursor()
        success = True
        try:
            cur.execute(sql)
        except:
            success = False
        db.commit()
        
        return(success)
    
    
    #============================#
    # List all Configured WG
    # Interfaces
    #============================#
    @staticmethod
    def list_wg_interfaces(db): 
        sql = "SELECT * FROM interfaces"
        cur = db.cursor()
        res = cur.execute(sql)
        db.commit()
        
        return(res)
        
        
    #============================#
    # Get one WG Interface detail
    #============================#
    @staticmethod
    def get_interface_detail(db, interface_id): 
        sql = f"SELECT * FROM interfaces WHERE id = {interface_id}"
        cur = db.cursor()
        cur.execute(sql)
        interface_info = cur.fetchall() 
        db.commit()
        
        sql = f"SELECT * FROM peers WHERE interface_id = {interface_id}"
        cur = db.cursor()
        cur.execute(sql)
        peer_info = cur.fetchall()
        db.commit()
        
        return(interface_info, peer_info)      
        
        
    #============================#
    # List all Configured WG
    # Interfaces
    #============================#
    @staticmethod
    def list_wg_peers(db):
        sql = "SELECT * FROM peers"
        cur = db.cursor()
        res = cur.execute(sql)
        db.commit()

        return(res)
