import sqlite3

con = sqlite3.connect('wgsm.db')
cur = con.cursor()

def setup():
    sql = """

        CREATE TABLE interfaces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR,
            privatekey VARCHAR,
            publickey VARCHAR,
            vpn_subnet_ip VARCHAR
        );

    """

    cur.execute(sql)
    con.commit()

    sql = """

        CREATE TABLE peers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR,
            privatekey VARCHAR,
            publickey VARCHAR,
            presharedkey VARCHAR,
            vpn_subnet_ip VARCHAR,
            allowed_ips VARCHAR,
            interface_id INTEGER
        );

    """

    cur.execute(sql)
    con.commit()

def fill_interfaces():
    for i in range(1,5):
        sql = """
            INSERT INTO interfaces (
                name,
                privatekey,
                publickey,
                vpn_subnet_ip
            ) VALUES (
                "name{}",
                "XXXXXXXX",
                "YYYYYYYY",
                '10.{}.0.1/16'
            );
        """.format(i, i)
        
        cur.execute(sql)
        con.commit()

def fill_peers():
    for i in range(1,5):
        sql = """
            INSERT INTO peers (
                name,
                privatekey,
                publickey,
                presharedkey,
                vpn_subnet_ip,
                allowed_ips,
                interface_id
            ) VALUES (
                "name{}",
                "XXXXXXXX",
                "YYYYYYYY",
                "ZZZZZZZZ",
                '10.{}.0.1/16',
                '192.168.0.0/24',
                {}
            );
        """.format(i, i, i)
        
        cur.execute(sql)
        con.commit()
        
setup()
#fill_interfaces()
#fill_peers()
