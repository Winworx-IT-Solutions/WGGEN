-- Create Table for WireGuard Peers
CREATE TABLE peers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          VARCHAR NOT NULL UNIQUE,
    privatekey    VARCHAR NOT NULL UNIQUE,
    publickey     VARCHAR NOT NULL UNIQUE,
    presharedkey  VARCHAR NOT NULL UNIQUE,            
    vpn_subnet_ip VARCHAR NOT NULL UNIQUE,
    allowed_ips   VARCHAR NOT NULL,
    interface_id  INTEGER NOT NULL
);

-- Create Table for WireGuard Interfaces
CREATE TABLE interfaces (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  VARCHAR NOT NULL UNIQUE,
    privatekey            VARCHAR NOT NULL UNIQUE,
    publickey             VARCHAR NOT NULL UNIQUE,
    vpn_subnet_id         INTEGER NOT NULL UNIQUE,
    passthrough_interface VARCHAR NOT NULL
);   

-- Create Table for VPN Subnets
CREATE TABLE subnet_directory (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    base_ip     VARCHAR NOT NULL UNIQUE,
    last_ip     VARCHAR NOT NULL,
    netmask     INTEGER NOT NULL,
    description TEXT
);
