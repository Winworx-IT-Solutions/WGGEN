import os
import re
import argparse
import configparser
from dataclasses import dataclass

PATH = "/etc/wireguard"


@dataclass
class File:
    filename: str
    path: str

    def abs_path(self):
        return f"{self.path}/{self.filename}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--publickey', type=str, help='Publickey to be searched', required=True)
    args = parser.parse_args()
    args.publickey = args.publickey.strip()

    client_files = []
    client_path = PATH + '/clients'
    wanted_psk = ""
    found = False
    for p in os.walk(client_path):
        for f in p[2]:
            if f.endswith(".conf"):
                client_files.append(File(filename=f, path=p[0]))

    sfile = read_server_file()
    for i, l in enumerate(sfile):
        if re.search(args.publickey, l):
            wanted_psk = sfile[i+1].split("= ")[1].strip()

    for i, f in enumerate(client_files):
        print(f"checking files {int((i/(len(client_files)-1))*100)}% of {len(client_files)} total clients", end="\r")
        c = configparser.ConfigParser()
        c.read(f.abs_path())
        psk = c.get('Peer', 'PresharedKey')
        if psk == wanted_psk:
            found = True
            print(f"File for publickey {args.publickey} is {f.filename}")

    if not found:
        print(f"The publickey {args.publickey} seems to not exist on this wireguard server")
    else:
        print(f"The publickey {args.publickey} was found!")


def read_server_file():
    server_file = PATH + "/wg0.conf"
    with open(server_file, 'r') as f:
        content = f.readlines()
    return content


if __name__ == "__main__":
    main()
